"""remove_added_at_from_todo_viewers

Revision ID: be0848aaf8e9
Revises: 51b014e02d76
Create Date: 2025-10-19 09:26:05.402115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be0848aaf8e9'
down_revision: Union[str, None] = '51b014e02d76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the old added_at column (replaced by created_at from BaseModel)
    op.drop_column('todo_viewers', 'added_at')


def downgrade() -> None:
    # Re-add the added_at column if needed
    op.add_column('todo_viewers',
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )