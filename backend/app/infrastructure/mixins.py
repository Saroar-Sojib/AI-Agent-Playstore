# app/infrastructure/mixins.py
from datetime import datetime, timezone
from sqlalchemy import Boolean,Integer, Column, DateTime, ForeignKey


def _utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
    created_by = Column(Integer, ForeignKey("res_users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("res_users.id"), nullable=True)


class CreatedAtMixin:
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)


class SoftDeleteMixin:
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


class AgentMixin:
    """For tables scoped to a single agent (the auth/catalog boundary)."""
    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
