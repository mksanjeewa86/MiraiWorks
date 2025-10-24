"""add_soft_delete_to_todo_related_tables

Revision ID: 975879a174e7
Revises: bc0f5b6b4147
Create Date: 2025-10-24 14:06:49.716523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '975879a174e7'
down_revision: Union[str, None] = 'bc0f5b6b4147'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add soft delete fields to todo_attachments
    op.add_column('todo_attachments', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('todo_attachments', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('todo_attachments', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_todo_attachments_is_deleted'), 'todo_attachments', ['is_deleted'], unique=False)
    op.create_foreign_key('fk_todo_attachments_deleted_by', 'todo_attachments', 'users', ['deleted_by'], ['id'], ondelete='SET NULL')

    # Add soft delete fields to todo_extension_requests
    op.add_column('todo_extension_requests', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('todo_extension_requests', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('todo_extension_requests', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_todo_extension_requests_is_deleted'), 'todo_extension_requests', ['is_deleted'], unique=False)
    op.create_foreign_key('fk_todo_extension_requests_deleted_by', 'todo_extension_requests', 'users', ['deleted_by'], ['id'], ondelete='SET NULL')

    # Add soft delete fields to todo_viewers (if table exists)
    # Check if table exists first
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if 'todo_viewers' in inspector.get_table_names():
        op.add_column('todo_viewers', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'))
        op.add_column('todo_viewers', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
        op.add_column('todo_viewers', sa.Column('deleted_by', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_todo_viewers_is_deleted'), 'todo_viewers', ['is_deleted'], unique=False)
        op.create_foreign_key('fk_todo_viewers_deleted_by', 'todo_viewers', 'users', ['deleted_by'], ['id'], ondelete='SET NULL')

    # Add soft delete fields to todo_viewer_memos (if table exists)
    if 'todo_viewer_memos' in inspector.get_table_names():
        op.add_column('todo_viewer_memos', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'))
        op.add_column('todo_viewer_memos', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
        op.add_column('todo_viewer_memos', sa.Column('deleted_by', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_todo_viewer_memos_is_deleted'), 'todo_viewer_memos', ['is_deleted'], unique=False)
        op.create_foreign_key('fk_todo_viewer_memos_deleted_by', 'todo_viewer_memos', 'users', ['deleted_by'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Drop soft delete fields from todo_viewer_memos
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if 'todo_viewer_memos' in inspector.get_table_names():
        op.drop_constraint('fk_todo_viewer_memos_deleted_by', 'todo_viewer_memos', type_='foreignkey')
        op.drop_index(op.f('ix_todo_viewer_memos_is_deleted'), table_name='todo_viewer_memos')
        op.drop_column('todo_viewer_memos', 'deleted_by')
        op.drop_column('todo_viewer_memos', 'deleted_at')
        op.drop_column('todo_viewer_memos', 'is_deleted')

    # Drop soft delete fields from todo_viewers
    if 'todo_viewers' in inspector.get_table_names():
        op.drop_constraint('fk_todo_viewers_deleted_by', 'todo_viewers', type_='foreignkey')
        op.drop_index(op.f('ix_todo_viewers_is_deleted'), table_name='todo_viewers')
        op.drop_column('todo_viewers', 'deleted_by')
        op.drop_column('todo_viewers', 'deleted_at')
        op.drop_column('todo_viewers', 'is_deleted')

    # Drop soft delete fields from todo_extension_requests
    op.drop_constraint('fk_todo_extension_requests_deleted_by', 'todo_extension_requests', type_='foreignkey')
    op.drop_index(op.f('ix_todo_extension_requests_is_deleted'), table_name='todo_extension_requests')
    op.drop_column('todo_extension_requests', 'deleted_by')
    op.drop_column('todo_extension_requests', 'deleted_at')
    op.drop_column('todo_extension_requests', 'is_deleted')

    # Drop soft delete fields from todo_attachments
    op.drop_constraint('fk_todo_attachments_deleted_by', 'todo_attachments', type_='foreignkey')
    op.drop_index(op.f('ix_todo_attachments_is_deleted'), table_name='todo_attachments')
    op.drop_column('todo_attachments', 'deleted_by')
    op.drop_column('todo_attachments', 'deleted_at')
    op.drop_column('todo_attachments', 'is_deleted')
