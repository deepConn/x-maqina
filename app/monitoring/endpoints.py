"""Prometheus metrics endpoints for FastAPI"""

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST

from app.monitoring.metrics import metrics

router = APIRouter(tags=["Monitoring"])


@router.get("/metrics", response_class=Response)
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=metrics.get_metrics(),
        media_type=CONTENT_TYPE_LATEST,
    )
