# Project Structure

## Directory Tree

```
AeyeGuard_mcp/
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore patterns
├── CLAUDE.md                          # Claude Code guidance
├── README.md                          # Complete user documentation
├── PROJECT_STRUCTURE.md               # This file - project layout reference
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup configuration
├── setup_and_run.sh                  # First-time setup and run script
├── run_service.sh                    # Quick service launcher
│
├── docs/
│   └── specifications.md             # Functional specification
│
├── tests/
│   ├── test_installation.py          # Installation verification script
│   ├── test_api.py                   # API endpoint tests
│   └── example_usage.py              # Usage examples
│
└── src/
    ├── __init__.py                   # Package initialization
    ├── AeyeGuard_mcp.py             # Main MCP service entry point
    │
    ├── models/
    │   ├── __init__.py              # Models package
    │   └── data_models.py           # Pydantic data models
    │
    ├── services/
    │   ├── __init__.py              # Services package
    │   ├── language_detector.py     # Language detection service
    │   └── llm_service.py           # LLM integration service
    │
    └── analyzers/
        ├── __init__.py              # Analyzers package
        ├── base_analyzer.py         # Abstract base security analyzer
        ├── csharp_analyzer.py       # C# security analyzer
        ├── react_typescript_analyzer.py  # React TypeScript analyzer
        ├── react_javascript_analyzer.py  # React JavaScript analyzer
        └── java_analyzer.py         # Java security analyzer
```

## File Descriptions

### Configuration & Setup
- **`.env.example`** - Template for environment configuration (LMStudio URL, model name, server port)
- **`.gitignore`** - Git ignore patterns for Python projects
- **`requirements.txt`** - Python dependencies (langchain, mcp, pydantic, fastapi, httpx)
- **`setup.py`** - Package setup with entry points and metadata
- **`setup_and_run.sh`** - Automated first-time setup script (creates venv, installs deps, runs service)
- **`run_service.sh`** - Quick launcher to run the service after setup

### Documentation
- **`CLAUDE.md`** - Architectural guidance for Claude Code instances working on this codebase
- **`README.md`** - Complete installation guide, API documentation, troubleshooting
- **`PROJECT_STRUCTURE.md`** - This file, project layout reference
- **`docs/specifications.md`** - Detailed functional specification with security rules

### Core Service
- **`src/AeyeGuard_mcp.py`** - Main FastAPI application and MCP service implementation
  - Exposes HTTP endpoints: `/analyze`, `/health`, `/languages`, `/mcp/tools`
  - Manages `SecurityAnalyzerMCP` instance with lifecycle management
  - Routes requests to appropriate language analyzers

### Data Models (`src/models/`)
- **`data_models.py`** - Pydantic models for validation:
  - `SecurityIssue` - Individual vulnerability with severity, location, remediation
  - `AnalysisRequest` - Input model (code, file_path, language)
  - `AnalysisResult` - Output with issues, summary, metadata
  - `LanguageType` - Enum for CSHARP, REACT_TYPESCRIPT, REACT_JAVASCRIPT, UNKNOWN
  - `SeverityLevel` - Enum for LOW, MEDIUM, HIGH, CRITICAL

### Services (`src/services/`)
- **`language_detector.py`** - Detects programming language from file extension or code patterns
  - Primary: Extension-based detection via `EXTENSION_MAP`
  - Fallback: Pattern-based detection via `LANGUAGE_PATTERNS`

- **`llm_service.py`** - LMStudio integration
  - Uses OpenAI-compatible API (`/v1/chat/completions`)
  - Async code analysis with httpx AsyncClient
  - Health checking and JSON response parsing

### Analyzers (`src/analyzers/`)
- **`base_analyzer.py`** - Abstract base class with common functionality
  - Code preprocessing (removes comments, preserves line structure)
  - SecurityIssue creation from LLM responses
  - Summary generation and error handling

- **`csharp_analyzer.py`** - C# security analysis (20+ rules)
  - SQL injection, command injection, path traversal
  - Insecure deserialization, weak cryptography, hardcoded secrets

- **`react_typescript_analyzer.py`** - React TypeScript security analysis
  - XSS prevention, insecure state management, props validation
  - API security, type safety, authentication/authorization

- **`react_javascript_analyzer.py`** - React JavaScript security analysis
  - XSS prevention, state management, API security
  - Unsafe code execution, input validation

- **`java_analyzer.py`** - Java security analysis (25+ rules)
  - SQL injection, command injection, path traversal, XXE, JNDI injection
  - Insecure deserialization, weak cryptography, hardcoded credentials
  - LDAP injection, SSRF, unsafe reflection, resource leaks

### Testing & Examples (`tests/`)
- **`test_installation.py`** - Verifies all dependencies and imports are working
- **`test_api.py`** - Tests all HTTP endpoints (requires service running)
- **`example_usage.py`** - Demonstrates programmatic usage with code examples

## Key Conventions

- **Module Organization**: Layered architecture (HTTP → Service → Analyzer → Models)
- **Naming**: Snake_case for files/modules, PascalCase for classes, lowercase for packages
- **Async**: All LLM operations use async/await
- **Imports**: Absolute imports from `src` package root
- **Entry Point**: Run via `python -m src.AeyeGuard_mcp`

## See Also

- [README.md](README.md) - Installation, usage, and API documentation
- [CLAUDE.md](CLAUDE.md) - Architecture and development guidance
- [docs/specifications.md](docs/specifications.md) - Functional specifications
