"""Remove duplicate two_factor_enabled field from user_settings

Revision ID: remove_duplicate_2fa
Revises: 45f3b411a417
Create Date: 2025-09-07 05:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "remove_duplicate_2fa"
down_revision = "45f3b411a417"
branch_labels = None
depends_on = None


def upgrade():
    """Remove the redundant two_factor_enabled column from user_settings table."""
    # Remove the column
    op.drop_column("user_settings", "two_factor_enabled")


def downgrade():
    """Add back the two_factor_enabled column to user_settings table."""
    # Add the column back
    op.add_column(
        "user_settings",
        sa.Column(
            "two_factor_enabled", sa.Boolean(), nullable=False, server_default="0"
        ),
    )
