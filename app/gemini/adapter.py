"""Adapter for Google Gemini using the official google.generativeai SDK.

This adapter provides a small async-friendly wrapper exposing two methods used by CopilotService:
- async def generate(prompt: str, max_tokens: int | None = None, **kwargs) -> Dict[str, Any]
- async def stream_generate(prompt: str, max_tokens: int | None = None, **kwargs) -> AsyncIterator[str]

Notes:
- The SDK is typically synchronous; we offload blocking calls to a thread via asyncio.to_thread.
- Configure credentials via the GEMINI_API_KEY environment variable.
- Configure model via GEMINI_MODEL env var (fallback to "gemini-2.0-flash").
- If the SDK cannot be imported, initialization will raise an informative error.
"""
import os
import asyncio
from typing import Any, AsyncIterator, Dict, Optional


class GeminiClientAdapter:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Lazy import to avoid import-time failures in test environments
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as e:
            raise ImportError(
                "google.generativeai SDK is required for the Gemini adapter. "
                "Install with `pip install google-generative-ai` or provide a mock client.`"
            ) from e

        self._genai = genai

        # Read configuration from env if not provided
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment")

        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

        # Configure SDK
        # The google.generativeai library typically uses `configure` or `client` to set the API key.
        # We attempt to call common config methods; if they don't exist, rely on environment variables.
        try:
            if hasattr(self._genai, "configure"):
                self._genai.configure(api_key=self.api_key)
            elif hasattr(self._genai, "Client"):
                # Some SDK variants instantiate a client
                self._client = self._genai.Client(api_key=self.api_key)
            else:
                # As a last resort, set the environment variable for underlying HTTP client
                os.environ["GEMINI_API_KEY"] = self.api_key
        except Exception:
            # Ignore configuration errors here; calls will surface errors later.
            pass

    async def generate(self, prompt: str, max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Generate a single response from Gemini.

        Returns a dict with keys:
        - text: str
        - safety_ratings: list (if available)
        """
        # Most SDK calls are blocking; run in thread
        return await asyncio.to_thread(self._sync_generate, prompt, max_tokens, kwargs)

    def _sync_generate(self, prompt: str, max_tokens: Optional[int], extra_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        # Prepare parameters compatible with the google.generativeai SDK
        params = {"model": self.model, "prompt": prompt}
        if max_tokens:
            # SDK parameter name may differ; commonly `max_output_tokens` or `max_tokens`
            params["max_output_tokens"] = max_tokens

        # Merge extra kwargs (e.g., safety_settings)
        params.update(extra_kwargs or {})

        # Try common SDK interfaces
        # 1) google.generativeai.generate_text
        try:
            if hasattr(self._genai, "generate_text"):
                resp = self._genai.generate_text(**params)
                # Response parsing depends on SDK; try common shapes
                text = ""
                if isinstance(resp, dict):
                    # e.g., {'candidates': [{'content': '...'}], 'safety': ...}
                    candidates = resp.get("candidates") or []
                    if candidates and isinstance(candidates, list):
                        text = "\n".join([c.get("content", "") for c in candidates if isinstance(c, dict)])
                    else:
                        text = resp.get("content") or resp.get("text") or ""
                    safety = resp.get("safety") or resp.get("safety_ratings") or []
                else:
                    # Fallback: try to stringify
                    text = str(resp)
                    safety = []

                return {"text": text, "safety_ratings": safety}

            # 2) client.generate or client.chat
            if hasattr(self, "_client"):
                client = getattr(self, "_client")
                if hasattr(client, "generate"):
                    resp = client.generate(**params)
                    # Attempt parse
                    text = getattr(resp, "text", str(resp))
                    safety = getattr(resp, "safety", [])
                    return {"text": text, "safety_ratings": safety}

        except Exception as e:
            # Normalize SDK errors
            return {"text": "", "safety_ratings": [], "error": str(e)}

        # If we reached here, we couldn't call the SDK as expected
        return {"text": "", "safety_ratings": [], "error": "Unsupported SDK interface"}

    async def stream_generate(self, prompt: str, max_tokens: Optional[int] = None, **kwargs) -> AsyncIterator[str]:
        """Stream generation. Yields text chunks as they arrive.

        If the SDK supports streaming, use that; otherwise, call generate and yield the final text.
        """
        # Try to use a streaming interface if available
        if hasattr(self._genai, "stream"):
            # Example: genai.stream(model=..., prompt=...)
            # We run streaming in a thread and iterate
            queue = asyncio.Queue()

            def _run_stream():
                try:
                    for event in self._genai.stream(model=self.model, prompt=prompt, **(kwargs or {})):
                        # event may be text or dict
                        if isinstance(event, str):
                            asyncio.run(queue.put(event))
                        elif isinstance(event, dict):
                            text = event.get("text") or event.get("content") or str(event)
                            asyncio.run(queue.put(text))
                except Exception as e:
                    asyncio.run(queue.put(f"[stream-error] {e}"))
                finally:
                    asyncio.run(queue.put(None))

            loop = asyncio.get_event_loop()
            # Start stream in executor
            await asyncio.get_running_loop().run_in_executor(None, _run_stream)

            # Drain queue
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item

        else:
            # Fallback: call generate once and yield the full text
            res = await self.generate(prompt=prompt, max_tokens=max_tokens, **kwargs)
            text = res.get("text", "")
            # Simple chunking to simulate streaming
            for i in range(0, len(text), 512):
                yield text[i : i + 512]
