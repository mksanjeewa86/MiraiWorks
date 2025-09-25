"""merge multiple heads

Revision ID: 5553901233eb
Revises: add_mbti_tables, add_todo_attachments, b0df91bde9c0, enhance_resume_system_japanese
Create Date: 2025-09-25 23:58:07.945932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5553901233eb'
down_revision: Union[str, None] = ('add_mbti_tables', 'add_todo_attachments', 'b0df91bde9c0', 'enhance_resume_system_japanese')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass