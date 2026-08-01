from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, AsyncGenerator, Dict
from fastapi.responses import StreamingResponse

from app.gemini.copilot import CopilotService
from app.gemini.advanced_prompts import PromptEngineer

router = APIRouter()


class QueryRequest(BaseModel):
    mode: str
    data: Dict[str, Any]
    use_cot: bool = True


class StreamRequest(BaseModel):
    mode: str
    data: Dict[str, Any]
    use_cot: bool = True


# Lightweight default mock Gemini client used for MVP when no real client is wired.
class _MockGeminiClient:
    async def generate(self, prompt: str, max_tokens: int = 512, **kwargs) -> Dict[str, Any]:
        # Return a deterministic mocked response and empty safety ratings
        return {"text": f"[mocked response] Received prompt length={len(prompt)}", "safety_ratings": []}

    async def stream_generate(self, prompt: str, max_tokens: int = 512, **kwargs) -> AsyncGenerator[str, None]:
        # Yield a few chunks and finish
        chunks = ["[mock stream] Starting...", "[mock stream] processing...", f"[mock stream] done (len={len(prompt)})"]
        for c in chunks:
            yield c


# Dependency provider for CopilotService. In a production deployment, replace the mock client
# with a real Gemini client adapter and register the dependency accordingly.
def get_copilot_service() -> CopilotService:
    client = _MockGeminiClient()
    return CopilotService(gemini_client=client, blocking_mode="high")


@router.post("/query")
async def copilot_query(req: QueryRequest, svc: CopilotService = Depends(get_copilot_service)):
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
async def copilot_stream(req: StreamRequest, svc: CopilotService = Depends(get_copilot_service)):
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
