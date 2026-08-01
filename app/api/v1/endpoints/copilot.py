from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, AsyncGenerator, Dict
from fastapi.responses import StreamingResponse

from app.gemini.copilot import CopilotService
from app.gemini.advanced_prompts import PromptEngineer
from app.api.auth import get_api_key, get_rate_limiter

router = APIRouter()


class QueryRequest(BaseModel):
    mode: str
    data: Dict[str, Any]
    use_cot: bool = True


class StreamRequest(BaseModel):
    mode: str
    data: Dict[str, Any]
    use_cot: bool = True


# Dependency provider for CopilotService. In production we wire the real Gemini adapter.
from app.gemini.adapter import GeminiClientAdapter


def get_copilot_service() -> CopilotService:
    try:
        client = GeminiClientAdapter()
    except Exception:
        from .copilot import _MockGeminiClient as _LocalMock

        client = _LocalMock()

    return CopilotService(gemini_client=client, blocking_mode="high")


@router.post("/query")
async def copilot_query(
    req: QueryRequest,
    svc: CopilotService = Depends(get_copilot_service),
    api_key: str = Depends(get_api_key),
    rate_limiter=Depends(get_rate_limiter),
):
    # Rate limit check
    allowed = await rate_limiter.is_allowed(api_key)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Build prompt based on mode
    mode = req.mode.lower()
    if mode == "market":
        prompt = PromptEngineer.get_market_analysis_prompt(req.data, timeframe=req.data.get("timeframe", "1h"), use_cot=req.use_cot)
    elif mode == "threat":
        threat = req.data.get("threat_data", str(req.data))
        prompt = PromptEngineer.get_threat_analysis_prompt(threat_data=threat, context=req.data.get("context", "general"), urgency=req.data.get("urgency", "medium"), use_cot=req.use_cot)
    else:
        prompt = str(req.data)

    result = await svc.query(prompt=prompt)
    if not result.get("ok"):
        raise HTTPException(status_code=403, detail=result.get("error", "blocked"))
    return {"result": result.get("response"), "safety_issues": result.get("safety_issues", [])}


@router.post("/stream")
async def copilot_stream(
    req: StreamRequest,
    svc: CopilotService = Depends(get_copilot_service),
    api_key: str = Depends(get_api_key),
    rate_limiter=Depends(get_rate_limiter),
):
    allowed = await rate_limiter.is_allowed(api_key)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    mode = req.mode.lower()
    if mode == "market":
        prompt = PromptEngineer.get_market_analysis_prompt(req.data, timeframe=req.data.get("timeframe", "1h"), use_cot=req.use_cot)
    elif mode == "threat":
        threat = req.data.get("threat_data", str(req.data))
        prompt = PromptEngineer.get_threat_analysis_prompt(threat_data=threat, context=req.data.get("context", "general"), urgency=req.data.get("urgency", "medium"), use_cot=req.use_cot)
    else:
        prompt = str(req.data)

    async def event_stream():
        async for chunk in svc.stream(prompt=prompt):
            # Server-Sent Events framing
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
