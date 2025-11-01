"""Merge migration heads

Revision ID: 8cdd14038b87
Revises: 9b7c8d5e4f2a, b2c3d4e5f6g7
Create Date: 2025-10-14 13:58:33.711893

"""
from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = "8cdd14038b87"
down_revision: Union[str, None] = ("9b7c8d5e4f2a", "b2c3d4e5f6g7")  # type: ignore[assignment]
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
