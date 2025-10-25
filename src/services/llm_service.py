import os
import json
import httpx
from typing import Optional, Dict, Any
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class LLMService:
    """Service for interacting with LMStudio LLM"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM service with LMStudio configuration.

        Args:
            base_url: LMStudio server URL
            model: Model name to use
            api_key: Optional API key for authentication
        """
        self.base_url = base_url or os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
        self.model = model or os.getenv("LMSTUDIO_MODEL", "qwen/qwen3-coder-30b")
        self.api_key = api_key or os.getenv("LMSTUDIO_API_KEY", "")

        # Remove trailing slash from base_url
        self.base_url = self.base_url.rstrip("/")

    async def analyze_code(self, code: str, prompt: str) -> str:
        """
        Analyze code using the LLM with a custom prompt.

        Args:
            code: Source code to analyze
            prompt: Analysis prompt with instructions

        Returns:
            LLM response as string
        """
        full_prompt = f"{prompt}\n\nCode to analyze:\n```\n{code}\n```\n\nProvide your analysis as a JSON array of security issues."

        try:
            # Use LMStudio's OpenAI-compatible API
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a security code analysis expert. Analyze code for security vulnerabilities and return results as structured JSON.",
                            },
                            {"role": "user", "content": full_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000,
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            raise Exception(f"LLM analysis failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if LLM service is available and healthy.

        Returns:
            Dictionary with health status information
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()

                models = response.json()
                return {
                    "status": "healthy",
                    "available": True,
                    "models": models.get("data", []),
                    "base_url": self.base_url,
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e),
                "base_url": self.base_url,
            }

    def parse_llm_response(self, response: str) -> list[Dict[str, Any]]:
        """
        Parse LLM response to extract security issues.

        Args:
            response: Raw LLM response

        Returns:
            List of issue dictionaries
        """
        try:
            # Try to find JSON in the response
            # LLMs often wrap JSON in code blocks
            json_start = response.find("[")
            json_end = response.rfind("]") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                issues = json.loads(json_str)
                return issues if isinstance(issues, list) else []

            # If no array found, try to parse entire response
            issues = json.loads(response)
            return issues if isinstance(issues, list) else []

        except json.JSONDecodeError:
            # If parsing fails, return empty list
            return []
