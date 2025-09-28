"""add_calendar_events_table

Revision ID: 37a8bb883c3b
Revises: add_holidays_table
Create Date: 2025-09-28 21:18:42.600670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37a8bb883c3b'
down_revision: Union[str, None] = 'add_holidays_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create calendar_events table
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_datetime', sa.DateTime(), nullable=False),
        sa.Column('end_datetime', sa.DateTime(), nullable=True),
        sa.Column('is_all_day', sa.Boolean(), nullable=False, default=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False, default='event'),
        sa.Column('status', sa.String(length=20), nullable=False, default='confirmed'),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('recurrence_rule', sa.String(length=255), nullable=True),
        sa.Column('parent_event_id', sa.Integer(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, default='UTC'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_event_id'], ['calendar_events.id'], ondelete='CASCADE')
    )

    # Create indexes for better query performance
    op.create_index('idx_calendar_events_start_datetime', 'calendar_events', ['start_datetime'])
    op.create_index('idx_calendar_events_creator_id', 'calendar_events', ['creator_id'])
    op.create_index('idx_calendar_events_status', 'calendar_events', ['status'])
    op.create_index('idx_calendar_events_event_type', 'calendar_events', ['event_type'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_calendar_events_event_type', table_name='calendar_events')
    op.drop_index('idx_calendar_events_status', table_name='calendar_events')
    op.drop_index('idx_calendar_events_creator_id', table_name='calendar_events')
    op.drop_index('idx_calendar_events_start_datetime', table_name='calendar_events')

    # Drop table
    op.drop_table('calendar_events')