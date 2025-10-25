"""rename_notes_to_assignee_memo_and_add_viewer_memos

Revision ID: bc0f5b6b4147
Revises: 950195cd21f3
Create Date: 2025-10-23 14:30:15.003768

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc0f5b6b4147"
down_revision: Union[str, None] = "950195cd21f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename 'notes' column to 'assignee_memo' in todos table
    op.alter_column(
        "todos",
        "notes",
        new_column_name="assignee_memo",
        existing_type=sa.Text(),
        existing_nullable=True,
    )

    # Create todo_viewer_memos table
    op.create_table(
        "todo_viewer_memos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("todo_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["todo_id"], ["todos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("todo_id", "user_id", name="uq_todo_viewer_memo"),
    )
    op.create_index("ix_todo_viewer_memos_todo_id", "todo_viewer_memos", ["todo_id"])
    op.create_index("ix_todo_viewer_memos_user_id", "todo_viewer_memos", ["user_id"])


def downgrade() -> None:
    # Drop indexes and table
    op.drop_index("ix_todo_viewer_memos_user_id", "todo_viewer_memos")
    op.drop_index("ix_todo_viewer_memos_todo_id", "todo_viewer_memos")
    op.drop_table("todo_viewer_memos")

    # Rename 'assignee_memo' back to 'notes'
    op.alter_column(
        "todos",
        "assignee_memo",
        new_column_name="notes",
        existing_type=sa.Text(),
        existing_nullable=True,
    )
