"""add_custom_is_randomized_to_exam_assignments

Revision ID: 4362115dcd78
Revises: 504e237d4188
Create Date: 2025-10-05 17:30:20.056002

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4362115dcd78"
down_revision: Union[str, None] = "504e237d4188"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add custom_is_randomized column to exam_assignments table
    op.add_column(
        "exam_assignments",
        sa.Column("custom_is_randomized", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    # Remove custom_is_randomized column from exam_assignments table
    op.drop_column("exam_assignments", "custom_is_randomized")
