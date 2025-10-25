#!/usr/bin/env python3
"""
Example usage of the Security Static Analysis MCP Service

This script demonstrates how to use the service programmatically
for testing and development purposes.
"""

import asyncio
from src.models import AnalysisRequest
from src.services import LanguageDetector, LLMService
from src.analyzers import CSharpSecurityAnalyzer, ReactTypeScriptAnalyzer


async def example_csharp_analysis():
    """Example: Analyze C# code with SQL injection vulnerability"""
    print("=" * 60)
    print("Example 1: C# SQL Injection Analysis")
    print("=" * 60)
    print()

    # Vulnerable C# code
    code = """
    public class UserController
    {
        public User GetUser(string userId)
        {
            // VULNERABLE: SQL Injection
            var sql = "SELECT * FROM Users WHERE Id = '" + userId + "'";
            return database.ExecuteQuery(sql);
        }

        public void DeleteUser(string userId)
        {
            // VULNERABLE: Hardcoded connection string
            var connectionString = "Server=localhost;Database=mydb;User=admin;Password=Secret123!";
            using (var connection = new SqlConnection(connectionString))
            {
                var command = new SqlCommand("DELETE FROM Users WHERE Id = " + userId, connection);
                command.ExecuteNonQuery();
            }
        }
    }
    """

    # Create services
    llm_service = LLMService()
    analyzer = CSharpSecurityAnalyzer(llm_service)

    print("Analyzing C# code...")
    print()

    try:
        # Perform analysis
        result = await analyzer.analyze(code, "UserController.cs")

        # Display results
        print(f"Language: {result.language.value}")
        print(f"Summary: {result.summary}")
        print()

        if result.issues:
            print("Security Issues Found:")
            print()
            for issue in result.issues:
                print(f"  [{issue.severity.value}] {issue.title}")
                print(f"  ID: {issue.id}")
                print(f"  Description: {issue.description}")
                if issue.line_number:
                    print(f"  Location: Line {issue.line_number}")
                if issue.remediation:
                    print(f"  Remediation: {issue.remediation}")
                print()
        else:
            print("No security issues detected.")

        print("Metadata:", result.analysis_metadata)

    except Exception as e:
        print(f"Analysis failed: {e}")

    print()


async def example_react_analysis():
    """Example: Analyze React TypeScript code with XSS vulnerability"""
    print("=" * 60)
    print("Example 2: React TypeScript XSS Analysis")
    print("=" * 60)
    print()

    # Vulnerable React code
    code = """
    import React, { useState } from 'react';

    export const UserProfile: React.FC = () => {
        const [userBio, setUserBio] = useState('');

        // VULNERABLE: XSS via dangerouslySetInnerHTML
        return (
            <div>
                <h1>User Profile</h1>
                <div dangerouslySetInnerHTML={{ __html: userBio }} />

                {/* VULNERABLE: Hardcoded API key */}
                <button onClick={() => {
                    fetch('https://api.example.com/user', {
                        headers: {
                            'Authorization': 'Bearer sk_live_1234567890abcdef'
                        }
                    });
                }}>
                    Load Data
                </button>
            </div>
        );
    };
    """

    # Create services
    llm_service = LLMService()
    analyzer = ReactTypeScriptAnalyzer(llm_service)

    print("Analyzing React TypeScript code...")
    print()

    try:
        # Perform analysis
        result = await analyzer.analyze(code, "UserProfile.tsx")

        # Display results
        print(f"Language: {result.language.value}")
        print(f"Summary: {result.summary}")
        print()

        if result.issues:
            print("Security Issues Found:")
            print()
            for issue in result.issues:
                print(f"  [{issue.severity.value}] {issue.title}")
                print(f"  ID: {issue.id}")
                print(f"  Description: {issue.description}")
                if issue.remediation:
                    print(f"  Remediation: {issue.remediation}")
                print()

        print("Metadata:", result.analysis_metadata)

    except Exception as e:
        print(f"Analysis failed: {e}")

    print()


async def example_language_detection():
    """Example: Language detection"""
    print("=" * 60)
    print("Example 3: Language Detection")
    print("=" * 60)
    print()

    detector = LanguageDetector()

    test_cases = [
        ("UserController.cs", "namespace MyApp { public class User { } }"),
        ("App.tsx", "import React from 'react'; export const App = () => <div>Hello</div>;"),
        ("component.jsx", "export default function Component() { return <div>Test</div>; }"),
    ]

    for file_path, code in test_cases:
        detected = detector.detect_language(code, file_path)
        print(f"File: {file_path}")
        print(f"  Detected language: {detected.value}")
        print(f"  Supported extensions: {detector.get_supported_extensions(detected)}")
        print()


async def example_health_check():
    """Example: Health check"""
    print("=" * 60)
    print("Example 4: Health Check")
    print("=" * 60)
    print()

    llm_service = LLMService()

    print("Checking LLM service health...")
    health = await llm_service.health_check()

    print(f"Status: {health['status']}")
    print(f"Available: {health['available']}")
    if 'error' in health:
        print(f"Error: {health['error']}")
    print(f"Base URL: {health['base_url']}")
    print()


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  Security Static Analysis MCP Service - Examples        ║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Check health first
    await example_health_check()

    # Language detection
    await example_language_detection()

    # Note: The following examples require LMStudio to be running
    # Uncomment to run actual analysis

    # await example_csharp_analysis()
    # await example_react_analysis()

    print("=" * 60)
    print("Examples completed!")
    print()
    print("Note: Analysis examples are commented out by default.")
    print("To run them, ensure LMStudio is running with qwen/qwen3-coder-30b")
    print("and uncomment the analysis function calls in this script.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
