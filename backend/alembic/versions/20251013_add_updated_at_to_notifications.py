"""add_updated_at_to_notifications

Revision ID: a1b2c3d4e5f6
Revises: 9b7c8d5e4f2a
Create Date: 2025-10-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '20251012001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at column to notifications table
    # Using server_default to set initial value for existing rows
    op.add_column(
        'notifications',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
        )
    )


def downgrade() -> None:
    # Remove updated_at column from notifications table
    op.drop_column('notifications', 'updated_at')
