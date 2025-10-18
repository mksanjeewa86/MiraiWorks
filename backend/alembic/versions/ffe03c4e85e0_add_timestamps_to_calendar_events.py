"""add_timestamps_to_calendar_events

Revision ID: ffe03c4e85e0
Revises: b19ce77ccc7e
Create Date: 2025-10-17 14:12:45.162226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffe03c4e85e0'
down_revision: Union[str, None] = 'b19ce77ccc7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Modify created_at and updated_at columns to add proper defaults
    op.execute('ALTER TABLE calendar_events MODIFY COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP')
    op.execute('ALTER TABLE calendar_events MODIFY COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')


def downgrade() -> None:
    # Revert created_at and updated_at columns to no defaults
    op.execute('ALTER TABLE calendar_events MODIFY COLUMN created_at DATETIME NOT NULL')
    op.execute('ALTER TABLE calendar_events MODIFY COLUMN updated_at DATETIME NOT NULL')