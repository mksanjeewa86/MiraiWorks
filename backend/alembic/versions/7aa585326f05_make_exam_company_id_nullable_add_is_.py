"""make_exam_company_id_nullable_add_is_public

Revision ID: 7aa585326f05
Revises: 4362115dcd78
Create Date: 2025-10-05 17:58:05.491119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7aa585326f05'
down_revision: Union[str, None] = '4362115dcd78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_public column to exams table
    op.add_column('exams', sa.Column('is_public', sa.Boolean(), nullable=False, server_default='0'))

    # Make company_id nullable (allow global exams)
    op.alter_column('exams', 'company_id',
               existing_type=sa.Integer(),
               nullable=True)


def downgrade() -> None:
    # Make company_id NOT NULL again
    # Note: This will fail if there are global exams (company_id=NULL)
    op.alter_column('exams', 'company_id',
               existing_type=sa.Integer(),
               nullable=False)

    # Remove is_public column
    op.drop_column('exams', 'is_public')