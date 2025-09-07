"""migrate_to_direct_messages_system

Revision ID: 5dc8de319ce0
Revises: remove_duplicate_2fa
Create Date: 2025-09-07 08:34:29.420948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dc8de319ce0'
down_revision: Union[str, None] = 'remove_duplicate_2fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate from conversation-based messaging to direct user-to-user messaging."""
    
    # First, drop foreign key constraints that reference messages table
    # Check if attachments table exists and has foreign key to messages
    try:
        # Drop foreign key constraint from attachments to messages if it exists
        op.drop_constraint('attachments_ibfk_1', 'attachments', type_='foreignkey')
    except:
        pass
    
    # Now drop old messaging tables (in correct order due to foreign keys)
    # Use direct SQL to handle IF EXISTS
    op.execute('DROP TABLE IF EXISTS message_reads')
    op.execute('DROP TABLE IF EXISTS messages')
    op.execute('DROP TABLE IF EXISTS conversation_participants') 
    op.execute('DROP TABLE IF EXISTS conversations')
    
    # Create new direct_messages table
    op.create_table(
        'direct_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, server_default='text'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted_by_sender', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted_by_recipient', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reply_to_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reply_to_id'], ['direct_messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_direct_messages_sender_id', 'direct_messages', ['sender_id'])
    op.create_index('idx_direct_messages_recipient_id', 'direct_messages', ['recipient_id'])
    op.create_index('idx_direct_messages_is_read', 'direct_messages', ['is_read'])
    op.create_index('idx_direct_messages_reply_to_id', 'direct_messages', ['reply_to_id'])
    op.create_index('idx_direct_messages_created_at', 'direct_messages', ['created_at'])
    op.create_index('idx_direct_messages_type', 'direct_messages', ['type'])
    op.create_index('idx_direct_messages_sender_recipient', 'direct_messages', ['sender_id', 'recipient_id'])
    op.create_index('idx_direct_messages_recipient_unread', 'direct_messages', ['recipient_id', 'is_read', 'is_deleted_by_recipient'])
    
    # Update attachments table to reference direct_messages instead of messages
    try:
        # Add new column for direct message reference
        op.add_column('attachments', sa.Column('direct_message_id', sa.Integer(), nullable=True))
        # Create foreign key to direct_messages
        op.create_foreign_key('attachments_direct_message_fk', 'attachments', 'direct_messages', ['direct_message_id'], ['id'], ondelete='CASCADE')
        # Drop the old message_id column if it exists
        op.drop_column('attachments', 'message_id')
    except:
        # If attachments table doesn't exist or columns don't exist, continue
        pass


def downgrade() -> None:
    """Revert back to conversation-based messaging (this will lose data!)."""
    
    # Drop direct messages table
    op.drop_table('direct_messages')
    
    # Recreate old tables (minimal structure for downgrade)
    # Note: This is a destructive operation and will lose data
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('type', sa.String(50), nullable=False, server_default='direct'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'conversation_participants',
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('conversation_id', 'user_id')
    )
    
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, server_default='text'),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('edited_content', sa.Text(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reply_to_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reply_to_id'], ['messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'message_reads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'user_id')
    )