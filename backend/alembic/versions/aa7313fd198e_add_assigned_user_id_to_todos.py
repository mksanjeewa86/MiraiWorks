"""add_assigned_user_id_to_todos

Revision ID: aa7313fd198e
Revises: 30ef7510ad6d
Create Date: 2025-09-23 15:50:04.255434

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aa7313fd198e"
down_revision: str | None = "30ef7510ad6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add assigned_user_id column to todos table
    op.add_column("todos", sa.Column("assigned_user_id", sa.Integer(), nullable=True))

    # Add index for performance
    op.create_index("idx_todos_assigned_user_id", "todos", ["assigned_user_id"])

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_todos_assigned_user_id",
        "todos",
        "users",
        ["assigned_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint("fk_todos_assigned_user_id", "todos", type_="foreignkey")

    # Remove index
    op.drop_index("idx_todos_assigned_user_id", "todos")

    # Remove column
    op.drop_column("todos", "assigned_user_id")
