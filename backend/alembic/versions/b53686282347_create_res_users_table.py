"""create res_users table

Revision ID: b53686282347
Revises: 0d43c756240b
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b53686282347"
down_revision: Union[str, Sequence[str], None] = "0d43c756240b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "res_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name=op.f("fk_res_users_agent_id_agents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_res_users")),
        sa.UniqueConstraint("agent_id", "email", name="uq_user_agent_email"),
    )
    op.create_index(op.f("ix_res_users_id"), "res_users", ["id"], unique=False)
    op.create_index(op.f("ix_res_users_agent_id"), "res_users", ["agent_id"], unique=False)
    op.create_index(op.f("ix_res_users_email"), "res_users", ["email"], unique=False)
    op.create_index(op.f("ix_res_users_deleted_at"), "res_users", ["deleted_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_res_users_deleted_at"), table_name="res_users")
    op.drop_index(op.f("ix_res_users_email"), table_name="res_users")
    op.drop_index(op.f("ix_res_users_agent_id"), table_name="res_users")
    op.drop_index(op.f("ix_res_users_id"), table_name="res_users")
    op.drop_table("res_users")
