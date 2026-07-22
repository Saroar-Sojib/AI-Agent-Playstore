from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin, SoftDeleteMixin


class User(Base, SoftDeleteMixin, CreatedAtMixin):
    __tablename__ = "res_users"
    __table_args__ = (
        UniqueConstraint("agent_id", "email", name="uq_user_agent_email"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = Column(String, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
