"""Add file attachment columns to direct_messages table

Revision ID: add_file_attachments
Revises:
Create Date: 2025-09-09 15:45:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_file_attachments"
down_revision = "5dc8de319ce0"
depends_on = None


def upgrade() -> None:
    # Add file attachment columns to direct_messages table
    op.add_column(
        "direct_messages", sa.Column("file_url", sa.String(500), nullable=True)
    )
    op.add_column(
        "direct_messages", sa.Column("file_name", sa.String(255), nullable=True)
    )
    op.add_column(
        "direct_messages", sa.Column("file_size", sa.Integer(), nullable=True)
    )
    op.add_column(
        "direct_messages", sa.Column("file_type", sa.String(100), nullable=True)
    )


def downgrade() -> None:
    # Remove file attachment columns from direct_messages table
    op.drop_column("direct_messages", "file_type")
    op.drop_column("direct_messages", "file_size")
    op.drop_column("direct_messages", "file_name")
    op.drop_column("direct_messages", "file_url")
