"""merge_multiple_heads

Revision ID: a84ff39f6879
Revises: 002_rename_jobs_to_positions, add_file_attachments, create_todos_table
Create Date: 2025-09-20 21:26:57.107799

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'a84ff39f6879'
down_revision: str | None = ('002_rename_jobs_to_positions', 'add_file_attachments', 'create_todos_table')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
