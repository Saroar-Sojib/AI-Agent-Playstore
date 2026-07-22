from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin


class SubAgent(Base, CreatedAtMixin):
    __tablename__ = "sub_agents"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(160), nullable=False)
    task_description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=1)
