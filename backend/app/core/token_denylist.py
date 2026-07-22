from __future__ import annotations

import time
from typing import Any, Optional

from fastapi import HTTPException, status

from app.core.config import settings

REVOKED_PREFIX = "auth:revoked:"
USER_MIN_IAT_PREFIX = "auth:min_iat:"


def _max_token_ttl() -> int:
    """Upper bound on any token's lifetime (refresh tokens are the longest)."""
    return settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400


async def revoke_token(redis, claims: dict[str, Any]) -> None:
    """Denylist a single token by its ``jti`` until it would have expired."""
    if redis is None:
        return
    jti = claims.get("jti")
    exp = claims.get("exp")
    if not jti or exp is None:
        return
    ttl = int(exp) - int(time.time())
    if ttl <= 0:
        return
    try:
        await redis.set(f"{REVOKED_PREFIX}{jti}", "1", ex=ttl)
    except Exception:
        pass


async def revoke_all_for_user(redis, uid: int) -> None:
    """Invalidate every token issued to ``uid`` before now (logout-everywhere)."""
    if redis is None:
        return
    try:
        await redis.set(
            f"{USER_MIN_IAT_PREFIX}{uid}",
            str(int(time.time())),
            ex=_max_token_ttl(),
        )
    except Exception:
        pass


async def is_revoked(redis, claims: dict[str, Any]) -> bool:
    """True if the token is denylisted or predates its user's revoke-all cutoff."""
    if redis is None:
        return False
    jti = claims.get("jti")
    uid = claims.get("uid")
    iat = claims.get("iat")
    try:
        if jti and await redis.get(f"{REVOKED_PREFIX}{jti}"):
            return True
        if uid is not None and iat is not None:
            raw = await redis.get(f"{USER_MIN_IAT_PREFIX}{uid}")
            if raw is not None:
                min_iat = int(raw.decode() if isinstance(raw, bytes) else raw)
                if int(iat) < min_iat:
                    return True
    except Exception:
        return False
    return False


async def assert_not_revoked(redis, claims: dict[str, Any]) -> dict[str, Any]:
    """Raise 401 if the token is revoked; otherwise return the claims."""
    if await is_revoked(redis, claims):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    return claims


def get_redis(request) -> Optional[Any]:
    """Best-effort fetch of the request-scoped Redis client."""
    try:
        return request.app.state.redis
    except AttributeError:
        return None
