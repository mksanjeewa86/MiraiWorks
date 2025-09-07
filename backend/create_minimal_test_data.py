#!/usr/bin/env python3
"""
Minimal test data creation for E2E tests
Creates only essential data needed for testing, optimized for speed.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import init_db
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.company import Company
from app.services.auth_service import AuthService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_minimal_data():
    """Create minimal test data for E2E tests"""
    logger.info("Creating minimal test data...")
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        # Create essential test users only
        test_users = [
            {
                "email": "jobseeker@test.com",
                "password": "Password123!",
                "full_name": "John Doe",
                "role": "candidate"
            },
            {
                "email": "admin@miraiworks.com", 
                "password": "password",
                "full_name": "Super Admin",
                "role": "super_admin"
            },
            {
                "email": "admin@techcorp.com",
                "password": "password", 
                "full_name": "Alice Johnson",
                "role": "company_admin"
            }
        ]
        
        for user_data in test_users:
            try:
                await auth_service.register_user(
                    email=user_data["email"],
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    role_name=user_data["role"]
                )
                logger.info(f"Created user: {user_data['email']}")
            except Exception as e:
                logger.info(f"User {user_data['email']} might already exist: {e}")
        
        await session.commit()

async def main():
    """Main function to set up database and create test data"""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Create test data
        await create_minimal_data()
        
        logger.info("Minimal test data creation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error creating test data: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())