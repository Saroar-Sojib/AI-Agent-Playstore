
from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


def _client_identity(request: Request) -> str:
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
