from sqlalchemy import Column, ForeignKey, Integer, String

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin


class Conversation(Base, CreatedAtMixin):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("res_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sub_agent_id = Column(
        Integer,
        ForeignKey("sub_agents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title = Column(String(255), nullable=True)
