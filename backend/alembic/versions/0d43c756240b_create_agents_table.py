"""create agents table

Revision ID: 0d43c756240b
Revises:
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d43c756240b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("industry", sa.String(length=160), nullable=True),
        sa.Column("profession", sa.String(length=160), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("source_row_no", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agents")),
    )
    op.create_index(op.f("ix_agents_id"), "agents", ["id"], unique=False)
    op.create_index(op.f("ix_agents_slug"), "agents", ["slug"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_agents_slug"), table_name="agents")
    op.drop_index(op.f("ix_agents_id"), table_name="agents")
    op.drop_table("agents")
