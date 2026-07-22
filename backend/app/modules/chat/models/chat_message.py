from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin


class ChatMessage(Base, CreatedAtMixin):
    """One turn of a ``Conversation`` — either the user's message or the
    assistant's reply (role: "user" / "assistant" / "system")."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
