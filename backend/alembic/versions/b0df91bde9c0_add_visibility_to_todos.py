"""add visibility column to todos

Revision ID: b0df91bde9c0
Revises: aa7313fd198e
Create Date: 2025-09-25 23:05:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b0df91bde9c0'
down_revision: str | None = 'aa7313fd198e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'todos',
        sa.Column(
            'visibility',
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'private'"),
        ),
    )
    op.create_index('idx_todos_visibility', 'todos', ['visibility'])
    op.execute("UPDATE todos SET visibility = 'private' WHERE visibility IS NULL")


def downgrade() -> None:
    op.drop_index('idx_todos_visibility', 'todos')
    op.drop_column('todos', 'visibility')
