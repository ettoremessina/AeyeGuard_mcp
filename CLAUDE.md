# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AeyeGuard MCP Service** - An MCP service that performs automated security analysis on source code using LMStudio with the qwen/qwen3-coder-30b language model. The service exposes HTTP/REST endpoints for integration with IDEs and development tools.

## Architecture

### Core Components

The system follows a layered architecture with clear separation of concerns:

1. **HTTP Transport Layer** ([src/AeyeGuard_mcp.py](src/AeyeGuard_mcp.py))
   - FastAPI application with lifespan management
   - Global `SecurityAnalyzerMCP` instance initialized on startup
   - RESTful endpoints: `/analyze`, `/health`, `/languages`, `/mcp/tools`
   - Async request handling throughout

2. **Service Layer**
   - **LanguageDetector** ([src/services/language_detector.py](src/services/language_detector.py)): Extension-based detection (primary) with pattern-based fallback
   - **LLMService** ([src/services/llm_service.py](src/services/llm_service.py)): Uses LMStudio's OpenAI-compatible API (`/v1/chat/completions`) with httpx async client

3. **Analyzer Layer** ([src/analyzers/](src/analyzers/))
   - **BaseSecurityAnalyzer** ([base_analyzer.py](src/analyzers/base_analyzer.py)): Abstract base with common preprocessing, issue creation, summary generation
   - Language-specific analyzers (C#, React TypeScript, React JavaScript) inherit from base and implement `get_language_type()` and `get_security_rules_prompt()`
   - Analyzers registered in `SecurityAnalyzerMCP.__init__()` as a dict mapping `LanguageType` to analyzer instances

4. **Data Models** ([src/models/data_models.py](src/models/data_models.py))
   - Pydantic models for validation: `AnalysisRequest`, `AnalysisResult`, `SecurityIssue`, `LanguageType`, `SeverityLevel`

### Analysis Flow

Request → Language Detection → Code Preprocessing (comment removal) → LLM Analysis → JSON Response Parsing → SecurityIssue Creation → Result Enrichment → Response

Key implementation details:
- Code preprocessing removes comments but preserves line structure for accurate line numbers
- LLM responses are parsed with JSON extraction from code blocks (`parse_llm_response`)
- Issue severity is validated and defaults to MEDIUM if invalid
- Analysis errors return partial results with error metadata rather than failing completely

### Extension Points

To add a new language:
1. Add to `LanguageType` enum in [src/models/data_models.py](src/models/data_models.py)
2. Create analyzer inheriting `BaseSecurityAnalyzer` in [src/analyzers/](src/analyzers/)
3. Add extension mappings in `LanguageDetector.EXTENSION_MAP` and patterns in `LANGUAGE_PATTERNS`
4. Register analyzer in `SecurityAnalyzerMCP.__init__()` analyzers dict

## Configuration

Environment variables (`.env` file):
- `LMSTUDIO_BASE_URL`: http://localhost:1234 (LMStudio server URL)
- `LMSTUDIO_MODEL`: qwen/qwen3-coder-30b (model name)
- `LMSTUDIO_API_KEY`: Optional authentication
- `MCP_HOST`: 0.0.0.0 (bind to all interfaces)
- `MCP_PORT`: 8000 (HTTP port)

## Commands

### Setup
```bash
cp .env.example .env                    # Create config (edit as needed)
pip install -r requirements.txt         # Install dependencies
chmod +x *.sh *.py                      # Make scripts executable
```

### Running
```bash
./setup_and_run.sh                      # First-time setup + run
./run_service.sh                        # Quick start (after setup)
python -m src.AeyeGuard_mcp             # Manual start
```

Stop service: `Ctrl+C`

### Testing
```bash
python tests/test_installation.py      # Verify installation
curl http://localhost:8000/health       # Check service health
python tests/test_api.py                # Test all endpoints (service must be running)
python tests/example_usage.py           # Run examples (requires LMStudio)
```

### Development
To run a single endpoint test, use curl:
```bash
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" \
  -d '{"code": "YOUR_CODE", "file_path": "test.cs", "language": "auto"}'
```

## Key Implementation Details

- **Stateless Service**: No session state maintained - horizontally scalable
- **Async Throughout**: FastAPI app uses async handlers, LLMService uses httpx AsyncClient
- **Error Recovery**: LLM failures return graceful error responses with metadata, not HTTP 500s
- **Comment Preservation**: Preprocessing removes comments but keeps empty lines to maintain line numbers
- **JSON Parsing**: `parse_llm_response` handles LLMs wrapping JSON in code blocks
- **Analyzer Registration**: Analyzers must be added to `SecurityAnalyzerMCP.__init__()` dict to be used

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9          # Kill process on port 8000
# OR change MCP_PORT in .env
```

### LLM Service Unavailable
Health check shows `"available": false`:
1. Start LMStudio and load qwen/qwen3-coder-30b model
2. Verify: `curl http://localhost:1234/v1/models`
3. Check `LMSTUDIO_BASE_URL` in `.env` matches LMStudio port

### Empty Analysis Results
- Verify LMStudio is running with model loaded
- Check language detection: `curl http://localhost:8000/languages`
- Review logs for LLM JSON parsing errors
- Remember: code preprocessing strips comments

### Script Permission Denied
```bash
chmod +x *.sh *.py
```

## Additional Documentation

- [README.md](README.md): Complete installation guide, API documentation, and troubleshooting
- [docs/specifications.md](docs/specifications.md): Complete functional spec, security rules, MCP tool schemas
