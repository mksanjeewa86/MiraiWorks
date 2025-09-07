"""
Migration script to clean old messaging tables and create new direct message structure.
Run this with: python migrations/clean_and_migrate_direct_messages.py
"""
import asyncio
import os
import sys

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, AsyncSessionLocal


async def clean_and_migrate():
    """Clean old messaging tables and create new direct message table."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("Cleaning old messaging tables...")
            
            # Drop old messaging tables in correct order (due to foreign keys)
            old_tables = [
                "message_reads",
                "messages", 
                "conversation_participants",
                "conversations"
            ]
            
            for table in old_tables:
                try:
                    await db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"   Dropped table: {table}")
                except Exception as e:
                    print(f"   Could not drop {table}: {e}")
            
            print("\nCreating new direct message table...")
            
            # Create new direct_messages table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS direct_messages (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                type VARCHAR(50) NOT NULL DEFAULT 'text',
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                is_deleted_by_sender BOOLEAN NOT NULL DEFAULT FALSE,
                is_deleted_by_recipient BOOLEAN NOT NULL DEFAULT FALSE,
                reply_to_id INTEGER REFERENCES direct_messages(id) ON DELETE SET NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                read_at TIMESTAMP WITH TIME ZONE
            )
            """
            
            # Separate index creation statements
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_sender_id ON direct_messages(sender_id)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_recipient_id ON direct_messages(recipient_id)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_is_read ON direct_messages(is_read)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_reply_to_id ON direct_messages(reply_to_id)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_created_at ON direct_messages(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_type ON direct_messages(type)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_sender_recipient ON direct_messages(sender_id, recipient_id)",
                "CREATE INDEX IF NOT EXISTS idx_direct_messages_recipient_unread ON direct_messages(recipient_id, is_read, is_deleted_by_recipient)"
            ]
            
            # Execute table creation
            await db.execute(text(create_table_sql))
            
            # Execute indexes
            for index_sql in indexes_sql:
                await db.execute(text(index_sql))
            
            await db.commit()
            print("   Created direct_messages table with indexes")
            
            print("\nMigration completed successfully!")
            print("\nNew table structure:")
            print("direct_messages")
            print("   - id (Primary Key)")
            print("   - sender_id → users(id)")
            print("   - recipient_id → users(id)")
            print("   - content (Message text)")
            print("   - type (text, file, system)")
            print("   - is_read (Boolean)")
            print("   - is_deleted_by_sender (Boolean)")
            print("   - is_deleted_by_recipient (Boolean)")
            print("   - reply_to_id → direct_messages(id)")
            print("   - created_at (Timestamp)")
            print("   - read_at (Timestamp)")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
    
    await engine.dispose()


if __name__ == "__main__":
    print("Starting database migration for direct messages...")
    print("WARNING: This will DELETE all existing conversations and messages!")
    
    confirm = input("Do you want to continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    asyncio.run(clean_and_migrate())