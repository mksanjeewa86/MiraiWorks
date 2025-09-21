"""migrate_to_messages_simple

Simple migration from direct_messages to messages table.
Handles existing foreign key constraints properly.

Revision ID: migrate_simple
Revises: a84ff39f6879
Create Date: 2025-09-21 03:10:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "migrate_simple"
down_revision: Union[str, None] = "a84ff39f6879"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Simple migration from direct_messages to messages table.
    """

    print("Starting simple migration to messages table...")

    # Step 1: Create backup of direct_messages if it exists
    try:
        op.execute("""
            CREATE TABLE IF NOT EXISTS direct_messages_backup AS
            SELECT * FROM direct_messages
        """)
        print("Backup of direct_messages created")
    except:
        print("No direct_messages table found to backup")

    # Step 2: Handle foreign key constraints on attachments table
    try:
        # First, check what foreign keys exist on attachments table
        op.execute("""
            SELECT
                CONSTRAINT_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = 'attachments'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)

        # Drop the foreign key constraint that references messages
        op.execute("ALTER TABLE attachments DROP FOREIGN KEY attachments_ibfk_1")
        print("Dropped foreign key constraint on attachments table")
    except Exception as e:
        print(f"No foreign key constraint to drop or error: {e}")

    # Step 3: Drop old tables
    try:
        op.execute("DROP TABLE IF EXISTS message_reads")
        op.execute("DROP TABLE IF EXISTS conversation_participants")
        op.execute("DROP TABLE IF EXISTS conversations")
        op.execute("DROP TABLE IF EXISTS messages")
        print("Dropped old conversation tables")
    except Exception as e:
        print(f"Error dropping tables: {e}")

    # Step 4: Create new messages table
    print("Creating new messages table...")
    op.create_table(
        "messages",
        # Core message fields
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="text"),

        # Message state
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted_by_sender", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted_by_recipient", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        # Reply functionality
        sa.Column("reply_to_id", sa.Integer(), nullable=True),

        # File attachments (inline)
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_type", sa.String(100), nullable=True),

        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),

        # Foreign keys
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reply_to_id"], ["messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Step 5: Create indexes
    print("Creating indexes...")
    op.create_index("idx_messages_sender_id", "messages", ["sender_id"])
    op.create_index("idx_messages_recipient_id", "messages", ["recipient_id"])
    op.create_index("idx_messages_is_read", "messages", ["is_read"])
    op.create_index("idx_messages_is_deleted", "messages", ["is_deleted"])
    op.create_index("idx_messages_created_at", "messages", ["created_at"])
    op.create_index("idx_messages_type", "messages", ["type"])
    op.create_index("idx_messages_sender_recipient", "messages", ["sender_id", "recipient_id"])
    op.create_index("idx_messages_recipient_unread", "messages", ["recipient_id", "is_read"])

    # Step 6: Migrate data from direct_messages if backup exists
    try:
        op.execute("""
            INSERT INTO messages (
                sender_id, recipient_id, content, type, is_read,
                is_deleted_by_sender, is_deleted_by_recipient, reply_to_id,
                file_url, file_name, file_size, file_type,
                created_at, read_at
            )
            SELECT
                sender_id, recipient_id, content, type, is_read,
                is_deleted_by_sender, is_deleted_by_recipient, reply_to_id,
                file_url, file_name, file_size, file_type,
                created_at, read_at
            FROM direct_messages_backup
            WHERE EXISTS (SELECT 1 FROM direct_messages_backup)
            ORDER BY created_at
        """)
        print("Migrated data from direct_messages_backup")
    except Exception as e:
        print(f"No data to migrate or error: {e}")

    # Step 7: Drop direct_messages table if it exists
    try:
        op.execute("DROP TABLE IF EXISTS direct_messages")
        print("Dropped direct_messages table")
    except Exception as e:
        print(f"Error dropping direct_messages: {e}")

    # Step 8: Recreate foreign key on attachments if needed
    try:
        # Add message_id column to attachments if it doesn't exist
        op.execute("""
            ALTER TABLE attachments
            ADD COLUMN IF NOT EXISTS message_id INTEGER
        """)

        # Create foreign key to messages
        op.execute("""
            ALTER TABLE attachments
            ADD CONSTRAINT attachments_message_fk
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
        """)
        print("Updated attachments table to reference messages")
    except Exception as e:
        print(f"Error updating attachments table: {e}")

    print("Migration completed successfully!")


def downgrade() -> None:
    """
    Revert back to direct_messages system.
    """

    print("Reverting to direct_messages system...")

    # Create backup of current messages data
    try:
        op.execute("""
            CREATE TABLE IF NOT EXISTS messages_backup AS
            SELECT * FROM messages
        """)
    except:
        pass

    # Drop messages table
    op.drop_table("messages")

    # Recreate direct_messages table
    op.create_table(
        "direct_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="text"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted_by_sender", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted_by_recipient", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reply_to_id", sa.Integer(), nullable=True),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_type", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reply_to_id"], ["direct_messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Restore data from backup
    try:
        op.execute("""
            INSERT INTO direct_messages
            SELECT sender_id, recipient_id, content, type, is_read,
                   is_deleted_by_sender, is_deleted_by_recipient, reply_to_id,
                   file_url, file_name, file_size, file_type,
                   created_at, read_at, id
            FROM direct_messages_backup
            WHERE EXISTS (SELECT 1 FROM direct_messages_backup)
        """)
    except:
        pass

    print("Downgrade completed!")