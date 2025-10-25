"""add_timestamps_to_todo_viewers

Revision ID: 51b014e02d76
Revises: b872bf71e419
Create Date: 2025-10-19 09:24:40.781938

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "51b014e02d76"
down_revision: Union[str, None] = "b872bf71e419"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add created_at and updated_at columns to todo_viewers table
    op.add_column(
        "todo_viewers",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "todo_viewers",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    # Remove created_at and updated_at columns from todo_viewers table
    op.drop_column("todo_viewers", "updated_at")
    op.drop_column("todo_viewers", "created_at")
