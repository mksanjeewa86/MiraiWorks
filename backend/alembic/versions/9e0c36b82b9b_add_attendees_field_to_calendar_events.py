"""Add attendees field to calendar_events

Revision ID: 9e0c36b82b9b
Revises: be0848aaf8e9
Create Date: 2025-10-20 13:28:52.489046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e0c36b82b9b'
down_revision: Union[str, None] = 'be0848aaf8e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add attendees column to calendar_events table
    op.add_column('calendar_events', sa.Column('attendees', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove attendees column from calendar_events table
    op.drop_column('calendar_events', 'attendees')