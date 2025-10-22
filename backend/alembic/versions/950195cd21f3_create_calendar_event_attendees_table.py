"""Create calendar_event_attendees table

Revision ID: 950195cd21f3
Revises: 9e0c36b82b9b
Create Date: 2025-10-20 13:38:19.855322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '950195cd21f3'
down_revision: Union[str, None] = '9e0c36b82b9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the JSON attendees column if it exists
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('calendar_events')]

    if 'attendees' in columns:
        op.drop_column('calendar_events', 'attendees')

    # Create calendar_event_attendees table if it doesn't exist
    tables = inspector.get_table_names()
    if 'calendar_event_attendees' not in tables:
        op.create_table(
            'calendar_event_attendees',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('event_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(255), nullable=False),
            sa.Column('response_status', sa.String(20), nullable=False, server_default='pending'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        )

        # Create indexes
        op.create_index('ix_calendar_event_attendees_event_id', 'calendar_event_attendees', ['event_id'])
        op.create_index('ix_calendar_event_attendees_user_id', 'calendar_event_attendees', ['user_id'])
        op.create_index('ix_calendar_event_attendees_email', 'calendar_event_attendees', ['email'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_calendar_event_attendees_email', 'calendar_event_attendees')
    op.drop_index('ix_calendar_event_attendees_user_id', 'calendar_event_attendees')
    op.drop_index('ix_calendar_event_attendees_event_id', 'calendar_event_attendees')

    # Drop table
    op.drop_table('calendar_event_attendees')

    # Add back the JSON column
    op.add_column('calendar_events', sa.Column('attendees', sa.JSON(), nullable=True))