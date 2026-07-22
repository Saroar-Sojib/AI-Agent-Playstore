from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rate_limit import RateLimit
from app.core.security import (
    decode_token,
    hash_password,
    security,
    verify_password,
)
from app.core.token_denylist import (
    assert_not_revoked,
    get_redis,
    revoke_all_for_user,
    revoke_token,
)
from app.core.tokens import (
    create_access_token,
    create_refresh_token,
)
from app.core.tokens import decode_token as decode_any_token
from app.infrastructure.database import get_db
from app.modules.agents.repositories.agent_repository import AgentRepository
from app.modules.auth.schemas.auth_schemas import (
    ChangePasswordRequest,
    CurrentUserResponse,
    LoginRequest,
    SignupRequest,
    TokenBundle,
)
from app.modules.users.models.user import User
from app.modules.users.repositories.user_repository import UserRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Cookie helpers
# ---------------------------------------------------------------------------


def _cookie_secure() -> bool:
    return not settings.DEBUG


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_COOKIE_MAX_AGE,
        path=settings.REFRESH_COOKIE_PATH,
        domain=settings.REFRESH_COOKIE_DOMAIN or None,
        secure=_cookie_secure(),
        httponly=True,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        domain=settings.REFRESH_COOKIE_DOMAIN or None,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _resolve_agent_id(agent_slug: str, db: AsyncSession) -> int:
    agent = await AgentRepository(db).get_by_slug(agent_slug)
    if agent is None:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_slug}' not found"
        )
    return agent.id


def _issue_token_response(user: User, status_code: int = 200) -> JSONResponse:
    access_token, expires_in = create_access_token(
        uid=user.id,
        email=user.email,
        agent_id=user.agent_id,
    )
    refresh_token = create_refresh_token(
        uid=user.id,
        email=user.email,
        agent_id=user.agent_id,
    )
    body = TokenBundle(access_token=access_token, expires_in=expires_in)
    response = JSONResponse(content=body.model_dump(), status_code=status_code)
    _set_refresh_cookie(response, refresh_token)
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/signup",
    response_model=TokenBundle,
    status_code=201,
    dependencies=[Depends(RateLimit("auth.signup", max_requests=20, window_seconds=60))],
)
async def signup(
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user account scoped to exactly one agent, then log them in."""
    agent_id = await _resolve_agent_id(payload.agent_slug, db)

    repo = UserRepository(db)
    if await repo.exists_by_email(payload.email, agent_id):
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists for this agent",
        )

    user = await repo.create(
        email=payload.email,
        agent_id=agent_id,
        password_hash=hash_password(payload.password),
    )
    return _issue_token_response(user, status_code=201)


@router.post(
    "/login",
    response_model=TokenBundle,
    dependencies=[Depends(RateLimit("auth.login", max_requests=30, window_seconds=60))],
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    agent_id = await _resolve_agent_id(payload.agent_slug, db)

    user = await UserRepository(db).get_by_email(payload.email, agent_id=agent_id)
    if (
        user is None
        or user.deleted_at is not None
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return _issue_token_response(user)


@router.post(
    "/refresh",
    response_model=TokenBundle,
    dependencies=[Depends(RateLimit("auth.refresh", max_requests=60, window_seconds=60))],
)
async def refresh(request: Request):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token cookie present")

    claims = decode_any_token(refresh_token, expected_type="refresh")
    await assert_not_revoked(get_redis(request), claims)
    uid = claims.get("uid")
    email = claims.get("email")
    agent_raw = claims.get("agent_id")
    if uid is None:
        raise HTTPException(status_code=401, detail="Malformed refresh token")
    agent_id = int(agent_raw) if agent_raw not in (None, "") else None

    # Rotation: the presented refresh token is single-use — revoke it so a
    # stolen copy can't be replayed after this exchange.
    await revoke_token(get_redis(request), claims)

    access_token, expires_in = create_access_token(
        uid=int(uid),
        email=email or "",
        agent_id=agent_id,
    )
    new_refresh = create_refresh_token(
        uid=int(uid),
        email=email or "",
        agent_id=agent_id,
    )
    body = TokenBundle(access_token=access_token, expires_in=expires_in)
    response = JSONResponse(content=body.model_dump())
    _set_refresh_cookie(response, new_refresh)
    return response


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims = decode_token(credentials.credentials)
    redis = get_redis(request)
    await revoke_token(redis, claims)

    rt = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if rt:
        try:
            await revoke_token(redis, decode_any_token(rt, expected_type="refresh"))
        except HTTPException:
            pass

    response = JSONResponse(content={"detail": "Logged out"})
    _clear_refresh_cookie(response)
    return response


@router.post("/logout-all")
async def logout_all(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Revoke every token issued to the caller (logout on all devices)."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims = decode_token(credentials.credentials)
    uid = claims.get("uid")
    if uid is None:
        raise HTTPException(status_code=400, detail="Malformed token")
    await revoke_all_for_user(get_redis(request), int(uid))
    response = JSONResponse(content={"detail": "All sessions revoked"})
    _clear_refresh_cookie(response)
    return response


@router.post("/change-password")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    claims = decode_token(credentials.credentials)
    await assert_not_revoked(get_redis(request), claims)
    uid = claims.get("uid")
    if uid is None:
        raise HTTPException(status_code=401, detail="Malformed token")

    user = await UserRepository(db).get_by_id(int(uid))
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    await db.commit()
    await revoke_all_for_user(get_redis(request), user.id)
    response = JSONResponse(content={"detail": "Password changed; please log in again"})
    _clear_refresh_cookie(response)
    return response


@router.get("/me", response_model=CurrentUserResponse)
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    uid = payload.get("uid")
    if uid is None:
        raise HTTPException(status_code=401, detail="Malformed token")

    user = await UserRepository(db).get_by_id(int(uid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
