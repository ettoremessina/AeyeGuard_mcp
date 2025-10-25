from src.models import LanguageType
from .base_analyzer import BaseSecurityAnalyzer


class JavaSecurityAnalyzer(BaseSecurityAnalyzer):
    """Security analyzer for Java code"""

    def get_language_type(self) -> LanguageType:
        """Return Java language type"""
        return LanguageType.JAVA

    def get_security_rules_prompt(self) -> str:
        """Return security rules prompt for Java analysis"""
        return """
You are a Java security expert. Analyze the following Java code for security vulnerabilities.

Focus on these security rules (25+ comprehensive checks):

**Injection Vulnerabilities:**
1. **SQL Injection**: Look for string concatenation in SQL queries, Statement.executeQuery() with user input, missing PreparedStatement usage
2. **Command Injection**: Identify Runtime.exec(), ProcessBuilder with unsanitized user input
3. **LDAP Injection**: Check for string concatenation in LDAP filters, unescaped user input in SearchControls
4. **XML External Entity (XXE)**: Find DocumentBuilderFactory, SAXParserFactory, XMLInputFactory without disabled external entities
5. **JNDI Injection**: Look for Context.lookup() with user-controlled strings, unsafe deserialization via JNDI

**Cryptographic Issues:**
6. **Weak Cryptography**: Detect DES, 3DES, RC4, MD5, SHA1, ECB mode, hardcoded keys, insufficient key lengths
7. **Insecure Random Number Generation**: Find java.util.Random or Math.random() used for security purposes instead of SecureRandom
8. **Insecure SSL/TLS Configuration**: Identify trusting all certificates, disabled hostname verification, allowing SSLv3/TLS1.0/1.1, custom TrustManager accepting all

**Deserialization Vulnerabilities:**
9. **Insecure Deserialization**: Check for ObjectInputStream.readObject() on untrusted data, missing serialization filters

**Authentication & Session Management:**
10. **Hardcoded Credentials**: Find literal passwords, API keys, database credentials, static encryption keys in code
11. **Session Management Flaws**: Identify session IDs in URLs, missing timeouts, no session regeneration, predictable identifiers
12. **Authentication Bypass**: Look for missing authentication checks, weak password policies, insecure "remember me"

**Path Traversal & File Handling:**
13. **Path Traversal**: Check for user input in file paths, missing canonicalization, ../ sequences, absolute path manipulation
14. **Insecure File Upload**: Find missing file type validation, size limits, executable files in web root, no content scanning
15. **Resource Leaks**: Identify missing try-with-resources, unclosed connections, file handles, network connections

**Code Execution & Reflection:**
16. **Unsafe Reflection**: Detect Class.forName(), Method.invoke() with user input, dynamic proxies, URLClassLoader
17. **Expression Language Injection**: Find unvalidated input in JSP/JSF EL, OGNL injection (Struts), SpEL injection (Spring), MVEL

**Server-Side Request Forgery:**
18. **SSRF Vulnerabilities**: Check for URL fetching with user destinations, unvalidated redirects, API calls to user endpoints

**Input Validation:**
19. **Regex Denial of Service (ReDoS)**: Identify nested quantifiers (a+)+, overlapping alternations, unbounded repetition
20. **Log Injection**: Find direct user input in log messages, missing newline sanitization, format string vulnerabilities
21. **Mass Assignment**: Look for automatic binding without field restrictions, missing @JsonIgnore

**Additional Security Concerns:**
22. **Insecure XML Processing**: Check for unlimited entity expansion, external DTD processing, no XML size limits
23. **Unvalidated Redirects**: Find response.sendRedirect() with user input, missing URL validation
24. **JNI Security Issues**: Identify unchecked native method calls, buffer overflows, missing input validation before JNI
25. **Race Conditions & Concurrency**: Look for check-then-act patterns, unsynchronized access to mutable state, double-checked locking issues

**Additional Checks:**
- Missing input validation on user-controlled data
- Insecure cookie configuration (missing HttpOnly, Secure, SameSite)
- Information disclosure in error messages or stack traces
- Missing authorization checks
- Unsafe use of reflection APIs
- Time-of-check to time-of-use (TOCTOU) vulnerabilities
- Null pointer dereferences that could lead to DoS

For each issue found, provide:
- id: Unique identifier (e.g., "JAVA-001")
- title: Brief issue title
- description: Detailed explanation of the vulnerability and its impact
- severity: One of "CRITICAL", "HIGH", "MEDIUM", "LOW"
- line_number: Approximate line number (if identifiable)
- code_snippet: The vulnerable code section
- remediation: Specific fix recommendation with code examples when applicable
- references: Array of relevant references (OWASP, CWE, CVE, etc.)

Return ONLY a JSON array of issues. If no issues found, return an empty array [].

Example format:
[
  {
    "id": "JAVA-001",
    "title": "SQL Injection via String Concatenation",
    "description": "SQL query is constructed using string concatenation with user input, allowing SQL injection attacks",
    "severity": "CRITICAL",
    "line_number": 42,
    "code_snippet": "String sql = \"SELECT * FROM users WHERE id = '\" + userId + \"'\";",
    "remediation": "Use PreparedStatement with parameterized queries: PreparedStatement ps = conn.prepareStatement(\"SELECT * FROM users WHERE id = ?\"); ps.setString(1, userId);",
    "references": ["OWASP-A03:2021", "CWE-89"]
  }
]
"""

    def preprocess_code(self, code: str) -> str:
        """
        Preprocess Java code before analysis.
        Removes comments while preserving line structure and annotations.
        """
        import re

        # Remove single-line comments but keep line breaks
        code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)

        # Remove multi-line comments but preserve line count
        def replace_multiline_comment(match):
            return "\n" * match.group(0).count("\n")

        code = re.sub(r"/\*.*?\*/", replace_multiline_comment, code, flags=re.DOTALL)

        return code
