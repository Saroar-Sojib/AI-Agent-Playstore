from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.database import Base
from app.infrastructure.mixins import _utcnow


class UsageLog(Base):
    """One row per LLM call — cost/usage tracking and abuse monitoring.

    Written for both success and error outcomes (``status``), independent of
    whether a ``ChatMessage`` pair was persisted, so failed calls are still
    visible in usage metrics.
    """

    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer, ForeignKey("res_users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_id = Column(
        Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sub_agent_id = Column(
        Integer,
        ForeignKey("sub_agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    request_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)
