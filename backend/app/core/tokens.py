"""Native JWT issuance and verification.

The backend is its own identity provider: it signs short-lived **access**
tokens and longer-lived **refresh** tokens with HS256 using
``settings.JWT_SECRET_KEY``. There is no external OIDC provider.

Token shape (access):
    {
      "sub":      "42",                 # stable subject: local res_users.id as string
      "uid":      42,                    # local res_users.id
      "email":    "user@example.com",
      "agent_id": "7" | null,            # local agents.id as string
      "type":     "access",
      "iat": ..., "exp": ...
    }

Refresh tokens carry the same identity claims plus ``"type": "refresh"`` and a
random ``jti`` so they can be denylisted later if needed.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encode(claims: dict[str, Any]) -> str:
    if not settings.JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY is not configured",
        )
    return jwt.encode(
        claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(
    *,
    uid: int,
    email: str,
    agent_id: Optional[int],
) -> tuple[str, int]:
    """Return ``(token, expires_in_seconds)`` for an access token."""
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = _now()
    claims = {
        "sub": str(uid),
        "uid": uid,
        "email": email,
        "agent_id": str(agent_id) if agent_id is not None else None,
        "type": ACCESS_TYPE,
        # jti enables single-token revocation (denylist); iat enables
        # per-user "revoke all" via a min-iat cutoff.
        "jti": secrets.token_urlsafe(16),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return _encode(claims), expires_in


def create_refresh_token(
    *,
    uid: int,
    email: str,
    agent_id: Optional[int],
) -> str:
    now = _now()
    claims = {
        "sub": str(uid),
        "uid": uid,
        "email": email,
        "agent_id": str(agent_id) if agent_id is not None else None,
        "type": REFRESH_TYPE,
        "jti": secrets.token_urlsafe(16),
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return _encode(claims)


def decode_token(token: str, *, expected_type: Optional[str] = None) -> dict[str, Any]:
    """Verify signature + expiry and return the claims. Raises 401 on failure.

    Pass ``expected_type`` (e.g. ``"refresh"``) to reject tokens of the wrong
    kind — prevents an access token being replayed at the refresh endpoint and
    vice-versa.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token"
        )
    try:
        claims = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc

    if expected_type is not None and claims.get("type") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Expected a {expected_type} token",
        )
    return claims


def claims_to_sub(claims: dict[str, Any]) -> str:
    """Return the stable subject string (local ``res_users.id``) from verified claims."""
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identifier",
        )
    return str(sub)
