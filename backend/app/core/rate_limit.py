"""Lightweight Redis-backed rate limiter.

Fixed-window counter keyed on (route × identity). One Redis INCR per request;
the first call seeds the TTL. Simple and good enough for abuse-prevention on
authentication and grant endpoints. If you need precise bursting semantics
later (sliding window, token bucket), swap in ``slowapi`` or ``limits``.

Usage::

    from app.core.rate_limit import RateLimit

    @router.post("/login", dependencies=[Depends(RateLimit("auth.login", 10, 60))])
    async def login(...): ...

If Redis is unavailable, the limiter fails OPEN (allows the request) and
logs a warning — denying real traffic over a cache outage would be worse
than the abuse window.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


def _client_identity(request: Request) -> str:
    """Best-effort caller identity for rate-key bucketing.

    Authenticated callers are keyed by their bearer-token's first 16 chars
    (stable per user without storing the full token). Anonymous callers
    fall back to their client IP (X-Forwarded-For first, then peer).
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        return f"tok:{token[:16]}"
    fwd = request.headers.get("X-Forwarded-For")
    if fwd:
        return f"ip:{fwd.split(',')[0].strip()}"
    if request.client:
        return f"ip:{request.client.host}"
    return "ip:unknown"


class RateLimit:
    """Dependency factory: enforce ``max_requests`` per ``window_seconds``.

    Args:
        name: Route key — appears in the Redis key, keep it short and stable.
        max_requests: Allowed count inside the window before 429s start.
        window_seconds: Window length in seconds.
    """

    def __init__(self, name: str, max_requests: int, window_seconds: int):
        if max_requests < 1 or window_seconds < 1:
            raise ValueError("max_requests and window_seconds must be >= 1")
        self.name = name
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(self, request: Request) -> None:
        redis = self._redis(request)
        if redis is None:
            return  # fail open

        identity = _client_identity(request)
        key = f"rl:{self.name}:{identity}"
        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self.window_seconds)
        except Exception:
            logger.warning("rate-limit redis call failed for %s", key, exc_info=True)
            return  # fail open

        if count > self.max_requests:
            try:
                ttl = await redis.ttl(key)
            except Exception:
                ttl = self.window_seconds
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {max(ttl, 1)}s.",
                headers={"Retry-After": str(max(ttl, 1))},
            )

    @staticmethod
    def _redis(request: Request) -> Optional[object]:
        try:
            return request.app.state.redis
        except AttributeError:
            return None
