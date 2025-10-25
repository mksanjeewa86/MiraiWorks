"""add_remember_me_to_refresh_tokens

Revision ID: b19ce77ccc7e
Revises: 76fccc37e5b9
Create Date: 2025-10-17 01:42:04.044889

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b19ce77ccc7e"
down_revision: Union[str, None] = "76fccc37e5b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add remember_me column to refresh_tokens table
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "remember_me", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
    )
    # Create index on remember_me column for faster queries
    op.create_index(
        op.f("ix_refresh_tokens_remember_me"),
        "refresh_tokens",
        ["remember_me"],
        unique=False,
    )


def downgrade() -> None:
    # Drop index first
    op.drop_index(op.f("ix_refresh_tokens_remember_me"), table_name="refresh_tokens")
    # Drop remember_me column
    op.drop_column("refresh_tokens", "remember_me")
