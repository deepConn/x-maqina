"""Gemini API client for REST-based interactions"""

import logging
from typing import Optional, Any

import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Async Gemini API client"""

    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.endpoint = settings.gemini_endpoint
        self.timeout = aiohttp.ClientTimeout(total=settings.gemini_stream_timeout)

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Gemini API"""
        logger.info(f"Generating content with {self.model}")
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.endpoint}/{self.model}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": settings.gemini_max_tokens,
                        "temperature": settings.gemini_temperature,
                    },
                }
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    else:
                        logger.error(f"Gemini API error: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return ""

    async def stream_content(self, prompt: str, **kwargs) -> Any:
        """Stream content from Gemini API"""
        logger.info(f"Streaming content from {self.model}")
        # TODO: Implement streaming
        pass
