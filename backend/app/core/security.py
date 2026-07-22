from __future__ import annotations

from typing import Any, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.tokens import decode_token as _decode_token
from app.core.user_context import current_user_id

security = HTTPBearer(auto_error=False)

_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """Return a bcrypt hash for ``password`` (utf-8, salted)."""
    pw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: Optional[str]) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(
            password.encode("utf-8")[:_BCRYPT_MAX_BYTES],
            hashed.encode("utf-8"),
        )
    except ValueError:
        return False


def decode_token(token: str) -> dict[str, Any]:
    """Verify a backend-issued access token and return its claims. Raises 401."""
    return _decode_token(token)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Auth dependency: validate the bearer token and return its claims."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
        )
    return decode_token(credentials.credentials)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[int]:
    existing = current_user_id.get()
    if existing is not None:
        return existing

    if not credentials:
        return None

    try:
        payload = decode_token(credentials.credentials)
    except HTTPException:
        return None

    uid = payload.get("uid")
    return int(uid) if uid is not None else None
