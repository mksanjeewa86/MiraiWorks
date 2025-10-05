"""merge_datetime_modernization_heads

Revision ID: 194a6252792a
Revises: rename_recruitment_to_workflow, 93a8434d5e0c
Create Date: 2025-10-05 10:32:47.468693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '194a6252792a'
down_revision: Union[str, None] = ('rename_recruitment_to_workflow', '93a8434d5e0c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass