"""Reset test database to match current models."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import os

os.environ["ENVIRONMENT"] = "test"

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import Base

# Import all models
from app.models import *

# Test database URL
TEST_DATABASE_URL = "mysql+asyncmy://changeme:changeme@localhost:3307/miraiworks_test"

async def reset_database():
    """Drop all tables and recreate from current models."""
    print("Connecting to test database...")
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            print("Dropping all existing tables...")

            # Disable foreign key checks
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

            # Get all tables
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]

            # Drop each table
            for table in tables:
                print(f"  Dropping table: {table}")
                await conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))

            # Re-enable foreign key checks
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

            print(f"Dropped {len(tables)} tables")

        # Create all tables from models
        async with engine.begin() as conn:
            print("Creating tables from current models...")
            await conn.run_sync(Base.metadata.create_all)

            # Verify tables were created
            result = await conn.execute(text("SHOW TABLES"))
            new_tables = [row[0] for row in result.fetchall()]
            print(f"Created {len(new_tables)} tables")

            # Show todos table structure to verify
            result = await conn.execute(text("DESCRIBE todos"))
            print("\nTodos table columns:")
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]}")

        print("\n✅ Test database reset successfully!")

    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_database())
