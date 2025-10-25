"""fix_notification_is_read_defaults

Revision ID: e8d566b8c47f
Revises: b54ff7762dc1
Create Date: 2025-10-24 14:52:22.189759

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8d566b8c47f"
down_revision: Union[str, None] = "b54ff7762dc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update existing NULL values to False
    op.execute("UPDATE notifications SET is_read = 0 WHERE is_read IS NULL")

    # Add server default
    op.alter_column(
        "notifications",
        "is_read",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default="0",
    )


def downgrade() -> None:
    # Remove server default
    op.alter_column(
        "notifications",
        "is_read",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=None,
    )
