from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin


class SubAgent(Base, CreatedAtMixin):
    """A specialized sub-agent belonging to one ``Agent`` persona.

    Each profession (``Agent``) exposes 2-5 sub-agents (e.g. Financial
    Controller -> "Reconciliation Agent", "Excel Agent", "Invoice Processing
    Agent", "Learning Agent") imported from the source spreadsheet's
    ``Agent 1..4`` / ``Agent 1..4 Task`` columns. A chat conversation can
    target either the main ``Agent`` persona directly or one specific
    ``SubAgent`` — same chat UI, different system prompt/behavior.

    ``system_prompt`` is left nullable — it's populated by a later
    content-pipeline script; chat falls back to a generic default built from
    ``name``/``task_description`` until then (see ``chat_service``).
    """

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
    # Position among the parent agent's sub-agents (1-4), matching the source
    # spreadsheet's "Agent 1".."Agent 4" column order.
    order_index = Column(Integer, nullable=False, default=1)
