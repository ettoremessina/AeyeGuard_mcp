from setuptools import setup, find_packages

setup(
    name="aeyeguard-mcp",
    version="1.0.0",
    description="AeyeGuard MCP Service - Security Static Analysis",
    author="ettoremessina",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.13",
        "mcp>=0.9.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aeyeguard-mcp=src.AeyeGuard_mcp:main",
        ],
    },
)
