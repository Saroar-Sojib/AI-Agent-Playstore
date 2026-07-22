"""create sub_agents table

Revision ID: 51b204ecd079
Revises: b53686282347
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "51b204ecd079"
down_revision: Union[str, Sequence[str], None] = "b53686282347"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sub_agents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("task_description", sa.Text(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name=op.f("fk_sub_agents_agent_id_agents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sub_agents")),
    )
    op.create_index(op.f("ix_sub_agents_id"), "sub_agents", ["id"], unique=False)
    op.create_index(op.f("ix_sub_agents_agent_id"), "sub_agents", ["agent_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_sub_agents_agent_id"), table_name="sub_agents")
    op.drop_index(op.f("ix_sub_agents_id"), table_name="sub_agents")
    op.drop_table("sub_agents")
