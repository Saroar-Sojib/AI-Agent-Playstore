
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.user_context import current_agent_id, current_user_id

SKIP_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


class AgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path not in SKIP_PATHS:
            resolved = await self._resolve_from_token(request)
            if resolved is not None:
                user_id, agent_id = resolved
                current_user_id.set(user_id)
                if agent_id is not None:
                    current_agent_id.set(agent_id)

        return await call_next(request)

    async def _resolve_from_token(self, request: Request):
        from fastapi import HTTPException

        from app.core.security import decode_token
        from app.core.token_denylist import is_revoked

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth[len("Bearer "):]

        try:
            payload = decode_token(token)
        except HTTPException:
            return None

        if await is_revoked(self._get_redis(request), payload):
            return None

        uid = payload.get("uid")
        if uid is None:
            return None

        agent_raw = payload.get("agent_id")
        agent_id = int(agent_raw) if agent_raw not in (None, "") else None
        return int(uid), agent_id

    def _get_redis(self, request: Request):
        try:
            return request.app.state.redis
        except AttributeError:
            return None
