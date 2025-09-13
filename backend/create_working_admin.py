#!/usr/bin/env python3
"""Create a working admin user for testing"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, '/app')

from app.database import get_db_session
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.user_settings import UserSettings
from app.services.auth_service import AuthService
from sqlalchemy import select, update

async def create_working_admin():
    auth_service = AuthService()

    async for db in get_db_session():
        try:
            # First, let's update the existing admin user with a proper hash
            password_hash = auth_service.get_password_hash("admin123")

            # Update admin@example.com
            await db.execute(
                update(User)
                .where(User.email == "admin@example.com")
                .values(hashed_password=password_hash)
            )

            await db.commit()
            print("✅ Updated admin@example.com password to 'admin123'")

            # Also update admin@ccc.com
            await db.execute(
                update(User)
                .where(User.email == "admin@ccc.com")
                .values(hashed_password=password_hash)
            )

            await db.commit()
            print("✅ Updated admin@ccc.com password to 'admin123'")

            # Test the password
            result = await db.execute(select(User).where(User.email == "admin@example.com"))
            user = result.scalar_one_or_none()

            if user and auth_service.verify_password("admin123", user.hashed_password):
                print("✅ Password verification successful!")
            else:
                print("❌ Password verification failed!")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(create_working_admin())