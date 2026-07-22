from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """A single chat turn from the caller — main-agent or sub-agent chat."""

    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """The assistant's reply plus the conversation it was persisted under."""

    conversation_id: int
    reply: str


class SubAgentResponse(BaseModel):
    """Public catalog entry for a sub-agent."""

    id: int
    name: str
    task_description: Optional[str] = None
    order_index: int

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """One turn of a conversation, for history reload."""

    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
