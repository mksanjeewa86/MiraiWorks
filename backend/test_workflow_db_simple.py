#!/usr/bin/env python3
"""
Simple workflow database test to verify pytest with database.
"""

import pytest
import os
from pathlib import Path

# Set up environment
os.environ["ENVIRONMENT"] = "test"

# Add project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test basic database connection through pytest fixtures."""
    
    # Test basic query
    result = await db_session.execute(text("SELECT 1 as test"))
    row = result.fetchone()
    
    assert row[0] == 1
    print(f"✅ Database connection test passed: {row[0]}")
    
    # Test table existence
    result = await db_session.execute(text("SHOW TABLES LIKE 'recruitment_processes'"))
    tables = result.fetchall()
    
    assert len(tables) > 0
    print(f"✅ Found recruitment_processes table")
    
    # Test workflow-related tables
    tables_to_check = ['recruitment_processes', 'interviews', 'todos']
    for table_name in tables_to_check:
        result = await db_session.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
        tables = result.fetchall()
        assert len(tables) > 0, f"Table {table_name} not found"
        print(f"✅ Found {table_name} table")
    
    print("🎉 All database tests passed!")


if __name__ == "__main__":
    # Run pytest on this file
    pytest.main([__file__, "-v", "-s"])