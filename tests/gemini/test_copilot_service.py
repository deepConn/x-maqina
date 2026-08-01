import asyncio

import pytest

from app.gemini.copilot import CopilotService


class _SimpleMockClient:
    async def generate(self, prompt: str, max_tokens: int = 512, **kwargs):
        return {"text": "mock response", "safety_ratings": []}

    async def stream_generate(self, prompt: str, max_tokens: int = 512, **kwargs):
        for p in ["a", "b", "c"]:
            yield p


@pytest.mark.asyncio
async def test_copilot_service_query():
    client = _SimpleMockClient()
    svc = CopilotService(gemini_client=client, blocking_mode="high")
    res = await svc.query("test prompt")
    assert res["ok"] is True
    assert res["response"] == "mock response"


@pytest.mark.asyncio
async def test_copilot_service_stream():
    client = _SimpleMockClient()
    svc = CopilotService(gemini_client=client, blocking_mode="high")
    chunks = []
    async for c in svc.stream("hello"):
        chunks.append(c)
    assert chunks == ["a", "b", "c"]
