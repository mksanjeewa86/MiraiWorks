"""add_creation_tracking_to_user_connections

Revision ID: f1413e5cffd1
Revises: eb618b540b0d
Create Date: 2025-09-28 09:07:58.277060

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1413e5cffd1"
down_revision: str | None = "eb618b540b0d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add creation tracking columns to user_connections table
    op.add_column(
        "user_connections",
        sa.Column(
            "creation_type",
            sa.String(20),
            nullable=False,
            server_default="manual",
            comment="Type of creation: automatic or manual",
        ),
    )
    op.add_column(
        "user_connections",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True,
            comment="User who created this connection (NULL for automatic creation)",
        ),
    )

    # Add foreign key constraint for created_by
    op.create_foreign_key(
        "fk_user_connections_created_by",
        "user_connections",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint(
        "fk_user_connections_created_by", "user_connections", type_="foreignkey"
    )

    # Remove columns
    op.drop_column("user_connections", "created_by")
    op.drop_column("user_connections", "creation_type")
