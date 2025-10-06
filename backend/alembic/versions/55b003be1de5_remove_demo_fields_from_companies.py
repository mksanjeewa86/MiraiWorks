"""remove_demo_fields_from_companies

Revision ID: 55b003be1de5
Revises: 8b3c7d9e2f1a
Create Date: 2025-10-06 21:45:50.169498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55b003be1de5'
down_revision: Union[str, None] = '8b3c7d9e2f1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove demo fields from companies table
    op.drop_column('companies', 'is_demo')
    op.drop_column('companies', 'demo_end_date')
    op.drop_column('companies', 'demo_features')
    op.drop_column('companies', 'demo_notes')


def downgrade() -> None:
    # Add back demo fields to companies table
    op.add_column('companies', sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('companies', sa.Column('demo_end_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('companies', sa.Column('demo_features', sa.Text(), nullable=True))
    op.add_column('companies', sa.Column('demo_notes', sa.Text(), nullable=True))