"""remove_position_title_from_interviews

Revision ID: ca8a5ea17c8d
Revises: a8e7a8ce9c21
Create Date: 2025-11-15 03:45:39.061616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca8a5ea17c8d'
down_revision: Union[str, None] = 'a8e7a8ce9c21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove position_title column from interviews table
    op.drop_column('interviews', 'position_title')


def downgrade() -> None:
    # Add back position_title column if we need to rollback
    op.add_column('interviews', sa.Column('position_title', sa.String(255), nullable=True))