"""Gemini API response caching with Redis backend"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any

import redis
from redis.asyncio import Redis as AsyncRedis

from app.config import settings

logger = logging.getLogger(__name__)


class PromptCache:
    """Caching layer for Gemini API prompts and responses"""

    def __init__(self):
        """Initialize cache"""
        self.redis_url = settings.redis_url
        self.ttl = settings.redis_cache_ttl
        self.client = None

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.client = await AsyncRedis.from_url(self.redis_url)
            await self.client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()

    def _generate_key(self, prompt: str, model: str = "") -> str:
        """Generate cache key from prompt"""
        model = model or settings.gemini_model
        combined = f"{model}:{prompt}"
        return f"gemini:cache:{hashlib.sha256(combined.encode()).hexdigest()}"

    async def get(self, prompt: str, model: str = "") -> Optional[Dict[str, Any]]:
        """Retrieve cached response"""
        if not self.client:
            return None

        try:
            key = self._generate_key(prompt, model)
            cached = await self.client.get(key)

            if cached:
                logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
                return json.loads(cached)
            else:
                logger.debug(f"Cache miss for prompt: {prompt[:50]}...")
                return None
        except Exception as e:
            logger.warning(f"Cache retrieval error: {str(e)}")
            return None

    async def set(
        self,
        prompt: str,
        response: Dict[str, Any],
        model: str = "",
        ttl: Optional[int] = None,
    ) -> bool:
        """Cache response"""
        if not self.client:
            return False

        try:
            key = self._generate_key(prompt, model)
            ttl = ttl or self.ttl
            await self.client.setex(
                key, ttl, json.dumps(response)
            )
            logger.debug(f"Cached response for prompt: {prompt[:50]}...")
            return True
        except Exception as e:
            logger.warning(f"Cache write error: {str(e)}")
            return False

    async def delete(self, prompt: str, model: str = "") -> bool:
        """Delete cached response"""
        if not self.client:
            return False

        try:
            key = self._generate_key(prompt, model)
            await self.client.delete(key)
            logger.debug(f"Deleted cache for prompt: {prompt[:50]}...")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {str(e)}")
            return False

    async def clear_all(self) -> bool:
        """Clear all Gemini cache entries"""
        if not self.client:
            return False

        try:
            pattern = "gemini:cache:*"
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {str(e)}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.client:
            return {}

        try:
            pattern = "gemini:cache:*"
            keys = await self.client.keys(pattern)
            info = await self.client.info("stats")
            return {
                "cached_prompts": len(keys),
                "redis_hits": info.get("keyspace_hits", 0),
                "redis_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {str(e)}")
            return {}


# Global cache instance
prompt_cache = PromptCache()
