"""rename_candidate_to_assignee_in_interviews

Revision ID: a8e7a8ce9c21
Revises: e8837ffa598b
Create Date: 2025-11-09 00:27:45.230302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8e7a8ce9c21'
down_revision: Union[str, None] = 'e8837ffa598b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename candidate_id to assignee_id in interviews table
    op.alter_column('interviews', 'candidate_id',
                    new_column_name='assignee_id',
                    existing_type=sa.Integer(),
                    existing_nullable=False)


def downgrade() -> None:
    # Rename assignee_id back to candidate_id
    op.alter_column('interviews', 'assignee_id',
                    new_column_name='candidate_id',
                    existing_type=sa.Integer(),
                    existing_nullable=False)