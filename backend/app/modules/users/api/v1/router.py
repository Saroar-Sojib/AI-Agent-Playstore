from fastapi import APIRouter
from app.modules.users.api.v1.endpoints.user_endpoints import router as user_router
from app.core.config import settings
router = APIRouter()
router.include_router(user_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
