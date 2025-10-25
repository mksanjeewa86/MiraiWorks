"""add_timezone_to_calendar_event_datetimes

Revision ID: 3048494cb683
Revises: ffe03c4e85e0
Create Date: 2025-10-17 16:01:03.387752

"""
from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = "3048494cb683"
down_revision: Union[str, None] = "ffe03c4e85e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # MySQL note: TIMESTAMP automatically stores in UTC and converts based on session timezone
    # We just ensure the columns are TIMESTAMP (which is timezone-aware in MySQL)
    # No actual migration needed - MySQL TIMESTAMP is already timezone-aware
    # This migration exists to document the model change
    pass


def downgrade() -> None:
    # No changes needed for MySQL
    pass
