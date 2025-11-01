"""add_assignment_approved_to_todos

Revision ID: e8837ffa598b
Revises: e8d566b8c47f
Create Date: 2025-11-01 12:56:37.982357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8837ffa598b'
down_revision: Union[str, None] = 'e8d566b8c47f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add assignment_approved column to todos table
    op.add_column('todos', sa.Column('assignment_approved', sa.Boolean(), nullable=True))


def downgrade() -> None:
    # Remove assignment_approved column from todos table
    op.drop_column('todos', 'assignment_approved')