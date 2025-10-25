#!/usr/bin/env python3
"""
Installation verification script for AeyeGuard MCP Service
"""

import sys
import importlib
from typing import Tuple


def test_import(module_name: str, description: str) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return True, f"✓ {description}"
    except ImportError as e:
        return False, f"✗ {description}: {str(e)}"


def main():
    """Run installation verification tests"""
    print("=" * 60)
    print("AeyeGuard MCP - Installation Verification")
    print("=" * 60)
    print()

    all_passed = True
    tests = [
        # Core dependencies
        ("pydantic", "Pydantic (data validation)"),
        ("dotenv", "Python-dotenv (environment variables)"),
        ("httpx", "HTTPX (HTTP client)"),
        ("langchain", "LangChain (LLM framework)"),
        ("langchain_community", "LangChain Community"),
        ("mcp", "Model Context Protocol"),

        # Project modules
        ("src.models", "Data models"),
        ("src.models.data_models", "Data model definitions"),
        ("src.services", "Services module"),
        ("src.services.language_detector", "Language detector"),
        ("src.services.llm_service", "LLM service"),
        ("src.analyzers", "Analyzers module"),
        ("src.analyzers.base_analyzer", "Base analyzer"),
        ("src.analyzers.csharp_analyzer", "C# analyzer"),
        ("src.analyzers.react_typescript_analyzer", "React TypeScript analyzer"),
        ("src.analyzers.react_javascript_analyzer", "React JavaScript analyzer"),
        ("src.AeyeGuard_mcp", "MCP service"),
    ]

    print("Testing imports...")
    print()

    for module_name, description in tests:
        passed, message = test_import(module_name, description)
        print(message)
        if not passed:
            all_passed = False

    print()
    print("=" * 60)

    if all_passed:
        print("✓ All tests passed! Installation is complete.")
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env and configure settings")
        print("2. Ensure LMStudio is running with qwen/qwen3-coder-30b model")
        print("3. Run: python -m src.AeyeGuard_mcp")
        return 0
    else:
        print("✗ Some tests failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
