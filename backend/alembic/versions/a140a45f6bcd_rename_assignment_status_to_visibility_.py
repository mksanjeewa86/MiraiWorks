"""rename_assignment_status_to_visibility_status_and_add_assignee

Revision ID: a140a45f6bcd
Revises: 94338479f2fa
Create Date: 2025-10-18 06:33:14.192306

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a140a45f6bcd"
down_revision: Union[str, None] = "94338479f2fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename assignment_status to visibility_status (MySQL requires existing type)
    op.alter_column(
        "todos",
        "assignment_status",
        new_column_name="visibility_status",
        existing_type=sa.String(20),
        existing_nullable=True,
    )

    # Add assignee_id for assignment type todos
    op.add_column("todos", sa.Column("assignee_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_todos_assignee_id"), "todos", ["assignee_id"], unique=False
    )
    op.create_foreign_key(
        "fk_todos_assignee_id",
        "todos",
        "users",
        ["assignee_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Remove assignee_id
    op.drop_constraint("fk_todos_assignee_id", "todos", type_="foreignkey")
    op.drop_index(op.f("ix_todos_assignee_id"), table_name="todos")
    op.drop_column("todos", "assignee_id")

    # Rename visibility_status back to assignment_status (MySQL requires existing type)
    op.alter_column(
        "todos",
        "visibility_status",
        new_column_name="assignment_status",
        existing_type=sa.String(20),
        existing_nullable=True,
    )
