# AeyeGuard MCP Service - Functional Specification

## Overview

AeyeGuard MCP Service is a Model Context Protocol (MCP) service that performs automated security analysis on source code using LMStudio with the qwen/qwen3-coder-30b language model. The service automatically detects programming languages and delegates analysis to specialized security analyzers.
This MCP Service must espose a standard http interface for integration with IDEs, stdio must not be supported for integration.

## Architecture

### Core Components

1. **MCP Service** (`src/AeyeGuard_mcp.py`)
   - Implements the Model Context Protocol interface
   - Handles tool registration and execution
   - Manages communication via TCP/WebSocket transport
   - Provides three main tools: `analyze_security`, `health_check`, `list_supported_languages`

2. **Language Detection Service**
   - Automatically detects programming languages from code content
   - Supports file extension-based detection; currently supports C#, React (tsx and jsx), and Java.
   - Uses pattern matching for language identification
   - Returns standardized language types

3. **LLM Service**
   - Integrates with LMStudio using langchain
   - Uses qwen/qwen3-coder-30b model for security analysis
   - Handles prompt engineering and response parsing
   - Provides health checking capabilities

4. **Specialized Analyzers**
   - Base analyzer class with common functionality
   - C# security analyzer with 20+ security rules
   - React security analyzer supporting both TypeScript and JavaScript
   - Java security analyzer with 25+ security rules
   - Extensible architecture for future language support

## Supported Languages

### Currently Supported
- **C#** (`LanguageType.CSHARP`)
  - File extensions: `.cs`
  - Security rules: SQL injection, command injection, path traversal, deserialization, cryptographic issues, hardcoded secrets, input validation, authentication bypass, and more

- **React TypeScript** (`LanguageType.REACT_TYPESCRIPT`)
  - File extensions: `.tsx`, `.ts`
  - Security rules: XSS prevention, insecure state management, props validation, API security, type safety, and more

- **React JavaScript** (`LanguageType.REACT_JAVASCRIPT`)
  - File extensions: `.jsx`, `.js`
  - Security rules: XSS prevention, insecure state management, props validation, API security, and more

- **Java** (`LanguageType.JAVA`)
  - File extensions: `.java`
  - Security rules: SQL injection, command injection, path traversal, XXE (XML External Entity), insecure deserialization, LDAP injection, insecure random number generation, weak cryptography, hardcoded credentials, resource leaks, input validation issues, authentication bypass, session management flaws, insecure file handling, unsafe reflection, JNI security issues, JNDI injection, server-side request forgery (SSRF), insecure SSL/TLS configuration, path manipulation, regex DoS, log injection, insecure XML processing, unvalidated redirects, and more

### Future Extensions
The architecture supports easy addition of new languages by:
1. Adding new language types to the `LanguageType` enum
2. Creating specialized analyzer classes inheriting from `BaseSecurityAnalyzer`
3. Updating the language detector patterns
4. Registering new analyzers in the MCP service

## Data Models

### Core Models

- **SecurityIssue**: Represents individual security vulnerabilities
  - Fields: id, title, description, severity, line_number, column_number, file_path, code_snippet, remediation, references
  - Severity levels: LOW, MEDIUM, HIGH, CRITICAL

- **AnalysisRequest**: Input model for security analysis
  - Fields: code, file_path, language (optional)

- **AnalysisResult**: Output model containing analysis results
  - Fields: language, issues, summary, analysis_metadata

- **LanguageType**: Enumeration of supported languages
  - Values: CSHARP, REACT_TYPESCRIPT, REACT_JAVASCRIPT, JAVA, UNKNOWN

## MCP Tools Specification

### 1. analyze_security
**Purpose**: Performs comprehensive security analysis on source code

**Parameters**:
- `code` (string, required): Source code to analyze
- `file_path` (string, optional): File path for context and extension-based language detection
- `language` (string, optional): Programming language specification
  - Values: "csharp", "react_typescript", "react_javascript", "java", "auto"
  - Default: "auto" (automatic detection)

**Response**: Formatted markdown report containing:
- Language detection results
- Security issues with severity classification
- Detailed descriptions and remediation suggestions
- Analysis metadata and statistics

### 2. health_check
**Purpose**: Verifies service health and dependency availability

**Parameters**: None

**Response**: JSON object containing:
- Service status and version
- LLM service availability
- Supported languages list
- Connection health status

### 3. list_supported_languages
**Purpose**: Lists all supported programming languages and their metadata

**Parameters**: None

**Response**: JSON array of language objects with:
- Language identifier
- Description
- Supported file extensions

## Security Analysis Process

### 1. Language Detection
- File extension analysis (primary method)
- Code pattern matching (fallback method)
- Returns standardized language type

### 2. Code Preprocessing
- Comment removal for focused analysis
- Language-specific preprocessing rules
- Maintains code structure for accurate line number reporting

### 3. LLM Analysis
- Sends preprocessed code to qwen/qwen3-coder-30b model
- Uses language-specific security rule prompts
- Requests structured JSON response with issue details

### 4. Result Processing
- Converts LLM response to SecurityIssue objects
- Validates and enriches issue data
- Generates analysis summary and metadata

### 5. Report Generation
- Formats results as structured markdown
- Includes severity-based issue categorization
- Provides actionable remediation guidance

## Configuration

### Settings (defaulted)
- `LMSTUDIO_BASE_URL`: LMStudio server URL (default: http://localhost:1234)
- `LMSTUDIO_MODEL`: Model name (default: qwen/qwen3-coder-30b)
- `LMSTUDIO_API_KEY`: API key for authentication (optional)
- `MCP_SERVER_NAME`: MCP server identifier (default: aeyeguard_mcp)
- `MCP_SERVER_VERSION`: Service version (default: 1.0.0)

### Dependencies
- langchain: LLM integration framework
- langchain-community: Community extensions
- mcp: Model Context Protocol implementation
- pydantic: Data validation and serialization
- httpx: HTTP client for health checks
- python-dotenv: Environment variable management

## Error Handling

### Graceful Degradation
- LLM service unavailability: Returns error with health status
- Language detection failure: Falls back to pattern matching
- Analysis failures: Returns partial results with error metadata
- Invalid input: Provides clear error messages

### Logging and Monitoring
- Structured error reporting in analysis metadata
- Health check endpoints for monitoring
- Detailed error messages for debugging

## Performance Considerations

### Optimization Strategies
- Efficient language detection with pattern caching
- Streamlined LLM prompts for faster processing
- Minimal code preprocessing to reduce overhead
- Structured response parsing for reliability

### Scalability
- Stateless service design for horizontal scaling
- Configurable LLM parameters for different performance needs
- Modular analyzer architecture for easy maintenance

## Security Considerations

### Input Validation
- Code content sanitization
- File path validation
- Language parameter validation
- Size limits for code analysis

### Output Sanitization
- Safe markdown generation
- Controlled information disclosure
- Secure error message handling

## Testing and Quality Assurance

### Test Coverage
- Unit tests for language detection
- Integration tests for analyzer functionality
- End-to-end tests for MCP service
- Installation verification scripts

### Quality Metrics
- Security rule coverage per language
- Analysis accuracy validation
- Performance benchmarking
- Error rate monitoring

## Deployment

### Prerequisites
- Python 3.8+
- LMStudio with qwen/qwen3-coder-30b model
- Virtual environment (recommended)

### Extensibility Points
- Plugin architecture for custom analyzers
- Configurable security rule sets
- Custom LLM model support
- Advanced reporting formats
- Integration with security databases

## Compliance and Standards

### Security Standards
- OWASP Top 10 compliance
- Language-specific security best practices
- Industry-standard vulnerability classifications
- CVE reference integration

### Protocol Compliance
- Full MCP protocol implementation
- Standard tool interface compliance
- Proper error handling and reporting
- Documentation and metadata standards

## Java Security Analysis Rules

### Injection Vulnerabilities

#### 1. SQL Injection
**Description**: Detection of unsafe SQL query construction using string concatenation or unparameterized queries.
**Patterns**:
- String concatenation in SQL queries (`"SELECT * FROM users WHERE id = '" + userId + "'"`)
- Direct use of user input in `Statement.executeQuery()`
- Missing prepared statements for dynamic queries

**Severity**: CRITICAL

**Remediation**:
- Use `PreparedStatement` with parameterized queries
- Employ ORM frameworks with parameterized queries (Hibernate, JPA)
- Input validation and sanitization
- Principle of least privilege for database accounts

#### 2. Command Injection
**Description**: Unsafe execution of system commands with user-controlled input.
**Patterns**:
- `Runtime.exec()` with concatenated user input
- `ProcessBuilder` with unsanitized arguments
- Shell command execution with user data

**Severity**: CRITICAL

**Remediation**:
- Avoid executing system commands when possible
- Use allowlists for permitted commands
- Sanitize all user input
- Use secure alternatives to shell execution

#### 3. LDAP Injection
**Description**: Unsafe LDAP query construction allowing filter manipulation.
**Patterns**:
- String concatenation in LDAP filters
- Unescaped user input in `SearchControls`
- Direct DN construction from user input

**Severity**: HIGH

**Remediation**:
- Escape LDAP special characters
- Use parameterized LDAP queries
- Validate input against expected patterns

#### 4. XML External Entity (XXE)
**Description**: Vulnerable XML parsing allowing external entity expansion.
**Patterns**:
- `DocumentBuilderFactory` without disabled external entities
- `SAXParserFactory` with default configuration
- `XMLInputFactory` without secure processing

**Severity**: HIGH

**Remediation**:
```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

#### 5. JNDI Injection
**Description**: Unsafe JNDI lookups allowing remote code execution.
**Patterns**:
- `Context.lookup()` with user-controlled strings
- Unsafe deserialization via JNDI
- Remote codebase loading

**Severity**: CRITICAL

**Remediation**:
- Validate JNDI names against allowlist
- Disable remote class loading
- Use `com.sun.jndi.ldap.object.trustURLCodebase=false`

### Cryptographic Issues

#### 6. Weak Cryptography
**Description**: Use of deprecated or weak cryptographic algorithms.
**Patterns**:
- DES, 3DES, RC4, MD5, SHA1
- ECB mode for encryption
- Static/hardcoded encryption keys
- Insufficient key lengths (< 2048 bits for RSA)

**Severity**: HIGH

**Remediation**:
- Use AES-256 with GCM or CBC mode
- SHA-256 or SHA-3 for hashing
- RSA with minimum 2048-bit keys
- Proper key management and rotation

#### 7. Insecure Random Number Generation
**Description**: Use of predictable random number generators for security.
**Patterns**:
- `java.util.Random` for security purposes
- `Math.random()` for cryptographic operations
- Predictable seed values

**Severity**: MEDIUM

**Remediation**:
```java
SecureRandom secureRandom = new SecureRandom();
```

#### 8. Insecure SSL/TLS Configuration
**Description**: Weak SSL/TLS configuration or disabled certificate validation.
**Patterns**:
- Trusting all certificates
- Disabled hostname verification
- Allowing SSLv3, TLSv1.0, TLSv1.1
- Custom `TrustManager` that accepts all certificates

**Severity**: HIGH

**Remediation**:
- Use TLS 1.2 or 1.3
- Enable certificate validation
- Use system trust store
- Implement certificate pinning for sensitive applications

### Deserialization Vulnerabilities

#### 9. Insecure Deserialization
**Description**: Unsafe deserialization of untrusted data leading to RCE.
**Patterns**:
- `ObjectInputStream.readObject()` on untrusted data
- Deserialization without validation
- Missing serialization filters

**Severity**: CRITICAL

**Remediation**:
- Avoid deserializing untrusted data
- Implement serialization filters (Java 9+)
- Use safer alternatives (JSON, Protocol Buffers)
- Validate class types before deserialization

### Authentication & Session Management

#### 10. Hardcoded Credentials
**Description**: Passwords, API keys, or secrets embedded in source code.
**Patterns**:
- Literal password strings in code
- Hardcoded API keys or tokens
- Embedded database credentials
- Static encryption keys

**Severity**: CRITICAL

**Remediation**:
- Use environment variables
- External configuration files (excluded from version control)
- Secret management systems (HashiCorp Vault, AWS Secrets Manager)
- Key management services

#### 11. Session Management Flaws
**Description**: Insecure session handling and fixation vulnerabilities.
**Patterns**:
- Session IDs in URLs
- Missing session timeout
- No session regeneration after authentication
- Predictable session identifiers

**Severity**: HIGH

**Remediation**:
- Use HTTP-only, secure cookies
- Implement proper session timeout
- Regenerate session ID after login
- Use framework-provided session management

#### 12. Authentication Bypass
**Description**: Flaws allowing authentication mechanism bypass.
**Patterns**:
- Missing authentication checks
- Weak password policies
- Insecure "remember me" functionality
- No account lockout mechanism

**Severity**: CRITICAL

**Remediation**:
- Implement proper authentication on all endpoints
- Enforce strong password requirements
- Multi-factor authentication
- Rate limiting and account lockout

### Path Traversal & File Handling

#### 13. Path Traversal
**Description**: Directory traversal allowing access to unauthorized files.
**Patterns**:
- User input in file paths without validation
- Missing canonicalization
- `../` sequences in filenames
- Absolute path manipulation

**Severity**: HIGH

**Remediation**:
```java
Path basePath = Paths.get("/safe/directory").toRealPath();
Path userPath = basePath.resolve(userInput).normalize();
if (!userPath.startsWith(basePath)) {
    throw new SecurityException("Path traversal attempt");
}
```

#### 14. Insecure File Upload
**Description**: Unrestricted file uploads leading to code execution.
**Patterns**:
- No file type validation
- Missing file size limits
- Executable files in web root
- No content scanning

**Severity**: HIGH

**Remediation**:
- Validate file extensions and MIME types
- Store uploads outside web root
- Rename uploaded files
- Scan for malware
- Implement file size limits

#### 15. Resource Leaks
**Description**: Unclosed resources leading to DoS or information disclosure.
**Patterns**:
- Missing `try-with-resources` for streams
- Unclosed database connections
- File handles not released
- Network connections left open

**Severity**: MEDIUM

**Remediation**:
```java
try (FileInputStream fis = new FileInputStream(file)) {
    // Use resource
} // Automatically closed
```

### Code Execution & Reflection

#### 16. Unsafe Reflection
**Description**: Dynamic class loading and reflection with untrusted input.
**Patterns**:
- `Class.forName()` with user input
- `Method.invoke()` on untrusted classes
- Dynamic proxy creation
- Unsafe use of `URLClassLoader`

**Severity**: HIGH

**Remediation**:
- Validate class names against allowlist
- Restrict reflection to trusted packages
- Use security manager to control reflection
- Avoid dynamic class loading when possible

#### 17. Expression Language Injection
**Description**: Unsafe evaluation of expression language with user input.
**Patterns**:
- Unvalidated input in JSP/JSF EL expressions
- OGNL injection in Struts
- SpEL injection in Spring
- MVEL expression injection

**Severity**: CRITICAL

**Remediation**:
- Sanitize all user input in expressions
- Use parameterized expressions
- Disable expression evaluation when possible
- Upgrade to patched framework versions

### Server-Side Request Forgery (SSRF)

#### 18. SSRF Vulnerabilities
**Description**: Application makes requests to unintended locations.
**Patterns**:
- URL fetching with user-controlled destinations
- Unvalidated redirect URLs
- API calls to user-specified endpoints
- Image/document processing from URLs

**Severity**: HIGH

**Remediation**:
- Validate and sanitize URLs
- Use allowlist of permitted domains
- Disable redirects or validate redirect targets
- Network segmentation to restrict internal access

### Input Validation

#### 19. Regex Denial of Service (ReDoS)
**Description**: Regular expressions vulnerable to catastrophic backtracking.
**Patterns**:
- Nested quantifiers: `(a+)+`
- Overlapping alternations: `(a|a)*`
- Unbounded repetition with user input

**Severity**: MEDIUM

**Remediation**:
- Use atomic groups and possessive quantifiers
- Set regex timeout limits
- Validate regex complexity
- Use non-backtracking regex engines

#### 20. Log Injection
**Description**: Unvalidated user input in log statements.
**Patterns**:
- Direct user input in log messages
- Missing newline sanitization
- Format string vulnerabilities in logs

**Severity**: LOW

**Remediation**:
```java
// Bad
logger.info("User input: " + userInput);

// Good
logger.info("User input: {}", userInput.replace("\n", "").replace("\r", ""));
```

#### 21. Mass Assignment
**Description**: Binding user input directly to object properties.
**Patterns**:
- Automatic binding without field restrictions
- Missing `@JsonIgnore` on sensitive fields
- No DTO layer for input validation

**Severity**: MEDIUM

**Remediation**:
- Use DTOs for input
- Explicitly define allowed fields
- Use `@JsonIgnore` for sensitive properties
- Implement proper validation

### Additional Security Concerns

#### 22. Insecure XML Processing
**Description**: XML bombs and entity expansion attacks.
**Patterns**:
- Unlimited entity expansion
- External DTD processing
- No limits on XML document size

**Severity**: HIGH

**Remediation**:
- Set entity expansion limits
- Disable external DTD processing
- Implement XML size limits
- Use secure XML parsers

#### 23. Unvalidated Redirects
**Description**: Open redirect vulnerabilities.
**Patterns**:
- `response.sendRedirect()` with user input
- No URL validation
- Missing domain allowlist

**Severity**: MEDIUM

**Remediation**:
- Validate redirect URLs against allowlist
- Use relative URLs when possible
- Implement proper URL parsing and validation

#### 24. JNI Security Issues
**Description**: Unsafe use of Java Native Interface.
**Patterns**:
- Unchecked native method calls
- Buffer overflows in native code
- Missing input validation before JNI calls

**Severity**: HIGH

**Remediation**:
- Validate all input before JNI calls
- Use managed code when possible
- Implement bounds checking
- Regular security audits of native code

#### 25. Race Conditions & Concurrency
**Description**: Thread safety and TOCTOU vulnerabilities.
**Patterns**:
- Check-then-act on shared resources
- Unsynchronized access to mutable state
- Double-checked locking issues
- Missing volatile or atomic operations

**Severity**: MEDIUM

**Remediation**:
- Use proper synchronization
- Atomic operations for critical sections
- Immutable objects when possible
- Concurrent collections and utilities

### Language-Specific Patterns

#### Java Detection Patterns for Language Identification
- `package [a-z][a-z0-9_.]*;`
- `import (java|javax|org)\\.`
- `public (class|interface|enum) \\w+`
- `@(Override|Autowired|Entity|Controller|Service|Repository)`
- `(public|private|protected)\\s+(static\\s+)?(void|int|String|boolean)`

### Code Preprocessing for Java
- Remove single-line comments (`//`)
- Remove multi-line comments (`/* */`)
- Remove Javadoc comments (`/** */`)
- Preserve annotations for security context
- Maintain line structure for accurate reporting