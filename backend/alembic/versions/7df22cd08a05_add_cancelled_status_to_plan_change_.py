"""add_cancelled_status_to_plan_change_requests

Revision ID: 7df22cd08a05
Revises: 55b003be1de5
Create Date: 2025-10-06 23:21:48.013969

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7df22cd08a05"
down_revision: Union[str, None] = "55b003be1de5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'cancelled' to the status enum for plan_change_requests table
    op.execute(
        """
        ALTER TABLE plan_change_requests
        MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'cancelled')
        NOT NULL DEFAULT 'pending'
    """
    )


def downgrade() -> None:
    # Remove 'cancelled' from the status enum
    # Note: This will fail if any rows have status='cancelled'
    op.execute(
        """
        ALTER TABLE plan_change_requests
        MODIFY COLUMN status ENUM('pending', 'approved', 'rejected')
        NOT NULL DEFAULT 'pending'
    """
    )
