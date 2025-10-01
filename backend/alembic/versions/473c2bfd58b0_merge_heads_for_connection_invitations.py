"""Merge heads for connection invitations

Revision ID: 473c2bfd58b0
Revises: 5553901233eb, add_user_connections_simple
Create Date: 2025-09-27 23:41:03.469632

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '473c2bfd58b0'
down_revision: str | None = ('5553901233eb', 'add_user_connections_simple')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
