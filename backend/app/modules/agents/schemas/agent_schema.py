from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AgentResponse(BaseModel):
    id: int
    slug: str
    industry: Optional[str] = None
    profession: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
