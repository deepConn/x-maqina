"""Data models for Gemini API interactions"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class GeminiRequest(BaseModel):
    """Request model for Gemini API"""
    prompt: str = Field(..., description="Input prompt")
    model: Optional[str] = Field(None, description="Model to use")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Temperature")
    max_tokens: Optional[int] = Field(4096, ge=1, description="Max output tokens")
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0, description="Top-p (nucleus) sampling")
    top_k: Optional[int] = Field(None, ge=1, description="Top-k sampling")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")


class SafetyRatingModel(BaseModel):
    """Safety rating for content"""
    category: str
    probability: str


class ContentPart(BaseModel):
    """Single part of content"""
    text: Optional[str] = None


class ContentModel(BaseModel):
    """Content with parts and safety ratings"""
    parts: List[ContentPart] = []
    role: Optional[str] = None
    safety_ratings: Optional[List[SafetyRatingModel]] = None


class Candidate(BaseModel):
    """Candidate response"""
    content: Optional[ContentModel] = None
    finish_reason: Optional[str] = None
    safety_ratings: Optional[List[SafetyRatingModel]] = None


class GeminiResponse(BaseModel):
    """Response model from Gemini API"""
    candidates: List[Candidate] = []
    usage_metadata: Optional[Dict[str, Any]] = None


class StreamingResponse(BaseModel):
    """Streaming response model"""
    text: str
    finish_reason: Optional[str] = None
    safety_ratings: Optional[List[SafetyRatingModel]] = None
    is_complete: bool = False


class CachedPromptResponse(BaseModel):
    """Response for cached prompt"""
    prompt: str
    response: str
    model: str
    cached: bool = True
    cache_key: Optional[str] = None


class PromptAnalysis(BaseModel):
    """Analysis of prompt quality"""
    prompt: str
    tokens_estimated: int
    complexity_score: float  # 0-1
    clarity_score: float  # 0-1
    suggestions: List[str] = []


class MultiAgentResponse(BaseModel):
    """Response from multi-agent reasoning"""
    problem: str
    num_agents: int
    solution: str
    confidence: float
    reasoning_steps: List[str] = []
    agent_perspectives: Dict[str, str] = {}
