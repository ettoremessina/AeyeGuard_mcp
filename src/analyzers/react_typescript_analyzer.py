from src.models import LanguageType
from .base_analyzer import BaseSecurityAnalyzer


class ReactTypeScriptAnalyzer(BaseSecurityAnalyzer):
    """Security analyzer for React TypeScript code"""

    def get_language_type(self) -> LanguageType:
        """Return React TypeScript language type"""
        return LanguageType.REACT_TYPESCRIPT

    def get_security_rules_prompt(self) -> str:
        """Return security rules prompt for React TypeScript analysis"""
        return """
You are a React TypeScript security expert. Analyze the following React TypeScript code for security vulnerabilities.

Focus on these security rules:

1. **Cross-Site Scripting (XSS)**:
   - Unsafe use of dangerouslySetInnerHTML
   - Unescaped user input in JSX
   - Improper sanitization before rendering

2. **Insecure State Management**:
   - Storing sensitive data (tokens, passwords) in component state
   - Exposing secrets in Redux store or Context
   - Client-side storage of sensitive information

3. **Props Validation Issues**:
   - Missing TypeScript types for security-critical props
   - Improper validation of user-controlled props
   - Type assertions that bypass safety checks (as, any)

4. **API Security Issues**:
   - Hardcoded API keys or secrets
   - Unvalidated API responses
   - Missing error handling exposing sensitive info
   - CORS misconfigurations

5. **Authentication & Authorization**:
   - Client-side only authentication checks
   - Insecure token storage (localStorage without encryption)
   - Missing token expiration checks
   - Exposed authentication logic

6. **Data Exposure**:
   - Console.log with sensitive data
   - Error messages revealing internal details
   - Source maps in production exposing code

7. **Unsafe Dependencies**:
   - Use of eval() or Function() constructor
   - Dynamic code execution
   - Unsafe third-party component usage

8. **Type Safety Issues**:
   - Excessive use of 'any' type
   - Missing type guards for external data
   - Unsafe type assertions

9. **Route Security**:
   - Missing route guards for protected pages
   - Client-side only authorization
   - Unprotected sensitive routes

10. **Input Validation**:
    - Missing sanitization of form inputs
    - Improper validation before API calls
    - Lack of input length/format restrictions

For each issue found, provide:
- id: Unique identifier (e.g., "REACT-TS-001")
- title: Brief issue title
- description: Detailed explanation of the vulnerability
- severity: One of "CRITICAL", "HIGH", "MEDIUM", "LOW"
- line_number: Approximate line number (if identifiable)
- code_snippet: The vulnerable code
- remediation: Specific fix recommendation with TypeScript examples
- references: Array of relevant references (OWASP, React docs, etc.)

Return ONLY a JSON array of issues. If no issues found, return an empty array [].
"""
