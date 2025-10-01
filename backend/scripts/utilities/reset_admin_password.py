#!/usr/bin/env python3
"""Reset admin user password for MiraiWorks"""

import asyncio

from passlib.context import CryptContext


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


async def main():
    # Test the existing hash
    existing_hash = "$2b$12$sYzasgJpUM2e926yAk9P6.8q7lyHnntI3j/ElsXstY5Fje1dRIoK6"
    test_password = "adminpassword123"

    print(f"Testing password: {test_password}")
    print(f"Against hash: {existing_hash}")
    print(f"Verification result: {verify_password(test_password, existing_hash)}")

    # Generate new hash
    new_hash = hash_password(test_password)
    print(f"New hash: {new_hash}")
    print(f"New hash verification: {verify_password(test_password, new_hash)}")


if __name__ == "__main__":
    asyncio.run(main())
