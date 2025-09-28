"""add assignment fields to todos

Revision ID: manual_assignment_001
Revises: f1413e5cffd1
Create Date: 2025-09-28 00:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'manual_assignment_001'
down_revision: Union[str, None] = 'enhance_resume_system_japanese'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add assignment workflow fields to todos table
    op.add_column('todos', sa.Column('todo_type', sa.String(20), nullable=False, server_default='regular'))
    op.add_column('todos', sa.Column('publish_status', sa.String(20), nullable=False, server_default='published'))
    op.add_column('todos', sa.Column('assignment_status', sa.String(20), nullable=True))
    op.add_column('todos', sa.Column('assignment_assessment', sa.Text(), nullable=True))
    op.add_column('todos', sa.Column('assignment_score', sa.Integer(), nullable=True))
    op.add_column('todos', sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('todos', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('todos', sa.Column('reviewed_by', sa.Integer(), nullable=True))

    # Add foreign key constraint for reviewed_by
    op.create_foreign_key('fk_todos_reviewed_by', 'todos', 'users', ['reviewed_by'], ['id'], ondelete='SET NULL')

    # Add indexes
    op.create_index('ix_todos_todo_type', 'todos', ['todo_type'])
    op.create_index('ix_todos_publish_status', 'todos', ['publish_status'])
    op.create_index('ix_todos_assignment_status', 'todos', ['assignment_status'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_todos_assignment_status', 'todos')
    op.drop_index('ix_todos_publish_status', 'todos')
    op.drop_index('ix_todos_todo_type', 'todos')

    # Remove foreign key constraint
    op.drop_constraint('fk_todos_reviewed_by', 'todos', type_='foreignkey')

    # Remove columns
    op.drop_column('todos', 'reviewed_by')
    op.drop_column('todos', 'reviewed_at')
    op.drop_column('todos', 'submitted_at')
    op.drop_column('todos', 'assignment_score')
    op.drop_column('todos', 'assignment_assessment')
    op.drop_column('todos', 'assignment_status')
    op.drop_column('todos', 'publish_status')
    op.drop_column('todos', 'todo_type')