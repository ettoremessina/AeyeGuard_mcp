import re
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models import SecurityIssue, AnalysisResult, LanguageType, SeverityLevel
from src.services import LLMService


class BaseSecurityAnalyzer(ABC):
    """Base class for language-specific security analyzers"""

    def __init__(self, llm_service: LLMService):
        """
        Initialize the analyzer with an LLM service.

        Args:
            llm_service: LLM service instance for code analysis
        """
        self.llm_service = llm_service

    @abstractmethod
    def get_language_type(self) -> LanguageType:
        """Return the language type this analyzer handles"""
        pass

    @abstractmethod
    def get_security_rules_prompt(self) -> str:
        """Return the prompt containing security rules for this language"""
        pass

    def preprocess_code(self, code: str) -> str:
        """
        Preprocess code before analysis.
        Default implementation removes comments while preserving line structure.

        Args:
            code: Source code to preprocess

        Returns:
            Preprocessed code
        """
        # Remove single-line comments but keep line breaks
        code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)

        # Remove multi-line comments but preserve line count
        def replace_multiline_comment(match):
            return "\n" * match.group(0).count("\n")

        code = re.sub(r"/\*.*?\*/", replace_multiline_comment, code, flags=re.DOTALL)

        return code

    async def analyze(self, code: str, file_path: str = None) -> AnalysisResult:
        """
        Perform security analysis on the code.

        Args:
            code: Source code to analyze
            file_path: Optional file path for context

        Returns:
            AnalysisResult containing detected issues
        """
        try:
            # Preprocess code
            preprocessed_code = self.preprocess_code(code)

            # Get security rules prompt
            prompt = self.get_security_rules_prompt()

            # Analyze with LLM
            llm_response = await self.llm_service.analyze_code(preprocessed_code, prompt)

            # Parse response
            issues_data = self.llm_service.parse_llm_response(llm_response)

            # Convert to SecurityIssue objects
            issues = self._create_security_issues(issues_data, file_path)

            # Generate summary
            summary = self._generate_summary(issues)

            # Create metadata
            metadata = {
                "total_issues": len(issues),
                "critical_count": sum(1 for i in issues if i.severity == SeverityLevel.CRITICAL),
                "high_count": sum(1 for i in issues if i.severity == SeverityLevel.HIGH),
                "medium_count": sum(1 for i in issues if i.severity == SeverityLevel.MEDIUM),
                "low_count": sum(1 for i in issues if i.severity == SeverityLevel.LOW),
                "analyzer": self.__class__.__name__,
                "status": "COMPLETED",
                "completion_message": "✅ Analysis finished successfully",
            }

            return AnalysisResult(
                language=self.get_language_type(),
                issues=issues,
                summary=summary,
                analysis_metadata=metadata,
            )

        except Exception as e:
            # Return error result with metadata
            return AnalysisResult(
                language=self.get_language_type(),
                issues=[],
                summary=f"Analysis failed: {str(e)}",
                analysis_metadata={"error": str(e), "analyzer": self.__class__.__name__},
            )

    def _create_security_issues(
        self, issues_data: List[Dict[str, Any]], file_path: str = None
    ) -> List[SecurityIssue]:
        """
        Convert raw issue data from LLM to SecurityIssue objects.

        Args:
            issues_data: List of issue dictionaries from LLM
            file_path: Optional file path to attach to issues

        Returns:
            List of SecurityIssue objects
        """
        issues = []
        for idx, data in enumerate(issues_data):
            try:
                # Parse severity
                severity_str = data.get("severity", "MEDIUM").upper()
                try:
                    severity = SeverityLevel(severity_str)
                except ValueError:
                    severity = SeverityLevel.MEDIUM

                issue = SecurityIssue(
                    id=data.get("id", f"SEC-{uuid.uuid4().hex[:8]}"),
                    title=data.get("title", "Security Issue"),
                    description=data.get("description", "No description provided"),
                    severity=severity,
                    line_number=data.get("line_number"),
                    column_number=data.get("column_number"),
                    file_path=file_path or data.get("file_path"),
                    code_snippet=data.get("code_snippet"),
                    remediation=data.get("remediation"),
                    references=data.get("references", []),
                )
                issues.append(issue)
            except Exception as e:
                # Skip malformed issues
                continue

        return issues

    def _generate_summary(self, issues: List[SecurityIssue]) -> str:
        """
        Generate a summary of the analysis results.

        Args:
            issues: List of detected security issues

        Returns:
            Summary string with completion message
        """
        # Generate issue summary
        if not issues:
            summary = "No security issues detected."
        else:
            critical = sum(1 for i in issues if i.severity == SeverityLevel.CRITICAL)
            high = sum(1 for i in issues if i.severity == SeverityLevel.HIGH)
            medium = sum(1 for i in issues if i.severity == SeverityLevel.MEDIUM)
            low = sum(1 for i in issues if i.severity == SeverityLevel.LOW)

            parts = []
            if critical:
                parts.append(f"{critical} critical")
            if high:
                parts.append(f"{high} high")
            if medium:
                parts.append(f"{medium} medium")
            if low:
                parts.append(f"{low} low")

            severity_text = ", ".join(parts) if parts else "0"
            summary = f"Found {len(issues)} security issue(s): {severity_text} severity."

        # Add highlighted completion message
        completion_message = "\n\n" + "=" * 70 + "\n"
        completion_message += "🎯 ANALYSIS COMPLETED SUCCESSFULLY 🎯\n"
        completion_message += "=" * 70 + "\n"
        completion_message += f"Language: {self.get_language_type().value.upper()}\n"
        completion_message += f"Analyzer: {self.__class__.__name__}\n"
        completion_message += "Status: ✅ FINISHED\n"
        completion_message += "=" * 70

        return summary + completion_message
