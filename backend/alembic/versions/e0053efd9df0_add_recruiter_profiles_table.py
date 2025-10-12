"""add recruiter profiles table

Revision ID: e0053efd9df0
Revises: 20251012_profile
Create Date: 2025-10-12 15:21:03.773275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0053efd9df0'
down_revision: Union[str, None] = '20251012_profile'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create recruiter_profiles table
    op.create_table(
        'recruiter_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('specializations', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('company_description', sa.Text(), nullable=True),
        sa.Column('industries', sa.Text(), nullable=True),
        sa.Column('job_types', sa.Text(), nullable=True),
        sa.Column('locations', sa.Text(), nullable=True),
        sa.Column('experience_levels', sa.Text(), nullable=True),
        sa.Column('calendar_link', sa.String(length=500), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('jobs_posted', sa.Integer(), nullable=True),
        sa.Column('candidates_placed', sa.Integer(), nullable=True),
        sa.Column('active_openings', sa.Integer(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recruiter_profiles_id'), 'recruiter_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_recruiter_profiles_user_id'), 'recruiter_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_recruiter_profiles_user_id'), table_name='recruiter_profiles')
    op.drop_index(op.f('ix_recruiter_profiles_id'), table_name='recruiter_profiles')
    op.drop_table('recruiter_profiles')