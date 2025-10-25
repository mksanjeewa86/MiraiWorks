"""remove_current_due_date_from_extension_requests

Revision ID: e8b5e6296ba3
Revises: a140a45f6bcd
Create Date: 2025-10-18 16:00:08.383984

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8b5e6296ba3"
down_revision: Union[str, None] = "a140a45f6bcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove current_due_date column from todo_extension_requests table
    op.drop_column("todo_extension_requests", "current_due_date")


def downgrade() -> None:
    # Add back current_due_date column if rollback is needed
    op.add_column(
        "todo_extension_requests",
        sa.Column("current_due_date", sa.DateTime(timezone=True), nullable=True),
    )
