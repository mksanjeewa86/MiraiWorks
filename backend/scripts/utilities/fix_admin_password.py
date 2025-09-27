#!/usr/bin/env python3
"""Fix admin user password hashes in the database"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update
from passlib.context import CryptContext

# Import models and config
from app.config import settings
from app.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


async def fix_admin_passwords():
    """Fix admin user password hashes"""
    # Create async engine
    engine = create_async_engine(settings.db_url, echo=True)

    # Create session maker
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("Fixing admin password hashes...")

            # Hash the passwords
            admin_hash = hash_password("admin123")
            ccc_hash = hash_password("password")

            print(f"Generated admin hash: {admin_hash}")
            print(f"Generated ccc hash: {ccc_hash}")

            # Update admin@example.com
            result1 = await session.execute(
                update(User)
                .where(User.email == "admin@example.com")
                .values(hashed_password=admin_hash)
            )

            # Update admin@ccc.com
            result2 = await session.execute(
                update(User)
                .where(User.email == "admin@ccc.com")
                .values(hashed_password=ccc_hash)
            )

            await session.commit()

            print(f"Updated {result1.rowcount} row(s) for admin@example.com")
            print(f"Updated {result2.rowcount} row(s) for admin@ccc.com")

            # Verify the updates
            admin_user = await session.execute(
                select(User).where(User.email == "admin@example.com")
            )
            admin = admin_user.scalar_one_or_none()

            if admin:
                verification = verify_password("admin123", admin.hashed_password)
                print(
                    f"Admin password verification: {'SUCCESS' if verification else 'FAILED'}"
                )

            ccc_user = await session.execute(
                select(User).where(User.email == "admin@ccc.com")
            )
            ccc = ccc_user.scalar_one_or_none()

            if ccc:
                verification = verify_password("password", ccc.hashed_password)
                print(
                    f"CCC admin password verification: {'SUCCESS' if verification else 'FAILED'}"
                )

        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_admin_passwords())
