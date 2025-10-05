"""migrate_to_messages_system

This migration switches from direct_messages to a simplified messages table system.
It removes all unnecessary conversation-related tables and creates a clean messages table.

Revision ID: migrate_to_messages
Revises: add_file_attachments
Create Date: 2025-09-21 02:50:00.000000

"""
import contextlib
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "migrate_to_messages"
down_revision: str | None = "a84ff39f6879"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Migrate from direct_messages to a simplified messages table.
    Remove all conversation-related tables and create a clean messages system.
    """

    # Step 1: Backup existing direct_messages data (optional - create temp table)
    print("Creating backup of direct_messages data...")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS direct_messages_backup AS
        SELECT * FROM direct_messages;
    """
    )

    # Step 2: Drop all conversation-related tables if they exist
    print("Removing conversation-related tables...")

    # Drop foreign key constraints first (if they exist)
    try:
        # Check if attachments table has foreign key to messages table
        op.execute(
            """
            DO $$
            BEGIN
                -- Drop foreign key constraint if it exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'attachments_ibfk_1'
                    AND table_name = 'attachments'
                ) THEN
                    ALTER TABLE attachments DROP FOREIGN KEY attachments_ibfk_1;
                END IF;
            EXCEPTION WHEN OTHERS THEN
                -- Ignore if constraint doesn't exist
                NULL;
            END $$;
        """
        )
    except:
        # Try alternative approach for MySQL
        with contextlib.suppress(Exception):
            op.execute("ALTER TABLE attachments DROP FOREIGN KEY attachments_ibfk_1")

    # Drop other foreign key constraints
    with contextlib.suppress(Exception):
        op.drop_constraint(
            "attachments_direct_message_fk", "attachments", type_="foreignkey"
        )

    # Drop tables in correct order (child tables first)
    op.execute("DROP TABLE IF EXISTS message_reads CASCADE")
    op.execute("DROP TABLE IF EXISTS conversation_participants CASCADE")
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")

    # Step 3: Create new simplified messages table
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
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "is_deleted_by_sender", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "is_deleted_by_recipient",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
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

    # Step 4: Create optimized indexes
    print("Creating indexes for performance...")
    op.create_index("idx_messages_sender_id", "messages", ["sender_id"])
    op.create_index("idx_messages_recipient_id", "messages", ["recipient_id"])
    op.create_index("idx_messages_is_read", "messages", ["is_read"])
    op.create_index("idx_messages_is_deleted", "messages", ["is_deleted"])
    op.create_index("idx_messages_reply_to_id", "messages", ["reply_to_id"])
    op.create_index("idx_messages_created_at", "messages", ["created_at"])
    op.create_index("idx_messages_type", "messages", ["type"])

    # Composite indexes for common queries
    op.create_index(
        "idx_messages_sender_recipient",
        "messages",
        ["sender_id", "recipient_id"],
    )
    op.create_index(
        "idx_messages_recipient_unread",
        "messages",
        ["recipient_id", "is_read", "is_deleted_by_recipient"],
    )
    op.create_index(
        "idx_messages_conversation_pair",
        "messages",
        ["sender_id", "recipient_id", "created_at"],
    )

    # Step 5: Migrate data from direct_messages to messages
    print("Migrating data from direct_messages to messages...")
    op.execute(
        """
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
        FROM direct_messages
        ORDER BY created_at;
    """
    )

    # Step 6: Drop direct_messages table
    print("Removing old direct_messages table...")
    op.drop_table("direct_messages")

    # Step 7: Update attachments table if it exists and references direct_messages
    try:
        # Check if attachments table has direct_message_id column
        op.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'attachments' AND column_name = 'direct_message_id'
                ) THEN
                    -- Add message_id column
                    ALTER TABLE attachments ADD COLUMN message_id INTEGER;

                    -- Create foreign key to messages
                    ALTER TABLE attachments
                    ADD CONSTRAINT attachments_message_fk
                    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE;

                    -- Drop old direct_message_id column
                    ALTER TABLE attachments DROP COLUMN direct_message_id;
                END IF;
            END $$;
        """
        )
    except:
        print("Attachments table update skipped (table may not exist)")
        pass

    print("Migration completed successfully!")


def downgrade() -> None:
    """
    Revert back to direct_messages system.
    WARNING: This will lose data if the backup table doesn't exist!
    """

    print("Reverting to direct_messages system...")

    # Create backup of current messages data
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS messages_backup AS
        SELECT * FROM messages;
    """
    )

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
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "is_deleted_by_sender", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "is_deleted_by_recipient",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("reply_to_id", sa.Integer(), nullable=True),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_type", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["reply_to_id"], ["direct_messages.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Restore data from backup if it exists
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'direct_messages_backup') THEN
                INSERT INTO direct_messages SELECT * FROM direct_messages_backup;
                DROP TABLE direct_messages_backup;
            END IF;
        END $$;
    """
    )

    # Recreate indexes
    op.create_index("idx_direct_messages_sender_id", "direct_messages", ["sender_id"])
    op.create_index(
        "idx_direct_messages_recipient_id", "direct_messages", ["recipient_id"]
    )
    op.create_index("idx_direct_messages_is_read", "direct_messages", ["is_read"])
    op.create_index(
        "idx_direct_messages_reply_to_id", "direct_messages", ["reply_to_id"]
    )
    op.create_index("idx_direct_messages_created_at", "direct_messages", ["created_at"])
    op.create_index("idx_direct_messages_type", "direct_messages", ["type"])
    op.create_index(
        "idx_direct_messages_sender_recipient",
        "direct_messages",
        ["sender_id", "recipient_id"],
    )
    op.create_index(
        "idx_direct_messages_recipient_unread",
        "direct_messages",
        ["recipient_id", "is_read", "is_deleted_by_recipient"],
    )

    print("Downgrade completed!")
