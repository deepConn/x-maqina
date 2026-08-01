"""Gemini API streaming response handling with advanced features"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any, Callable

import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class StreamChunk:
    """Represents a single chunk from Gemini streaming response"""

    def __init__(self, chunk_data: Dict[str, Any]):
        self.raw = chunk_data
        self.text = self._extract_text()
        self.finish_reason = self._extract_finish_reason()
        self.safety_ratings = self._extract_safety_ratings()

    def _extract_text(self) -> str:
        """Extract text content from chunk"""
        try:
            candidates = self.raw.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        except (KeyError, IndexError, TypeError):
            pass
        return ""

    def _extract_finish_reason(self) -> Optional[str]:
        """Extract finish reason from chunk"""
        try:
            candidates = self.raw.get("candidates", [])
            if candidates:
                return candidates[0].get("finishReason")
        except (KeyError, IndexError, TypeError):
            pass
        return None

    def _extract_safety_ratings(self) -> list:
        """Extract safety ratings from chunk"""
        try:
            candidates = self.raw.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                return content.get("safetyRatings", [])
        except (KeyError, IndexError, TypeError):
            pass
        return []

    def is_complete(self) -> bool:
        """Check if stream is complete"""
        return self.finish_reason is not None

    def has_safety_issues(self) -> bool:
        """Check if response has safety issues"""
        for rating in self.safety_ratings:
            if rating.get("probability") in ["HIGH", "VERY_HIGH"]:
                return True
        return False

    def __repr__(self) -> str:
        return f"StreamChunk(text={len(self.text)}chars, finish_reason={self.finish_reason})"


class StreamBuffer:
    """Buffer for accumulating streamed content with backpressure handling"""

    def __init__(self, max_size: int = 1024 * 1024):  # 1MB default
        self.max_size = max_size
        self.content = ""
        self.chunks = []

    def add(self, text: str) -> None:
        """Add text to buffer"""
        self.content += text
        if len(self.content) > self.max_size:
            raise OverflowError(f"Stream buffer exceeded max size: {self.max_size}")

    def add_chunk(self, chunk: StreamChunk) -> None:
        """Add chunk to buffer"""
        self.chunks.append(chunk)
        self.add(chunk.text)

    def get_content(self) -> str:
        """Get accumulated content"""
        return self.content

    def get_chunks(self) -> list:
        """Get all chunks"""
        return self.chunks

    def reset(self) -> None:
        """Reset buffer"""
        self.content = ""
        self.chunks = []


class GeminiStreamClient:
    """Advanced streaming client for Gemini API"""

    def __init__(self):
        """Initialize streaming client"""
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.endpoint = settings.gemini_endpoint
        self.timeout = aiohttp.ClientTimeout(total=settings.gemini_stream_timeout)

    async def stream_generate(
        self,
        prompt: str,
        on_chunk: Optional[Callable[[StreamChunk], None]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> StreamBuffer:
        """Stream content generation with callbacks

        Args:
            prompt: The input prompt
            on_chunk: Optional callback for each chunk
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Additional parameters

        Returns:
            StreamBuffer with accumulated content
        """
        buffer = StreamBuffer()
        temperature = temperature or settings.gemini_temperature
        max_tokens = max_tokens or settings.gemini_max_tokens

        logger.info(f"Starting stream with model: {self.model}")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.endpoint}/{self.model}:streamGenerateContent?key={self.api_key}"

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": temperature,
                    },
                }
                payload.update(kwargs)

                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Gemini API error: {response.status} - {error_text}")
                        raise RuntimeError(f"API error: {response.status}")

                    async for line in response.content:
                        if not line:
                            continue

                        try:
                            chunk_data = json.loads(line.decode("utf-8"))
                            chunk = StreamChunk(chunk_data)

                            if chunk.has_safety_issues():
                                logger.warning(f"Safety issue detected: {chunk.safety_ratings}")

                            buffer.add_chunk(chunk)

                            if on_chunk:
                                on_chunk(chunk)

                            logger.debug(f"Received: {chunk}")

                            if chunk.is_complete():
                                logger.info("Stream completed")
                                break

                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse chunk: {e}")
                            continue

        except asyncio.TimeoutError:
            logger.error("Stream timeout")
            raise
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            raise

        return buffer

    async def stream_generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        on_chunk: Optional[Callable[[StreamChunk], None]] = None,
        **kwargs
    ) -> StreamBuffer:
        """Stream with exponential backoff retry logic

        Args:
            prompt: The input prompt
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff factor
            on_chunk: Optional callback for each chunk
            **kwargs: Additional parameters

        Returns:
            StreamBuffer with accumulated content
        """
        for attempt in range(max_retries):
            try:
                return await self.stream_generate(prompt, on_chunk=on_chunk, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Stream failed after {max_retries} attempts")
                    raise

                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Stream attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}"
                )
                await asyncio.sleep(wait_time)

    async def stream_generate_async_generator(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream as async generator for real-time processing

        Args:
            prompt: The input prompt
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Additional parameters

        Yields:
            StreamChunk objects as they arrive
        """
        temperature = temperature or settings.gemini_temperature
        max_tokens = max_tokens or settings.gemini_max_tokens

        logger.info(f"Starting async generator stream with model: {self.model}")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.endpoint}/{self.model}:streamGenerateContent?key={self.api_key}"

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": temperature,
                    },
                }
                payload.update(kwargs)

                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Gemini API error: {response.status} - {error_text}")
                        raise RuntimeError(f"API error: {response.status}")

                    async for line in response.content:
                        if not line:
                            continue

                        try:
                            chunk_data = json.loads(line.decode("utf-8"))
                            chunk = StreamChunk(chunk_data)

                            if chunk.has_safety_issues():
                                logger.warning(f"Safety issue detected: {chunk.safety_ratings}")

                            yield chunk

                            if chunk.is_complete():
                                logger.info("Async stream completed")
                                break

                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse chunk: {e}")
                            continue

        except Exception as e:
            logger.error(f"Async stream error: {str(e)}")
            raise


class StreamAggregator:
    """Aggregates multiple streams for parallel processing"""

    def __init__(self):
        self.streams = {}
        self.client = GeminiStreamClient()

    async def parallel_streams(
        self,
        prompts: Dict[str, str],
        **kwargs
    ) -> Dict[str, StreamBuffer]:
        """Process multiple prompts in parallel

        Args:
            prompts: Dictionary of {name: prompt}
            **kwargs: Additional parameters

        Returns:
            Dictionary of {name: StreamBuffer}
        """
        tasks = {
            name: self.client.stream_generate(prompt, **kwargs)
            for name, prompt in prompts.items()
        }

        results = await asyncio.gather(*tasks.values())
        return dict(zip(tasks.keys(), results))
