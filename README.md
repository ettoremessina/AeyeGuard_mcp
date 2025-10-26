# AeyeGuard MCP Service

A Model Context Protocol (MCP) service that performs automated security analysis on source code using LMStudio with the qwen/qwen3-coder-30b language model.

## Overview

This service automatically detects programming languages and performs comprehensive security analysis using specialized analyzers for each supported language. It exposes a standard HTTP interface for integration with IDEs and development tools.

## Features

- **Automatic Language Detection**: Supports file extension and pattern-based detection
- **Multiple Language Support**: C#, React TypeScript, React JavaScript, Java
- **Comprehensive Security Rules**: 20-25+ security rules per language aligned with OWASP Top 10
- **LLM-Powered Analysis**: Uses qwen/qwen3-coder-30b for intelligent code analysis
- **Structured Results**: Returns detailed security issues with severity, remediation, and references
- **Health Monitoring**: Built-in health check endpoints
- **Extensible Architecture**: Easy to add new language analyzers

## Supported Languages

### C# (.cs)
Security rules include:
- SQL Injection
- Command Injection
- Path Traversal
- Insecure Deserialization
- Weak Cryptography
- Hardcoded Secrets
- And 14+ more security rules

### React TypeScript (.tsx, .ts)
Security rules include:
- XSS Prevention
- Insecure State Management
- Props Validation
- API Security
- Type Safety Issues
- Authentication & Authorization
- And more

### React JavaScript (.jsx, .js)
Security rules include:
- XSS Prevention
- Insecure State Management
- API Security
- Unsafe Code Execution
- Input Validation
- And more

### Java (.java)
Security rules include:
- SQL Injection
- Command Injection
- Path Traversal
- XXE (XML External Entity)
- Insecure Deserialization
- LDAP Injection
- JNDI Injection
- Weak Cryptography
- Hardcoded Credentials
- Resource Leaks
- Unsafe Reflection
- SSRF (Server-Side Request Forgery)
- And 13+ more security rules

## Quick Start

### Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] LMStudio installed and running
- [ ] qwen/qwen3-coder-30b model loaded in LMStudio
- [ ] LMStudio API server running on http://localhost:1234

### Installation

**Option 1: Automated Setup (Recommended)**

```bash
./setup_and_run.sh
```

This script will create `.env`, set up virtual environment, install dependencies, and start the service.

**Option 2: Manual Setup**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for standard LMStudio setup)

# Verify installation
python tests/test_installation.py

# Run the service
python -m src.AeyeGuard_mcp
```

### Configuration

Edit the `.env` file to configure the service:

```env
# LMStudio Configuration
LMSTUDIO_BASE_URL=http://localhost:1234
LMSTUDIO_MODEL=qwen/qwen3-coder-30b
LMSTUDIO_API_KEY=

# MCP Server Configuration
MCP_SERVER_NAME=aeyeguard_mcp
MCP_SERVER_VERSION=1.0.0
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

### Running the Service

**First time:**
```bash
./setup_and_run.sh
```

**Subsequent runs:**
```bash
./run_service.sh
```

**Or run directly:**
```bash
python -m src.AeyeGuard_mcp
```

The service will start an HTTP server on `http://0.0.0.0:8000` (configurable via `.env`).

**Stop service:** Press `Ctrl+C`

## HTTP API Endpoints

The service exposes RESTful HTTP endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze code for vulnerabilities |
| GET | `/languages` | List supported languages |
| GET | `/mcp/tools` | MCP tool definitions |

### Example: Health Check

```bash
curl http://localhost:8000/health
```

### Example: Analyze Code

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public void GetUser(string userId) { var sql = \"SELECT * FROM Users WHERE Id = '\'' + userId + '\''\"; }",
    "file_path": "UserController.cs",
    "language": "auto"
  }'
```

**Request Body:**
```json
{
  "code": "source code to analyze",
  "file_path": "optional/path/to/file.cs",
  "language": "auto"
}
```

Supported language values: `auto`, `csharp`, `react_typescript`, `react_javascript`, `java`

### Example: List Languages

```bash
curl http://localhost:8000/languages
```

## Testing

### Verify Installation

```bash
python tests/test_installation.py
```

Expected output:
```
✓ All tests passed! Installation is complete.
```

### Test HTTP Endpoints

```bash
# Check service is running
curl http://localhost:8000/

# Check health
curl http://localhost:8000/health

# List supported languages
curl http://localhost:8000/languages

# Analyze code (requires LMStudio)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "var sql = \"SELECT * FROM users WHERE id = \" + userId;",
    "file_path": "test.cs",
    "language": "auto"
  }'
```

### Run Automated Tests

```bash
# Service must be running in another terminal
python tests/test_api.py
```

### Run Usage Examples

```bash
python tests/example_usage.py
```

This demonstrates language detection, health checks, and code analysis (requires LMStudio running).

## Architecture

### Core Components

1. **MCP Service** ([src/AeyeGuard_mcp.py](src/AeyeGuard_mcp.py))
   - Implements MCP protocol interface
   - FastAPI application with HTTP endpoints
   - Handles tool registration and execution

2. **Language Detection** ([src/services/language_detector.py](src/services/language_detector.py))
   - Extension-based detection (primary)
   - Pattern-based detection (fallback)

3. **LLM Service** ([src/services/llm_service.py](src/services/llm_service.py))
   - LMStudio integration via OpenAI-compatible API
   - Handles prompt engineering and response parsing

4. **Security Analyzers** ([src/analyzers/](src/analyzers/))
   - Base analyzer with common functionality
   - Language-specific analyzers with security rules

### Data Models

Located in [src/models/data_models.py](src/models/data_models.py):

- **SecurityIssue**: Individual vulnerability details
- **AnalysisRequest**: Input for analysis
- **AnalysisResult**: Analysis output with issues and metadata
- **LanguageType**: Supported language enumeration

## Extending the Service

### Adding a New Language

1. Add language to `LanguageType` enum in [src/models/data_models.py](src/models/data_models.py)
2. Create analyzer class inheriting from `BaseSecurityAnalyzer` in [src/analyzers/](src/analyzers/)
3. Implement `get_language_type()` and `get_security_rules_prompt()` methods
4. Update `EXTENSION_MAP` in [src/services/language_detector.py](src/services/language_detector.py)
5. Register analyzer in [src/AeyeGuard_mcp.py](src/AeyeGuard_mcp.py) `__init__()` method

## Integration

The HTTP API can be integrated with:
- VSCode extensions
- JetBrains IDE plugins
- Custom development tools
- CI/CD pipelines
- Any HTTP-capable client

## Security Considerations

- Code is preprocessed to remove comments before LLM analysis
- No code is stored or transmitted beyond LMStudio
- LLM responses are validated and sanitized
- Structured output format prevents injection attacks
- Health checks ensure service availability

## Error Handling

The service implements graceful degradation:
- LLM unavailability returns health status
- Language detection failures fall back to pattern matching
- Analysis errors return partial results with error metadata
- Invalid input produces clear error messages

## Troubleshooting

### LMStudio Not Connected

**Error**: `LLM analysis failed: Connection refused`

**Solution**:
1. Start LMStudio application
2. Load the qwen/qwen3-coder-30b model
3. Enable API server (usually on port 1234)
4. Verify: `curl http://localhost:1234/v1/models`
5. Check `LMSTUDIO_BASE_URL` in `.env` matches LMStudio port

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
```

### Permission Denied on Scripts

**Error**: `Permission denied: ./run_service.sh`

**Solution**:
```bash
chmod +x setup_and_run.sh run_service.sh tests/*.py
```

### Port Already in Use

**Error**: `[Errno 48] Address already in use`

**Solution**:
```bash
lsof -ti:8000 | xargs kill -9
# OR change MCP_PORT in .env
```

### Virtual Environment Issues

**Error**: `venv not found`

**Solution**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Empty Analysis Results

If `/analyze` returns no security issues for clearly vulnerable code:
- Verify LMStudio is running with model loaded
- Check language detection: `curl http://localhost:8000/languages`
- Review service logs for LLM JSON parsing errors
- Remember: code preprocessing strips comments

## Success Indicators

You'll know everything is working when:

✓ Installation verification passes all tests
✓ Health check shows `"status": "healthy"`
✓ Example usage runs without errors
✓ LMStudio connection is established
✓ Service responds to MCP tool calls

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./setup_and_run.sh` | First-time setup and run |
| `./run_service.sh` | Start the service (quick) |
| `python tests/test_installation.py` | Verify installation |
| `python tests/test_api.py` | Test all endpoints |
| `python tests/example_usage.py` | Run examples |
| `python -m src.AeyeGuard_mcp` | Run service directly |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Additional Documentation

- [CLAUDE.md](CLAUDE.md): Architectural guidance for development
- [docs/specifications.md](docs/specifications.md): Complete functional specifications, security rules, MCP tool schemas
