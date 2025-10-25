#!/usr/bin/env python3
"""
Test script for the Security Analyzer HTTP API

This script tests the HTTP endpoints without requiring LMStudio.
"""

import httpx
import asyncio
import sys


async def test_endpoints():
    """Test all HTTP endpoints"""
    base_url = "http://localhost:8000"

    print("=" * 60)
    print("Security Analyzer MCP API - Endpoint Tests")
    print("=" * 60)
    print()

    async with httpx.AsyncClient(timeout=10.0) as client:

        # Test 1: Root endpoint
        print("1. Testing GET / (root endpoint)...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
                data = response.json()
                print(f"   ✓ Service: {data.get('service')}")
                print(f"   ✓ Version: {data.get('version')}")
            else:
                print(f"   ✗ Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()

        # Test 2: Health check
        print("2. Testing GET /health...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
                data = response.json()
                print(f"   ✓ Service status: {data.get('status')}")
                print(f"   ✓ LLM available: {data.get('llm_service', {}).get('available')}")
                print(f"   ✓ Supported languages: {len(data.get('supported_languages', []))}")
            else:
                print(f"   ⚠ Status: {response.status_code} (may indicate LLM not running)")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()

        # Test 3: List languages
        print("3. Testing GET /languages...")
        try:
            response = await client.get(f"{base_url}/languages")
            if response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
                data = response.json()
                print(f"   ✓ Languages found: {len(data)}")
                for lang in data:
                    print(f"      - {lang.get('language')}: {', '.join(lang.get('extensions', []))}")
            else:
                print(f"   ✗ Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()

        # Test 4: MCP tools
        print("4. Testing GET /mcp/tools...")
        try:
            response = await client.get(f"{base_url}/mcp/tools")
            if response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
                data = response.json()
                print(f"   ✓ Tools found: {len(data.get('tools', []))}")
                for tool in data.get('tools', []):
                    print(f"      - {tool.get('name')}")
            else:
                print(f"   ✗ Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        print()

        # Test 5: Analyze endpoint (this will fail without LMStudio)
        print("5. Testing POST /analyze...")
        print("   (This requires LMStudio to be running)")
        try:
            test_code = """
            public void GetUser(string userId) {
                var sql = "SELECT * FROM Users WHERE Id = '" + userId + "'";
            }
            """

            response = await client.post(
                f"{base_url}/analyze",
                json={
                    "code": test_code,
                    "file_path": "test.cs",
                    "language": "csharp"
                }
            )

            if response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
                data = response.json()
                print(f"   ✓ Language detected: {data.get('language')}")
                print(f"   ✓ Issues found: {len(data.get('issues', []))}")
                print(f"   ✓ Summary: {data.get('summary')}")
            else:
                print(f"   ⚠ Status: {response.status_code}")
                print(f"   ⚠ This is expected if LMStudio is not running")
        except Exception as e:
            print(f"   ⚠ Error: {e}")
            print(f"   ⚠ This is expected if LMStudio is not running")
        print()

    print("=" * 60)
    print("API endpoint tests completed!")
    print()
    print("Note: Full analysis tests require LMStudio with")
    print("qwen/qwen3-coder-30b model running on http://localhost:1234")
    print("=" * 60)


def main():
    """Main entry point"""
    print()
    print("Starting API tests...")
    print("Make sure the service is running on http://localhost:8000")
    print()

    try:
        asyncio.run(test_endpoints())
        return 0
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nTests failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
