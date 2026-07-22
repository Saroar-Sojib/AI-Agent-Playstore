from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.modules.users.models.user import User
from app.modules.users.schemas.user_response import UserResponse
from app.modules.users.services.user_service import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's own profile."""
    return current_user


@router.delete("/me")
async def delete_me(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Deactivate the authenticated user's own account (soft-delete)."""
    await service.delete_user(current_user.id)
    return {"detail": "Account deactivated"}
