from src.models import LanguageType
from .base_analyzer import BaseSecurityAnalyzer


class ReactJavaScriptAnalyzer(BaseSecurityAnalyzer):
    """Security analyzer for React JavaScript code"""

    def get_language_type(self) -> LanguageType:
        """Return React JavaScript language type"""
        return LanguageType.REACT_JAVASCRIPT

    def get_security_rules_prompt(self) -> str:
        """Return security rules prompt for React JavaScript analysis"""
        return """
You are a React JavaScript security expert. Analyze the following React JavaScript code for security vulnerabilities.

Focus on these security rules:

1. **Cross-Site Scripting (XSS)**:
   - Unsafe use of dangerouslySetInnerHTML
   - Unescaped user input in JSX
   - Improper sanitization before rendering
   - Direct DOM manipulation with user data

2. **Insecure State Management**:
   - Storing sensitive data (tokens, passwords) in component state
   - Exposing secrets in Redux store or Context
   - Client-side storage of sensitive information (localStorage)

3. **Props Validation Issues**:
   - Missing PropTypes validation
   - Improper validation of user-controlled props
   - Lack of type checking on security-critical data

4. **API Security Issues**:
   - Hardcoded API keys or secrets in code
   - Unvalidated API responses
   - Missing error handling exposing sensitive info
   - CORS misconfigurations
   - Insecure HTTP instead of HTTPS

5. **Authentication & Authorization**:
   - Client-side only authentication checks
   - Insecure token storage
   - Missing token expiration checks
   - Exposed authentication logic in client code

6. **Data Exposure**:
   - Console.log with sensitive data in production
   - Error messages revealing internal details
   - Comments containing secrets or sensitive info

7. **Unsafe Code Execution**:
   - Use of eval() or Function() constructor
   - Dynamic code execution from user input
   - Unsafe innerHTML assignments

8. **Input Validation**:
   - Missing sanitization of form inputs
   - Improper validation before API calls
   - Lack of input length/format restrictions
   - No protection against injection attacks

9. **Route Security**:
   - Missing route guards for protected pages
   - Client-side only authorization
   - Unprotected sensitive routes

10. **Third-Party Dependencies**:
    - Use of outdated or vulnerable packages
    - Unsafe third-party component integration
    - Missing Content Security Policy

For each issue found, provide:
- id: Unique identifier (e.g., "REACT-JS-001")
- title: Brief issue title
- description: Detailed explanation of the vulnerability
- severity: One of "CRITICAL", "HIGH", "MEDIUM", "LOW"
- line_number: Approximate line number (if identifiable)
- code_snippet: The vulnerable code
- remediation: Specific fix recommendation with JavaScript examples
- references: Array of relevant references (OWASP, React docs, etc.)

Return ONLY a JSON array of issues. If no issues found, return an empty array [].
"""
