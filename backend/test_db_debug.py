#!/usr/bin/env python3
"""Debug script to understand the database issue."""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Set test environment
os.environ["ENVIRONMENT"] = "test"

async def main():
    print("DEBUG: Debugging database setup...")

    # Import after setting environment
    from app.tests.conftest import test_engine, TestingSessionLocal
    from app.database import Base
    from app.models.user import User
    from app.models.company import Company
    from app.models.role import Role
    from sqlalchemy import text, select

    print(f"Database URL: {test_engine.url}")

    # Test 1: Create tables
    print("\nSTEP 1: Creating tables...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Check tables
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"   Created {len(tables)} tables")
        print(f"   Users table exists: {'users' in tables}")

    # Test 2: Test session
    print("\nSTEP 2: Testing database session...")
    async with TestingSessionLocal() as session:
        try:
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"   SUCCESS: Users query successful: {len(users)} users")
        except Exception as e:
            print(f"   ERROR: Users query failed: {e}")

    # Test 3: Create a user
    print("\nSTEP 3: Creating test user...")
    async with TestingSessionLocal() as session:
        try:
            # Create company first
            company = Company(
                name="Test Company",
                type="recruiter",
                email="test@company.com",
                phone="123-456-7890",
                is_active="1"
            )
            session.add(company)
            await session.commit()
            await session.refresh(company)
            print(f"   SUCCESS: Company created: {company.id}")

            # Create user
            from app.services.auth_service import auth_service
            user = User(
                email="debug@example.com",
                first_name="Debug",
                last_name="User",
                company_id=company.id,
                hashed_password=auth_service.get_password_hash("password123"),
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"   SUCCESS: User created: {user.id} - {user.email}")

        except Exception as e:
            print(f"   ERROR: User creation failed: {e}")
            await session.rollback()

    # Test 4: Query user
    print("\nSTEP 4: Querying created user...")
    async with TestingSessionLocal() as session:
        try:
            result = await session.execute(select(User).where(User.email == "debug@example.com"))
            user = result.scalar_one_or_none()
            if user:
                print(f"   SUCCESS: User found: {user.email}")
            else:
                print("   ERROR: User not found")
        except Exception as e:
            print(f"   ERROR: User query failed: {e}")

    print("\nDEBUG COMPLETE: Database debug finished!")

if __name__ == "__main__":
    asyncio.run(main())