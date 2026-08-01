import os
import time
import asyncio
from typing import Optional

from fastapi import Header, HTTPException


# Read valid API keys from environment variable COPILOT_API_KEYS (comma-separated)
_raw = os.environ.get("COPILOT_API_KEYS", "")
_VALID_API_KEYS = set([k.strip() for k in _raw.split(",") if k.strip()])

# Configurable rate limit
_DEFAULT_CALLS_PER_MINUTE = int(os.environ.get("COPILOT_RATE_LIMIT_PER_MINUTE", "100"))


class RateLimiter:
    """Simple per-key fixed-window rate limiter.

    This is an in-memory limiter suitable for single-process dev/test. If you provide
    REDIS_URL in the environment and want distributed limits, replace this with a Redis implementation.
    """

    def __init__(self, calls_per_minute: int = _DEFAULT_CALLS_PER_MINUTE):
        self.calls_per_minute = calls_per_minute
        self._data: dict[str, list[int]] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        """Return True if the key may proceed, False if rate limited."""
        async with self._lock:
            now = int(time.time())
            window = now // 60
            entry = self._data.get(key)
            if not entry or entry[0] != window:
                # New window
                self._data[key] = [window, 1]
                return True
            if entry[1] < self.calls_per_minute:
                entry[1] += 1
                return True
            return False


# Singleton limiter for the app
_rate_limiter_singleton = RateLimiter()


async def get_rate_limiter() -> RateLimiter:
    return _rate_limiter_singleton


async def get_api_key(authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)) -> str:
    """FastAPI dependency to validate an API key.

    Supports either `Authorization: Bearer <key>` or `x-api-key: <key>` headers.
    """
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    if not token and x_api_key:
        token = x_api_key

    if not token:
        raise HTTPException(status_code=401, detail="Missing API key")

    if _VALID_API_KEYS and token not in _VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # If _VALID_API_KEYS is empty, deny by default to force explicit config
    if not _VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="No API keys configured")

    return token
