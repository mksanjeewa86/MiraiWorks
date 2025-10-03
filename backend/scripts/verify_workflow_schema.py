#!/usr/bin/env python3
"""
Verify workflow relationship schema in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine


async def verify_schema():
    """Verify that workflow relationships are properly set up in the database."""
    async with engine.connect() as conn:
        print("🔍 Verifying Workflow Relationship Schema...\n")
        
        # 1. Check interviews table
        print("1️⃣ Checking interviews table...")
        result = await conn.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'miraiworks' 
            AND TABLE_NAME = 'interviews' 
            AND COLUMN_NAME = 'workflow_id'
        """))
        interview_col = result.fetchone()
        
        if interview_col:
            print(f"  ✅ workflow_id column exists in interviews table")
            print(f"     Type: {interview_col[1]}, Nullable: {interview_col[2]}, Key: {interview_col[3]}")
        else:
            print("  ❌ workflow_id column NOT FOUND in interviews table")
        
        # Check foreign key
        result = await conn.execute(text("""
            SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME, DELETE_RULE
            FROM information_schema.REFERENTIAL_CONSTRAINTS
            WHERE TABLE_NAME = 'interviews' 
            AND CONSTRAINT_SCHEMA = 'miraiworks'
            AND REFERENCED_TABLE_NAME = 'recruitment_processes'
        """))
        interview_fk = result.fetchone()
        
        if interview_fk:
            print(f"  ✅ Foreign key to recruitment_processes exists")
            print(f"     Constraint: {interview_fk[0]}, On Delete: {interview_fk[2]}")
        else:
            print("  ❌ Foreign key to recruitment_processes NOT FOUND")
        
        # 2. Check todos table
        print("\n2️⃣ Checking todos table...")
        result = await conn.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'miraiworks' 
            AND TABLE_NAME = 'todos' 
            AND COLUMN_NAME = 'workflow_id'
        """))
        todo_col = result.fetchone()
        
        if todo_col:
            print(f"  ✅ workflow_id column exists in todos table")
            print(f"     Type: {todo_col[1]}, Nullable: {todo_col[2]}, Key: {todo_col[3]}")
        else:
            print("  ❌ workflow_id column NOT FOUND in todos table")
        
        # Check foreign key
        result = await conn.execute(text("""
            SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME, DELETE_RULE
            FROM information_schema.REFERENTIAL_CONSTRAINTS
            WHERE TABLE_NAME = 'todos' 
            AND CONSTRAINT_SCHEMA = 'miraiworks'
            AND REFERENCED_TABLE_NAME = 'recruitment_processes'
        """))
        todo_fk = result.fetchone()
        
        if todo_fk:
            print(f"  ✅ Foreign key to recruitment_processes exists")
            print(f"     Constraint: {todo_fk[0]}, On Delete: {todo_fk[2]}")
        else:
            print("  ❌ Foreign key to recruitment_processes NOT FOUND")
        
        # 3. Check indexes
        print("\n3️⃣ Checking indexes...")
        
        # Interview index
        result = await conn.execute(text("""
            SELECT INDEX_NAME, COLUMN_NAME
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'miraiworks' 
            AND TABLE_NAME = 'interviews' 
            AND COLUMN_NAME = 'workflow_id'
        """))
        interview_idx = result.fetchone()
        
        if interview_idx:
            print(f"  ✅ Index on interviews.workflow_id exists: {interview_idx[0]}")
        else:
            print("  ❌ Index on interviews.workflow_id NOT FOUND")
        
        # Todo index
        result = await conn.execute(text("""
            SELECT INDEX_NAME, COLUMN_NAME
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'miraiworks' 
            AND TABLE_NAME = 'todos' 
            AND COLUMN_NAME = 'workflow_id'
        """))
        todo_idx = result.fetchone()
        
        if todo_idx:
            print(f"  ✅ Index on todos.workflow_id exists: {todo_idx[0]}")
        else:
            print("  ❌ Index on todos.workflow_id NOT FOUND")
        
        # 4. Current migration status
        print("\n4️⃣ Checking migration status...")
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()
        
        if version:
            print(f"  ✅ Current migration: {version[0]}")
            if version[0] == 'e936f1f184f8':
                print("  ✅ Workflow relationships migration is applied!")
            else:
                print("  ⚠️  Different migration version is active")
        else:
            print("  ❌ No migration version found")
        
        print("\n✨ Schema verification complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("Workflow Relationship Schema Verification")
    print("=" * 60)
    asyncio.run(verify_schema())