"""fix_todo_viewer_memo_defaults

Revision ID: b54ff7762dc1
Revises: 975879a174e7
Create Date: 2025-10-24 14:18:54.889283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b54ff7762dc1'
down_revision: Union[str, None] = '975879a174e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server defaults for created_at and updated_at in todo_viewer_memos
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'todo_viewer_memos' in inspector.get_table_names():
        op.alter_column('todo_viewer_memos', 'created_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=sa.text('CURRENT_TIMESTAMP'))
        op.alter_column('todo_viewer_memos', 'updated_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Add server defaults for created_at and updated_at in todo_viewers
    if 'todo_viewers' in inspector.get_table_names():
        op.alter_column('todo_viewers', 'created_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=sa.text('CURRENT_TIMESTAMP'))
        op.alter_column('todo_viewers', 'updated_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


def downgrade() -> None:
    # Remove server defaults
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'todo_viewers' in inspector.get_table_names():
        op.alter_column('todo_viewers', 'updated_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=None)
        op.alter_column('todo_viewers', 'created_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=None)

    if 'todo_viewer_memos' in inspector.get_table_names():
        op.alter_column('todo_viewer_memos', 'updated_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=None)
        op.alter_column('todo_viewer_memos', 'created_at',
                       existing_type=sa.DateTime(timezone=True),
                       nullable=False,
                       server_default=None)