from fastapi import APIRouter

from app.core.config import settings
from app.modules.agents.api.v1.endpoints.agent_endpoints import (
    router as agent_router,
)

router = APIRouter()
router.include_router(
    agent_router, prefix=f"{settings.API_V1_PREFIX}/agents", tags=["Agents"]
)
