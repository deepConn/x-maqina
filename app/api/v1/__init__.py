"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1.endpoints import autonomous, diagnostics, financial, security, agents

router = APIRouter()

# Include domain-specific routers
router.include_router(security.router, prefix="/security", tags=["Security"])
router.include_router(financial.router, prefix="/financial", tags=["Financial"])
router.include_router(diagnostics.router, prefix="/diagnostics", tags=["Diagnostics"])
router.include_router(agents.router, prefix="/agents", tags=["Multi-Agent"])
router.include_router(autonomous.router, prefix="/autonomous", tags=["Autonomous"])
