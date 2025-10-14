"""Add blocked_companies table

Revision ID: 45708fe415bb
Revises: 8cdd14038b87
Create Date: 2025-10-14 13:59:50.125990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45708fe415bb'
down_revision: Union[str, None] = '8cdd14038b87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create blocked_companies table
    op.create_table(
        'blocked_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_blocked_companies_user_id', 'blocked_companies', ['user_id'], unique=False)
    op.create_index('ix_blocked_companies_company_id', 'blocked_companies', ['company_id'], unique=False)
    op.create_index('ix_blocked_companies_company_name', 'blocked_companies', ['company_name'], unique=False)
    op.create_index('ix_blocked_companies_user_company', 'blocked_companies', ['user_id', 'company_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_blocked_companies_user_company', table_name='blocked_companies')
    op.drop_index('ix_blocked_companies_company_name', table_name='blocked_companies')
    op.drop_index('ix_blocked_companies_company_id', table_name='blocked_companies')
    op.drop_index('ix_blocked_companies_user_id', table_name='blocked_companies')

    # Drop table
    op.drop_table('blocked_companies')