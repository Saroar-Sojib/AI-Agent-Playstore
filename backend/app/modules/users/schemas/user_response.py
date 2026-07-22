from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    email: str
    agent_id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
