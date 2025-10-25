"""fix_todos_timestamps

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-10-13 13:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix created_at column to have CURRENT_TIMESTAMP default
    op.execute(
        """
        ALTER TABLE todos
        MODIFY COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    """
    )

    # Fix updated_at column to have CURRENT_TIMESTAMP default and ON UPDATE
    op.execute(
        """
        ALTER TABLE todos
        MODIFY COLUMN updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    """
    )


def downgrade() -> None:
    # Remove defaults (revert to previous state)
    op.execute(
        """
        ALTER TABLE todos
        MODIFY COLUMN created_at DATETIME NOT NULL
    """
    )

    op.execute(
        """
        ALTER TABLE todos
        MODIFY COLUMN updated_at DATETIME NOT NULL
    """
    )
