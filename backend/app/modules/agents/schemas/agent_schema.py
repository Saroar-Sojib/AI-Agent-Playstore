from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Public catalog entry for an agent persona.

    ``system_prompt`` is deliberately NOT exposed here — it's the persona's
    implementation detail, not catalog/browsing data.
    """

    id: int
    slug: str
    industry: Optional[str] = None
    profession: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
