from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user_id, security, decode_token
from app.core.token_denylist import assert_not_revoked, get_redis
from app.core.user_context import current_agent_id, current_user_id
from app.infrastructure.database import get_db
from app.modules.users.models.user import User


async def set_user_context(
    user_id: int | None = Depends(get_current_user_id),
):
    """App-wide dependency: make sure ``current_user_id`` is populated.

    Usually a no-op — ``AgentMiddleware`` already set it from the bearer
    token before any route dependency runs. Kept as a light safety net for
    request paths the middleware might not cover.
    """
    if user_id is not None:
        current_user_id.set(user_id)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require an authenticated, active user. Returns the loaded ``User`` row.

    Use this in place of the deleted ``require_permission(...)`` — AgentHub
    has no fine-grained permissions, just "does this user belong to this
    agent". Endpoints that need agent-scoped access should compare
    ``user.agent_id`` against the resource being acted on.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    payload = decode_token(credentials.credentials)
    await assert_not_revoked(get_redis(request), payload)

    uid = payload.get("uid")
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token"
        )

    result = await db.execute(
        select(User).where(User.id == int(uid), User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )

    current_user_id.set(user.id)
    current_agent_id.set(user.agent_id)
    return user
