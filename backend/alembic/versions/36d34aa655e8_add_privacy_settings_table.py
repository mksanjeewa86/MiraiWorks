"""add_privacy_settings_table

Revision ID: 36d34aa655e8
Revises: e0053efd9df0
Create Date: 2025-10-12 08:01:37.067494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36d34aa655e8'
down_revision: Union[str, None] = 'e0053efd9df0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'privacy_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('profile_visibility', sa.String(length=20), nullable=False, server_default='public'),
        sa.Column('searchable', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('show_email', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('show_phone', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('show_work_experience', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('show_education', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('show_skills', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('show_certifications', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('show_projects', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('show_resume', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_privacy_settings_user_id'), 'privacy_settings', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_privacy_settings_user_id'), table_name='privacy_settings')
    op.drop_table('privacy_settings')