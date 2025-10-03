#!/usr/bin/env python3
"""
Create database schema from SQLAlchemy models.
This bypasses alembic migrations and creates tables directly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine
from app.models.base import Base

# Import all models to ensure they're registered
import app.models.user
import app.models.role
import app.models.resume
import app.models.company
import app.models.position
import app.models.interview
import app.models.user_settings
import app.models.todo
import app.models.recruitment_process
import app.models.interview_note
import app.models.mbti_model
import app.models.holiday
import app.models.calendar_event
import app.models.user_connection
import app.models.connection_invitation
import app.models.message
import app.models.video_call
import app.models.todo_attachment
import app.models.exam
import app.models.process_node
import app.models.candidate_process


async def create_schema():
    """Create all tables from SQLAlchemy models."""
    print("Creating database schema...")
    
    async with engine.begin() as conn:
        # Drop all existing tables to start fresh (be careful!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Create alembic version table and set to latest migration
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL PRIMARY KEY
            )
        """))
        
        # Set to the latest migration version
        await conn.execute(text("""
            INSERT INTO alembic_version (version_num) 
            VALUES ('e936f1f184f8')
            ON DUPLICATE KEY UPDATE version_num = 'e936f1f184f8'
        """))
        
        print("Schema created successfully!")
        print("Alembic version set to: e936f1f184f8")


if __name__ == "__main__":
    asyncio.run(create_schema())