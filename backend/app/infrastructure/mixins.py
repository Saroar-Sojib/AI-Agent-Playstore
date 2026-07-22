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
    """Just ``created_at`` — for tables with no update/audit trail (seeded
    catalog rows, append-only logs/messages). Use ``TimestampMixin`` instead
    when a table is mutated by an authenticated user and needs the full
    created/updated-by audit trail."""

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)


class SoftDeleteMixin:
    """Universal soft-delete + activation flag.

    ``is_active=false`` means revoked / disabled but kept on file.
    ``deleted_at`` set means soft-deleted (filtered out by default queries).
    """

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
