"""create todos table

Revision ID: create_todos_table
Revises: add_user_suspension
Create Date: 2025-09-19 06:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "create_todos_table"
down_revision = "add_user_suspension"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
        sa.Column(
            "last_updated_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_todos_owner", "todos", ["owner_id"])
    op.create_index("ix_todos_status", "todos", ["status"])
    op.create_index("ix_todos_due_date", "todos", ["due_date"])
    op.create_index("ix_todos_owner_status", "todos", ["owner_id", "status"])


def downgrade():
    op.drop_index("ix_todos_owner_status", table_name="todos")
    op.drop_index("ix_todos_due_date", table_name="todos")
    op.drop_index("ix_todos_status", table_name="todos")
    op.drop_index("ix_todos_owner", table_name="todos")
    op.drop_table("todos")
