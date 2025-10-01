"""add user connections table

Revision ID: add_user_connections_simple
Revises: b0df91bde9c0
Create Date: 2024-12-27 22:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint

from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_user_connections_simple'
down_revision = 'b0df91bde9c0'
branch_labels = None
depends_on = None


def upgrade():
    """Create user_connections table."""
    op.create_table(
        'user_connections',
        Column('id', Integer, primary_key=True, index=True),
        Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        Column('connected_user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime, nullable=False, default=sa.func.current_timestamp()),
        UniqueConstraint('user_id', 'connected_user_id', name='unique_user_connection'),
    )


def downgrade():
    """Drop user_connections table."""
    op.drop_table('user_connections')
