"""remove_todo_user_assignment_fields

Revision ID: 94338479f2fa
Revises: eeb10585ac49
Create Date: 2025-10-18 14:31:56.217594

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "94338479f2fa"
down_revision: Union[str, None] = "eeb10585ac49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the todo_viewers table first
    op.drop_table("todo_viewers")

    # Use batch operations for MySQL to handle foreign keys and indexes automatically
    with op.batch_alter_table("todos", schema=None) as batch_op:
        batch_op.drop_column("assigned_user_id")
        batch_op.drop_column("visibility")


def downgrade() -> None:
    # Recreate todo_viewers table
    op.create_table(
        "todo_viewers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("todo_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["todo_id"], ["todos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("todo_id", "user_id", name="uq_todo_viewers_todo_user"),
    )
    op.create_index("ix_todo_viewers_todo_id", "todo_viewers", ["todo_id"])
    op.create_index("ix_todo_viewers_user_id", "todo_viewers", ["user_id"])

    # Add back the columns to todos table
    op.add_column(
        "todos",
        sa.Column(
            "visibility", sa.String(length=20), nullable=False, server_default="private"
        ),
    )
    op.add_column("todos", sa.Column("assigned_user_id", sa.Integer(), nullable=True))
    op.create_index("ix_todos_visibility", "todos", ["visibility"])
    op.create_index("ix_todos_assigned_user_id", "todos", ["assigned_user_id"])
    op.create_foreign_key(
        "fk_todos_assigned_user_id",
        "todos",
        "users",
        ["assigned_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
