from fastapi import APIRouter

from app.core.config import settings
from app.modules.chat.api.v1.endpoints.chat_endpoints import router as chat_router

router = APIRouter()
router.include_router(
    chat_router, prefix=f"{settings.API_V1_PREFIX}/agents", tags=["Chat"]
)
