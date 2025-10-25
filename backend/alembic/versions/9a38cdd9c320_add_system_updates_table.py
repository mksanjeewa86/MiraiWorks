"""Add system_updates table

Revision ID: 9a38cdd9c320
Revises: 7df22cd08a05
Create Date: 2025-10-11 01:06:31.642236

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a38cdd9c320"
down_revision: Union[str, None] = "7df22cd08a05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create system_updates table
    op.create_table(
        "system_updates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_system_updates_id"), "system_updates", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_system_updates_is_active"),
        "system_updates",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_system_updates_created_at"),
        "system_updates",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop system_updates table
    op.drop_index(op.f("ix_system_updates_created_at"), table_name="system_updates")
    op.drop_index(op.f("ix_system_updates_is_active"), table_name="system_updates")
    op.drop_index(op.f("ix_system_updates_id"), table_name="system_updates")
    op.drop_table("system_updates")
