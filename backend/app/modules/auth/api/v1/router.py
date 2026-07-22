from fastapi import APIRouter

from app.core.config import settings
from app.modules.auth.api.v1.endpoints.auth_endpoints import router as auth_router

router = APIRouter()
router.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Auth"])
