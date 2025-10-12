"""add_profile_views_table

Revision ID: 9b7c8d5e4f2a
Revises: 36d34aa655e8
Create Date: 2025-10-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b7c8d5e4f2a'
down_revision: Union[str, None] = '36d34aa655e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profile_views',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_user_id', sa.Integer(), nullable=False, comment='User whose profile was viewed'),
        sa.Column('viewer_user_id', sa.Integer(), nullable=True, comment='User who viewed the profile (null for anonymous views)'),
        sa.Column('viewer_company_id', sa.Integer(), nullable=True, comment='Company of the viewer'),
        sa.Column('viewer_ip', sa.String(length=45), nullable=True, comment='IP address of viewer'),
        sa.Column('viewer_user_agent', sa.Text(), nullable=True, comment='Browser/device info'),
        sa.Column('view_duration', sa.Integer(), nullable=True, comment='Duration of view in seconds'),
        sa.Column('referrer', sa.String(length=500), nullable=True, comment='How they found the profile'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['profile_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['viewer_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['viewer_company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_views_profile_user_id'), 'profile_views', ['profile_user_id'], unique=False)
    op.create_index(op.f('ix_profile_views_viewer_user_id'), 'profile_views', ['viewer_user_id'], unique=False)
    op.create_index(op.f('ix_profile_views_created_at'), 'profile_views', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_profile_views_created_at'), table_name='profile_views')
    op.drop_index(op.f('ix_profile_views_viewer_user_id'), table_name='profile_views')
    op.drop_index(op.f('ix_profile_views_profile_user_id'), table_name='profile_views')
    op.drop_table('profile_views')
