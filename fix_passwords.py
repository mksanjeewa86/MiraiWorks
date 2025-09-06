#!/usr/bin/env python3
"""
Fix password hashes in the MiraiWorks database
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.auth_service import auth_service
from app.config import settings

async def fix_password_hashes():
    """Fix all password hashes in the database"""
    
    # Create async engine
    engine = create_async_engine(settings.db_url, echo=True)
    SessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        # Generate proper bcrypt hash for "password"
        correct_hash = auth_service.get_password_hash("password")
        print(f"Generated bcrypt hash: {correct_hash}")
        
        async with SessionLocal() as session:
            # Update all users with the correct hash
            result = await session.execute(
                text("""
                UPDATE users 
                SET hashed_password = :hash, updated_at = NOW()
                WHERE hashed_password IS NOT NULL
                """),
                {"hash": correct_hash}
            )
            
            await session.commit()
            print(f"Updated {result.rowcount} users")
            
            # Verify the update
            result = await session.execute(
                text("""
                SELECT email, LEFT(hashed_password, 30) as hash_prefix
                FROM users 
                WHERE hashed_password IS NOT NULL
                ORDER BY email
                """)
            )
            
            print("\nVerification:")
            for row in result:
                print(f"  {row.email}: {row.hash_prefix}...")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_password_hashes())