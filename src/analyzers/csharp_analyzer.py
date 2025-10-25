from src.models import LanguageType
from .base_analyzer import BaseSecurityAnalyzer


class CSharpSecurityAnalyzer(BaseSecurityAnalyzer):
    """Security analyzer for C# code"""

    def get_language_type(self) -> LanguageType:
        """Return C# language type"""
        return LanguageType.CSHARP

    def get_security_rules_prompt(self) -> str:
        """Return security rules prompt for C# analysis"""
        return """
You are a C# security expert. Analyze the following C# code for security vulnerabilities.

Focus on these security rules:

1. **SQL Injection**: Look for string concatenation or interpolation in SQL queries without parameterization
2. **Command Injection**: Identify use of Process.Start, ProcessStartInfo with user input
3. **Path Traversal**: Check for file operations using user-controlled paths without validation
4. **Insecure Deserialization**: Find BinaryFormatter, NetDataContractSerializer, or other unsafe deserializers
5. **Weak Cryptography**: Detect use of MD5, SHA1, DES, RC2 for sensitive operations
6. **Hardcoded Secrets**: Find hardcoded passwords, API keys, connection strings, or tokens
7. **Insecure Random**: Identify use of System.Random for security-sensitive operations
8. **XML External Entity (XXE)**: Check for unsafe XML parsing configurations
9. **LDAP Injection**: Look for LDAP queries built with string concatenation
10. **Cross-Site Scripting (XSS)**: Find unencoded user input in web responses
11. **Insecure Direct Object Reference**: Check for authorization bypass opportunities
12. **Mass Assignment**: Identify model binding without property filtering
13. **Insufficient Input Validation**: Look for missing input validation on user data
14. **Authentication Bypass**: Find weak authentication or authorization checks
15. **Insecure SSL/TLS**: Detect disabled certificate validation or weak protocols
16. **Race Conditions**: Identify TOCTOU issues in file operations
17. **Information Disclosure**: Find stack traces or sensitive data in error messages
18. **Insecure Cookie Configuration**: Check for missing HttpOnly, Secure, SameSite flags
19. **Open Redirect**: Look for unvalidated redirect destinations
20. **Regular Expression DoS (ReDoS)**: Identify complex regex patterns on user input

For each issue found, provide:
- id: Unique identifier (e.g., "CSHARP-001")
- title: Brief issue title
- description: Detailed explanation of the vulnerability
- severity: One of "CRITICAL", "HIGH", "MEDIUM", "LOW"
- line_number: Approximate line number (if identifiable)
- code_snippet: The vulnerable code
- remediation: Specific fix recommendation
- references: Array of relevant references (OWASP, CWE, etc.)

Return ONLY a JSON array of issues. If no issues found, return an empty array [].
"""
