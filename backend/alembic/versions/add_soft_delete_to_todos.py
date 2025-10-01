"""add soft delete fields to todos table

Revision ID: add_soft_delete_to_todos
Revises: create_todos_table
Create Date: 2025-09-21 15:30:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_soft_delete_to_todos"
down_revision = "create_todos_table"
branch_labels = None
depends_on = None


def upgrade():
    # Add is_deleted column with default False
    op.add_column(
        "todos",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE")
        )
    )

    # Add deleted_at column
    op.add_column(
        "todos",
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Add index on is_deleted for efficient filtering
    op.create_index("ix_todos_is_deleted", "todos", ["is_deleted"])


def downgrade():
    # Remove index
    op.drop_index("ix_todos_is_deleted", table_name="todos")

    # Remove columns
    op.drop_column("todos", "deleted_at")
    op.drop_column("todos", "is_deleted")
