"""Add suspension fields to users table

Revision ID: add_user_suspension
Revises: remove_duplicate_2fa
Create Date: 2025-09-14 05:10:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_user_suspension"
down_revision = "remove_duplicate_2fa"
branch_labels = None
depends_on = None


def upgrade():
    """Add suspension fields to users table."""
    # Add suspension fields
    op.add_column(
        "users",
        sa.Column("is_suspended", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users", sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("users", sa.Column("suspended_by", sa.Integer(), nullable=True))

    # Create indexes for better query performance
    op.create_index("ix_users_is_suspended", "users", ["is_suspended"])


def downgrade():
    """Remove suspension fields from users table."""
    # Drop indexes first
    op.drop_index("ix_users_is_suspended", table_name="users")

    # Drop columns
    op.drop_column("users", "suspended_by")
    op.drop_column("users", "suspended_at")
    op.drop_column("users", "is_suspended")
