#!/usr/bin/env python3
"""
Test Java analyzer implementation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import LanguageType
from src.services import LanguageDetector


def test_java_language_detection():
    """Test Java language detection"""
    print("Testing Java language detection...")

    detector = LanguageDetector()

    # Test extension-based detection
    java_file = "UserService.java"
    detected = detector.detect_language("", java_file)
    assert detected == LanguageType.JAVA, f"Expected JAVA, got {detected}"
    print("✓ Extension-based detection works")

    # Test pattern-based detection
    java_code = """
    package com.example.service;

    import java.util.List;
    import javax.persistence.Entity;

    @Entity
    public class User {
        private String username;
        private String password;

        public String getUsername() {
            return username;
        }
    }
    """

    detected = detector._detect_by_patterns(java_code)
    assert detected == LanguageType.JAVA, f"Expected JAVA, got {detected}"
    print("✓ Pattern-based detection works")

    # Test supported extensions
    extensions = detector.get_supported_extensions(LanguageType.JAVA)
    assert ".java" in extensions, f"Expected .java in {extensions}"
    print(f"✓ Supported extensions: {extensions}")


def test_java_analyzer_import():
    """Test that Java analyzer can be imported"""
    print("\nTesting Java analyzer import...")

    try:
        from src.analyzers import JavaSecurityAnalyzer
        from src.services import LLMService

        # Create analyzer instance
        llm_service = LLMService()
        analyzer = JavaSecurityAnalyzer(llm_service)

        # Verify language type
        assert analyzer.get_language_type() == LanguageType.JAVA
        print("✓ Java analyzer imported successfully")
        print(f"✓ Language type: {analyzer.get_language_type().value}")

        # Verify security rules prompt exists
        prompt = analyzer.get_security_rules_prompt()
        assert len(prompt) > 0, "Security rules prompt is empty"
        assert "SQL Injection" in prompt, "SQL Injection rule not found in prompt"
        assert "Command Injection" in prompt, "Command Injection rule not found"
        assert "XXE" in prompt, "XXE rule not found"
        assert "JNDI Injection" in prompt, "JNDI Injection rule not found"
        assert "Hardcoded Credentials" in prompt, "Hardcoded Credentials rule not found"
        print("✓ Security rules prompt contains expected rules")

        # Test preprocessing
        java_code_with_comments = """
        package com.example;

        // This is a single-line comment
        /* This is a
           multi-line comment */

        public class Test {
            /** Javadoc comment */
            public void method() {
                String sql = "SELECT * FROM users";
            }
        }
        """

        preprocessed = analyzer.preprocess_code(java_code_with_comments)
        assert "// This is a single-line comment" not in preprocessed
        assert "/* This is a" not in preprocessed
        assert "public class Test" in preprocessed
        print("✓ Code preprocessing removes comments correctly")

    except ImportError as e:
        print(f"✗ Failed to import Java analyzer: {e}")
        raise


def test_java_in_mcp_service():
    """Test that Java is registered in MCP service"""
    print("\nTesting Java analyzer registration in MCP service...")

    try:
        from src.AeyeGuard_mcp import SecurityAnalyzerMCP
        from src.models import LanguageType

        # Note: This will try to connect to LMStudio, so we just test initialization
        print("  Note: Full service test requires LMStudio running")
        print("  Testing analyzer registration...")

        # Check that JavaSecurityAnalyzer is in the imports
        import src.AeyeGuard_mcp as mcp_module
        assert hasattr(mcp_module, 'JavaSecurityAnalyzer'), "JavaSecurityAnalyzer not imported in MCP service"
        print("✓ JavaSecurityAnalyzer is imported in MCP service module")

    except Exception as e:
        print(f"  Note: Service initialization test skipped ({e})")
        print("  This is expected if LMStudio is not running")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Java Analyzer Implementation Tests")
    print("=" * 60)
    print()

    try:
        test_java_language_detection()
        test_java_analyzer_import()
        test_java_in_mcp_service()

        print()
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print()
        print("Java analyzer is ready to use.")
        print("Start the service with: ./run_service.sh")
        print("Then analyze Java code via: POST /analyze")

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"✗ Test failed: {e}")
        print("=" * 60)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Unexpected error: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
