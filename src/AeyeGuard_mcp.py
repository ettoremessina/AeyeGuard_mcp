#!/usr/bin/env python3
"""
AeyeGuard MCP Service

An MCP service that performs automated security analysis on source code
using LMStudio with the qwen/qwen3-coder-30b language model.

This service exposes HTTP endpoints for integration with IDEs.
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from src.models import AnalysisRequest, LanguageType
from src.services import LanguageDetector, LLMService
from src.analyzers import (
    CSharpSecurityAnalyzer,
    ReactTypeScriptAnalyzer,
    ReactJavaScriptAnalyzer,
    JavaSecurityAnalyzer,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    service: str
    version: str
    status: str
    llm_service: dict
    supported_languages: list[str]


class LanguageInfo(BaseModel):
    """Language information model"""
    language: str
    description: str
    extensions: list[str]
    analyzer_available: bool


class AnalysisResponse(BaseModel):
    """Analysis response model"""
    language: str
    summary: str
    issues: list[dict]
    metadata: dict
    completion_status: str = "✅ ANALYSIS FINISHED"


class SecurityAnalyzerMCP:
    """MCP Service for security analysis"""

    def __init__(self):
        """Initialize the MCP service"""
        self.server_name = os.getenv("MCP_SERVER_NAME", "aeyeguard_mcp")
        self.server_version = os.getenv("MCP_SERVER_VERSION", "1.0.0")
        self.host = os.getenv("MCP_HOST", "0.0.0.0")
        self.port = int(os.getenv("MCP_PORT", "8000"))

        logger.info(f"Initializing {self.server_name} v{self.server_version}")

        # Initialize services
        self.llm_service = LLMService()
        self.language_detector = LanguageDetector()

        # Initialize analyzers
        self.analyzers = {
            LanguageType.CSHARP: CSharpSecurityAnalyzer(self.llm_service),
            LanguageType.REACT_TYPESCRIPT: ReactTypeScriptAnalyzer(self.llm_service),
            LanguageType.REACT_JAVASCRIPT: ReactJavaScriptAnalyzer(self.llm_service),
            LanguageType.JAVA: JavaSecurityAnalyzer(self.llm_service),
        }

        logger.info(f"Loaded {len(self.analyzers)} analyzers")

    async def analyze_security(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Perform security analysis on code.

        Args:
            request: AnalysisRequest containing code, file_path, and language

        Returns:
            AnalysisResponse with analysis results
        """
        try:
            # Detect language
            if request.language == "auto" or not request.language:
                detected_lang = self.language_detector.detect_language(
                    request.code, request.file_path
                )
            else:
                try:
                    detected_lang = LanguageType(request.language)
                except ValueError:
                    detected_lang = LanguageType.UNKNOWN

            # Check if language is supported
            if detected_lang == LanguageType.UNKNOWN:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to detect language or unsupported language type."
                )

            if detected_lang not in self.analyzers:
                raise HTTPException(
                    status_code=400,
                    detail=f"No analyzer available for {detected_lang.value}"
                )

            # Get appropriate analyzer
            analyzer = self.analyzers[detected_lang]

            logger.info(f"Analyzing code with {detected_lang.value} analyzer")

            # Perform analysis
            result = await analyzer.analyze(request.code, request.file_path)

            # Log completion
            logger.info(f"✅ Analysis completed: {result.analysis_metadata.get('total_issues', 0)} issues found")

            # Convert to response format
            issues_list = [
                {
                    "id": issue.id,
                    "title": issue.title,
                    "description": issue.description,
                    "severity": issue.severity if isinstance(issue.severity, str) else issue.severity.value,
                    "line_number": issue.line_number,
                    "column_number": issue.column_number,
                    "file_path": issue.file_path,
                    "code_snippet": issue.code_snippet,
                    "remediation": issue.remediation,
                    "references": issue.references,
                }
                for issue in result.issues
            ]

            return AnalysisResponse(
                language=result.language if isinstance(result.language, str) else result.language.value,
                summary=result.summary,
                issues=issues_list,
                metadata=result.analysis_metadata,
                completion_status="✅ ANALYSIS FINISHED SUCCESSFULLY"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    async def health_check(self) -> HealthCheckResponse:
        """
        Check service health.

        Returns:
            HealthCheckResponse with health status
        """
        try:
            # Check LLM service
            llm_health = await self.llm_service.health_check()

            status = "healthy" if llm_health["available"] else "degraded"

            return HealthCheckResponse(
                service=self.server_name,
                version=self.server_version,
                status=status,
                llm_service=llm_health,
                supported_languages=[
                    lang.value for lang in LanguageType if lang != LanguageType.UNKNOWN
                ],
            )

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail={
                    "service": self.server_name,
                    "version": self.server_version,
                    "status": "unhealthy",
                    "error": str(e),
                }
            )

    async def list_supported_languages(self) -> list[LanguageInfo]:
        """
        List supported languages.

        Returns:
            List of LanguageInfo objects
        """
        languages = []

        for lang_type in LanguageType:
            if lang_type == LanguageType.UNKNOWN:
                continue

            extensions = self.language_detector.get_supported_extensions(lang_type)

            languages.append(
                LanguageInfo(
                    language=lang_type.value,
                    description=f"{lang_type.value.replace('_', ' ').title()} Security Analysis",
                    extensions=extensions,
                    analyzer_available=lang_type in self.analyzers,
                )
            )

        return languages


# Global service instance
service_instance: Optional[SecurityAnalyzerMCP] = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager"""
    global service_instance

    logger.info("Starting Security Analyzer MCP Service...")
    service_instance = SecurityAnalyzerMCP()

    # Perform initial health check
    try:
        health = await service_instance.health_check()
        logger.info(f"Service status: {health.status}")
        logger.info(f"LLM service available: {health.llm_service['available']}")
    except Exception as e:
        logger.warning(f"Initial health check failed: {e}")

    yield

    logger.info("Shutting down Security Analyzer MCP Service...")
    service_instance = None


# Create FastAPI application
app = FastAPI(
    title="Security Static Analysis MCP Service",
    description="Automated security analysis on source code using LLM",
    version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Security Static Analysis MCP Service",
        "version": os.getenv("MCP_SERVER_VERSION", "1.0.0"),
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "languages": "/languages",
        }
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health():
    """Health check endpoint"""
    if service_instance is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return await service_instance.health_check()


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Analyze code for security vulnerabilities.

    Parameters:
    - code: Source code to analyze (required)
    - file_path: Optional file path for context and language detection
    - language: Programming language (auto, csharp, react_typescript, react_javascript)
    """
    if service_instance is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    logger.info(f"Received analysis request for {request.language or 'auto-detect'}")
    return await service_instance.analyze_security(request)


@app.get("/languages", response_model=list[LanguageInfo])
async def languages():
    """List all supported programming languages"""
    if service_instance is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return await service_instance.list_supported_languages()


@app.get("/mcp/tools")
async def mcp_tools():
    """
    MCP-compatible tools endpoint.
    Returns the list of available tools in MCP format.
    """
    return {
        "tools": [
            {
                "name": "analyze_security",
                "description": "Performs comprehensive security analysis on source code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code to analyze",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Optional file path for context and language detection",
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto, csharp, react_typescript, react_javascript, java)",
                            "enum": ["auto", "csharp", "react_typescript", "react_javascript", "java"],
                            "default": "auto",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "health_check",
                "description": "Verifies service health and dependency availability",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "list_supported_languages",
                "description": "Lists all supported programming languages and their metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]
    }


def main():
    """Main entry point"""
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
