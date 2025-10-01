"""Add holidays table

Revision ID: add_holidays_table
Revises:
Create Date: 2025-09-28 12:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_holidays_table'
down_revision = 'manual_assignment_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create holidays table
    op.create_table(
        'holidays',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('name_en', sa.String(length=255), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('country', sa.String(length=10), nullable=False),
        sa.Column('is_national', sa.Boolean(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('description_en', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better query performance
    op.create_index('ix_holidays_date', 'holidays', ['date'])
    op.create_index('ix_holidays_year', 'holidays', ['year'])
    op.create_index('ix_holidays_country', 'holidays', ['country'])
    op.create_index('ix_holidays_year_country', 'holidays', ['year', 'country'])
    op.create_index('ix_holidays_date_country', 'holidays', ['date', 'country'])


def downgrade():
    # Drop indexes first
    op.drop_index('ix_holidays_date_country', table_name='holidays')
    op.drop_index('ix_holidays_year_country', table_name='holidays')
    op.drop_index('ix_holidays_country', table_name='holidays')
    op.drop_index('ix_holidays_year', table_name='holidays')
    op.drop_index('ix_holidays_date', table_name='holidays')

    # Drop table
    op.drop_table('holidays')
