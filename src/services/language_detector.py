import re
from typing import Optional
from src.models import LanguageType


class LanguageDetector:
    """Service for detecting programming languages from code and file paths"""

    # File extension mappings
    EXTENSION_MAP = {
        ".cs": LanguageType.CSHARP,
        ".tsx": LanguageType.REACT_TYPESCRIPT,
        ".ts": LanguageType.REACT_TYPESCRIPT,
        ".jsx": LanguageType.REACT_JAVASCRIPT,
        ".js": LanguageType.REACT_JAVASCRIPT,
        ".java": LanguageType.JAVA,
    }

    # Language pattern signatures for content-based detection
    LANGUAGE_PATTERNS = {
        LanguageType.CSHARP: [
            r"\busing\s+System\b",
            r"\bnamespace\s+\w+",
            r"\bpublic\s+class\s+\w+",
            r"\bprivate\s+\w+\s+\w+\s*\{",
            r"\[assembly:\s*\w+\]",
        ],
        LanguageType.REACT_TYPESCRIPT: [
            r"\bimport\s+.*\s+from\s+['\"]react['\"]",
            r"\bexport\s+.*React\.FC",
            r"\binterface\s+\w+Props",
            r":\s*React\.ReactNode",
            r"<.*>\s*\(.*\)\s*=>\s*\{",
        ],
        LanguageType.REACT_JAVASCRIPT: [
            r"\bimport\s+.*\s+from\s+['\"]react['\"]",
            r"\bexport\s+default\s+function",
            r"\bReact\.createElement",
            r"<\w+[^>]*>.*<\/\w+>",
        ],
        LanguageType.JAVA: [
            r"\bpackage\s+[a-z][a-z0-9_.]*\s*;",
            r"\bimport\s+(java|javax|org)\.",
            r"\bpublic\s+(class|interface|enum)\s+\w+",
            r"@(Override|Autowired|Entity|Controller|Service|Repository)",
            r"\b(public|private|protected)\s+(static\s+)?(void|int|String|boolean)\s+\w+\s*\(",
        ],
    }

    def detect_language(self, code: str, file_path: Optional[str] = None) -> LanguageType:
        """
        Detect the programming language from code content or file path.

        Args:
            code: Source code to analyze
            file_path: Optional file path for extension-based detection

        Returns:
            LanguageType enum value
        """
        # Try file extension detection first (primary method)
        if file_path:
            lang = self._detect_by_extension(file_path)
            if lang != LanguageType.UNKNOWN:
                return lang

        # Fall back to pattern matching
        return self._detect_by_patterns(code)

    def _detect_by_extension(self, file_path: str) -> LanguageType:
        """Detect language based on file extension"""
        for ext, lang in self.EXTENSION_MAP.items():
            if file_path.lower().endswith(ext):
                return lang
        return LanguageType.UNKNOWN

    def _detect_by_patterns(self, code: str) -> LanguageType:
        """Detect language based on code patterns"""
        scores = {lang: 0 for lang in LanguageType if lang != LanguageType.UNKNOWN}

        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE):
                    scores[lang] += 1

        # Return language with highest score
        if scores:
            max_lang = max(scores.items(), key=lambda x: x[1])
            if max_lang[1] > 0:
                return max_lang[0]

        return LanguageType.UNKNOWN

    def get_supported_extensions(self, language: LanguageType) -> list[str]:
        """Get file extensions for a specific language"""
        return [ext for ext, lang in self.EXTENSION_MAP.items() if lang == language]
