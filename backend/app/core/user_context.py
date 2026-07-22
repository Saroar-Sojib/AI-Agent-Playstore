from contextvars import ContextVar
from typing import Optional

# Local ``res_users.id`` of the authenticated user.
current_user_id: ContextVar[Optional[int]] = ContextVar(
    "current_user_id", default=None
)
# Local ``agents.id`` the authenticated user (or the request being handled)
# is scoped to — the auth-scoping boundary for AgentHub.
current_agent_id: ContextVar[Optional[int]] = ContextVar(
    "current_agent_id", default=None
)
