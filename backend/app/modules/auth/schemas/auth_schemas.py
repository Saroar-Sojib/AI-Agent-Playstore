from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Create a new user account, scoped to exactly one agent."""
    agent_slug: str = Field(..., min_length=1, max_length=160)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    """Credentials for native email + password login, scoped to one agent."""
    agent_slug: str = Field(..., min_length=1, max_length=160)
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    """Self-service password change — requires the current password."""
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


class TokenBundle(BaseModel):
    """Access-token payload returned to the SPA after signup / login / refresh.

    The refresh token is delivered out-of-band in an httpOnly cookie, not in
    this body.
    """
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None


class CurrentUserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    agent_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
