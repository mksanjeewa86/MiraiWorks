#!/usr/bin/env python3
"""Test script to verify MySQL Docker setup works properly."""

import asyncio
import subprocess
import time
import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import os
os.environ["ENVIRONMENT"] = "test"

# Import models at module level
from app.database import Base
import app.models  # Import models module

async def main():
    print("Testing MySQL Docker setup for tests...")

    # Step 1: Start MySQL container
    print("\n1. Starting MySQL test container...")
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
            check=True,
            cwd=str(BACKEND_DIR.parent)
        )
        print("   SUCCESS: Container started")
    except subprocess.CalledProcessError as e:
        print(f"   ERROR: Failed to start container: {e}")
        return False

    # Step 2: Wait for MySQL to be ready
    print("\n2. Waiting for MySQL to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["docker", "exec", "miraiworks-mysql-test", "mysqladmin", "ping", "-h", "localhost", "-u", "changeme", "-pchangeme"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("   SUCCESS: MySQL is ready!")
                break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

        time.sleep(2)
        print(f"   Waiting... (attempt {attempt + 1}/{max_attempts})")
    else:
        print("   ERROR: MySQL failed to start within timeout")
        return False

    # Step 3: Test database connection
    print("\n3. Testing database connection...")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        TEST_DATABASE_URL = "mysql+asyncmy://changeme:changeme@localhost:3307/miraiworks_test"
        test_engine = create_async_engine(
            TEST_DATABASE_URL,
            pool_size=2,
            max_overflow=0,
            pool_pre_ping=True,
            pool_timeout=10,
            echo=False,
        )

        async with test_engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row[0] == 1:
                print("   SUCCESS: Database connection successful")
            else:
                print("   ERROR: Unexpected query result")
                return False

        await test_engine.dispose()

    except Exception as e:
        print(f"   ERROR: Database connection failed: {e}")
        return False

    # Step 4: Test table creation
    print("\n4. Testing table creation...")
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Check if tables were created
        async with test_engine.begin() as conn:
            result = await conn.execute("SHOW TABLES")
            tables = [row[0] for row in result.fetchall()]

        if 'users' in tables and 'companies' in tables:
            print(f"   SUCCESS: Tables created successfully ({len(tables)} tables)")
        else:
            print(f"   ERROR: Expected tables not found. Found: {tables}")
            return False

        await test_engine.dispose()

    except Exception as e:
        print(f"   ERROR: Table creation failed: {e}")
        return False

    # Step 5: Test simple todo attachment workflow
    print("\n5. Testing todo attachment workflow...")
    try:
        from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
        from app.services.auth_service import auth_service
        from app.utils.constants import CompanyType, UserRole as UserRoleEnum

        test_engine = create_async_engine(
            TEST_DATABASE_URL,
            pool_size=2,
            max_overflow=0,
            pool_pre_ping=True,
            pool_timeout=10,
            echo=False,
        )

        TestingSessionLocal = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with TestingSessionLocal() as session:
            # Create basic test data
            from app.models.company import Company
            from app.models.user import User
            from app.models.role import Role
            from app.models.user_role import UserRole

            # Create role
            role = Role(name=UserRoleEnum.EMPLOYER.value, description="Test employer role")
            session.add(role)
            await session.commit()
            await session.refresh(role)

            # Create company
            company = Company(
                name="Test Company",
                type=CompanyType.RECRUITER,
                email="test@company.com",
                phone="123-456-7890",
                is_active="1",
            )
            session.add(company)
            await session.commit()
            await session.refresh(company)

            # Create user
            user = User(
                email="test@example.com",
                first_name="Test",
                last_name="User",
                company_id=company.id,
                hashed_password=auth_service.get_password_hash("password123"),
                is_active=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            # Assign role
            user_role = UserRole(user_id=user.id, role_id=role.id)
            session.add(user_role)
            await session.commit()

            print(f"   SUCCESS: Test data created: User {user.id}, Company {company.id}")

        await test_engine.dispose()

    except Exception as e:
        print(f"   ERROR: Todo attachment workflow test failed: {e}")
        return False

    # Step 6: Clean up
    print("\n6. Cleaning up...")
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
            check=True,
            cwd=str(BACKEND_DIR.parent)
        )
        print("   SUCCESS: Cleanup completed")
    except subprocess.CalledProcessError as e:
        print(f"   WARNING: Cleanup warning: {e}")

    print("\nALL TESTS PASSED! MySQL Docker setup is working correctly.")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)