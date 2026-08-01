"""Copilot service wrapper for assembling prompts, invoking Gemini client, and enforcing safety checks."""
from typing import Any, AsyncIterator, Dict, List, Optional

from app.gemini.advanced_prompts import PromptEngineer
from app.gemini.safety import SafetyFilter


class CopilotService:
    """Service to run Copilot queries against a Gemini-like client.

    The service expects a client with the following interface:
    - async def generate(prompt: str, max_tokens: int | None = None, **kwargs) -> Dict[str, Any]
      returns {"text": str, "safety_ratings": List[Dict[str, Any]]}

    - async def stream_generate(prompt: str, **kwargs) -> AsyncIterator[str]
      yields text chunks (str). The final chunk may be the full text or a marker.
    """

    def __init__(self, gemini_client: Any, blocking_mode: str = "high"):
        self.client = gemini_client
        self.blocking_mode = blocking_mode
        self.safety_settings = SafetyFilter.get_safety_settings(blocking_mode=blocking_mode)

    async def query(self, prompt: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        # Sanitize and truncate prompt
        prompt = SafetyFilter.filter_content(prompt, max_length=8000, strip_urls=False)

        # Call client
        result = await self.client.generate(prompt=prompt, max_tokens=max_tokens or 512, safety_settings=self.safety_settings)

        text = result.get("text", "")
        safety_ratings = result.get("safety_ratings", [])

        # Check safety
        is_safe, issues = SafetyFilter.check_safety_ratings(safety_ratings, allow_medium=False)
        if not is_safe:
            # Log issues and return a safe error
            SafetyFilter.log_safety_issues([str(i) for i in issues], severity="ERROR")
            return {"ok": False, "error": "Response blocked by safety policy", "safety_issues": issues}

        return {"ok": True, "response": text, "safety_issues": issues}

    async def stream(self, prompt: str, max_tokens: Optional[int] = None) -> AsyncIterator[str]:
        """Stream text chunks from the client. Each yielded value is a text chunk.

        Safety is checked at the end when the client returns final safety metadata (if available).
        For clients that stream safety ratings separately, consider adapting this method.
        """
        prompt = SafetyFilter.filter_content(prompt, max_length=8000, strip_urls=False)

        async for chunk in self.client.stream_generate(prompt=prompt, max_tokens=max_tokens or 512, safety_settings=self.safety_settings):
            # Yield raw chunks to the caller (the HTTP layer will decide framing)
            yield chunk

        # If the client provides a final safety report, the client implementation should handle it.
