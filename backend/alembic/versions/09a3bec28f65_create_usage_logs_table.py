"""create usage_logs table

Revision ID: 09a3bec28f65
Revises: 239389782f83
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "09a3bec28f65"
down_revision: Union[str, Sequence[str], None] = "239389782f83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "usage_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("sub_agent_id", sa.Integer(), nullable=True),
        sa.Column("request_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["res_users.id"],
            name=op.f("fk_usage_logs_user_id_res_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name=op.f("fk_usage_logs_agent_id_agents"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["sub_agent_id"],
            ["sub_agents.id"],
            name=op.f("fk_usage_logs_sub_agent_id_sub_agents"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usage_logs")),
    )
    op.create_index(op.f("ix_usage_logs_id"), "usage_logs", ["id"], unique=False)
    op.create_index(op.f("ix_usage_logs_user_id"), "usage_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_usage_logs_agent_id"), "usage_logs", ["agent_id"], unique=False)
    op.create_index(op.f("ix_usage_logs_sub_agent_id"), "usage_logs", ["sub_agent_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_usage_logs_sub_agent_id"), table_name="usage_logs")
    op.drop_index(op.f("ix_usage_logs_agent_id"), table_name="usage_logs")
    op.drop_index(op.f("ix_usage_logs_user_id"), table_name="usage_logs")
    op.drop_index(op.f("ix_usage_logs_id"), table_name="usage_logs")
    op.drop_table("usage_logs")
