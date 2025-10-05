"""Add todo attachments table

Revision ID: add_todo_attachments
Revises: add_video_call_tables
Create Date: 2024-01-15 10:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_todo_attachments"
down_revision = "add_video_call_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create todo_attachments table
    op.create_table(
        "todo_attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("todo_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_extension", sa.String(length=10), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["todo_id"], ["todos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename"),
    )

    # Create indexes for better performance
    op.create_index(
        op.f("ix_todo_attachments_todo_id"),
        "todo_attachments",
        ["todo_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_todo_attachments_uploaded_at"),
        "todo_attachments",
        ["uploaded_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_todo_attachments_uploaded_by"),
        "todo_attachments",
        ["uploaded_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_todo_attachments_mime_type"),
        "todo_attachments",
        ["mime_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_todo_attachments_file_size"),
        "todo_attachments",
        ["file_size"],
        unique=False,
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f("ix_todo_attachments_file_size"), table_name="todo_attachments")
    op.drop_index(op.f("ix_todo_attachments_mime_type"), table_name="todo_attachments")
    op.drop_index(
        op.f("ix_todo_attachments_uploaded_by"), table_name="todo_attachments"
    )
    op.drop_index(
        op.f("ix_todo_attachments_uploaded_at"), table_name="todo_attachments"
    )
    op.drop_index(op.f("ix_todo_attachments_todo_id"), table_name="todo_attachments")

    # Drop table
    op.drop_table("todo_attachments")
