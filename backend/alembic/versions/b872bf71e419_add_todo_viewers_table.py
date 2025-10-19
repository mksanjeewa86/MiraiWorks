"""add_todo_viewers_table

Revision ID: b872bf71e419
Revises: d5fb4c228327
Create Date: 2025-10-19 08:50:23.090596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b872bf71e419'
down_revision: Union[str, None] = 'd5fb4c228327'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create todo_viewers table
    op.create_table(
        'todo_viewers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('todo_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('added_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['todo_id'], ['todos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['added_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_todo_viewers_id'), 'todo_viewers', ['id'], unique=False)
    op.create_index(op.f('ix_todo_viewers_todo_id'), 'todo_viewers', ['todo_id'], unique=False)
    op.create_index(op.f('ix_todo_viewers_user_id'), 'todo_viewers', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop todo_viewers table
    op.drop_index(op.f('ix_todo_viewers_user_id'), table_name='todo_viewers')
    op.drop_index(op.f('ix_todo_viewers_todo_id'), table_name='todo_viewers')
    op.drop_index(op.f('ix_todo_viewers_id'), table_name='todo_viewers')
    op.drop_table('todo_viewers')