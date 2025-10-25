"""add_soft_delete_to_interviews_and_processes

Revision ID: 3caefaa119d8
Revises: recruitment_workflow_001
Create Date: 2025-10-01 23:34:06.759708

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3caefaa119d8"
down_revision: Union[str, None] = "recruitment_workflow_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add soft delete columns to interviews table
    op.add_column(
        "interviews",
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "interviews", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index("ix_interviews_is_deleted", "interviews", ["is_deleted"])

    # Add soft delete columns to workflows table
    op.add_column(
        "workflows",
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "workflows",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_workflows_is_deleted", "workflows", ["is_deleted"])


def downgrade() -> None:
    # Remove soft delete columns from workflows table
    op.drop_index("ix_workflows_is_deleted", "workflows")
    op.drop_column("workflows", "deleted_at")
    op.drop_column("workflows", "is_deleted")

    # Remove soft delete columns from interviews table
    op.drop_index("ix_interviews_is_deleted", "interviews")
    op.drop_column("interviews", "deleted_at")
    op.drop_column("interviews", "is_deleted")
