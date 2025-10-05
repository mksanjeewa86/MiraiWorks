"""add_soft_delete_to_interviews_and_processes

Revision ID: 3caefaa119d8
Revises: recruitment_workflow_001
Create Date: 2025-10-01 23:34:06.759708

"""
from typing import Sequence, Union

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

    # Add soft delete columns to recruitment_processes table
    op.add_column(
        "recruitment_processes",
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "recruitment_processes",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_recruitment_processes_is_deleted", "recruitment_processes", ["is_deleted"]
    )


def downgrade() -> None:
    # Remove soft delete columns from recruitment_processes table
    op.drop_index("ix_recruitment_processes_is_deleted", "recruitment_processes")
    op.drop_column("recruitment_processes", "deleted_at")
    op.drop_column("recruitment_processes", "is_deleted")

    # Remove soft delete columns from interviews table
    op.drop_index("ix_interviews_is_deleted", "interviews")
    op.drop_column("interviews", "deleted_at")
    op.drop_column("interviews", "is_deleted")
