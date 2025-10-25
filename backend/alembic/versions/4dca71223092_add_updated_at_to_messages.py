"""add_updated_at_to_messages

Revision ID: 4dca71223092
Revises: 45708fe415bb
Create Date: 2025-10-16 12:31:52.812723

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dca71223092"
down_revision: Union[str, None] = "45708fe415bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at column to messages table
    op.add_column(
        "messages",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # Add ON UPDATE trigger for MySQL
    op.execute(
        """
        ALTER TABLE messages
        MODIFY COLUMN updated_at DATETIME(6) NOT NULL
        DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6)
        """
    )


def downgrade() -> None:
    # Remove updated_at column from messages table
    op.drop_column("messages", "updated_at")
