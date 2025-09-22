"""merge_all_heads

Revision ID: 1afe6001ccfc
Revises: add_soft_delete_to_todos, add_video_call_tables, migrate_simple, migrate_to_messages, optimize_messages
Create Date: 2025-09-22 21:01:47.217808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1afe6001ccfc'
down_revision: Union[str, None] = ('add_soft_delete_to_todos', 'add_video_call_tables', 'migrate_simple', 'migrate_to_messages', 'optimize_messages')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass