from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Security issue severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LanguageType(str, Enum):
    """Supported programming languages"""
    CSHARP = "csharp"
    REACT_TYPESCRIPT = "react_typescript"
    REACT_JAVASCRIPT = "react_javascript"
    JAVA = "java"
    UNKNOWN = "unknown"


class SecurityIssue(BaseModel):
    """Represents an individual security vulnerability"""
    id: str = Field(..., description="Unique identifier for the issue")
    title: str = Field(..., description="Brief title of the security issue")
    description: str = Field(..., description="Detailed description of the issue")
    severity: SeverityLevel = Field(..., description="Severity level of the issue")
    line_number: Optional[int] = Field(None, description="Line number where issue occurs")
    column_number: Optional[int] = Field(None, description="Column number where issue occurs")
    file_path: Optional[str] = Field(None, description="File path of the analyzed code")
    code_snippet: Optional[str] = Field(None, description="Code snippet showing the issue")
    remediation: Optional[str] = Field(None, description="Suggested fix or remediation steps")
    references: Optional[List[str]] = Field(default_factory=list, description="External references (CVE, OWASP, etc.)")

    class Config:
        use_enum_values = True


class AnalysisRequest(BaseModel):
    """Input model for security analysis"""
    code: str = Field(..., description="Source code to analyze")
    file_path: Optional[str] = Field(None, description="File path for context and language detection")
    language: Optional[str] = Field("auto", description="Programming language (auto, csharp, react_typescript, react_javascript, java)")

    class Config:
        use_enum_values = True


class AnalysisResult(BaseModel):
    """Output model containing analysis results"""
    language: LanguageType = Field(..., description="Detected or specified programming language")
    issues: List[SecurityIssue] = Field(default_factory=list, description="List of detected security issues")
    summary: str = Field(..., description="Summary of the analysis")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata")

    class Config:
        use_enum_values = True
