#!/usr/bin/env python3
"""
Debug script for specific temporary password issue
"""

import asyncio
import sys
sys.path.insert(0, './backend')

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.database import get_db
from app.models.user import User
from app.services.auth_service import auth_service

async def debug_specific_user():
    """Debug the specific user and password."""

    print("Debugging Specific User Account")
    print("=" * 50)

    email = "ssss@aaa.com"
    temp_password = "bOPxIYY1OWde"

    print(f"Email: {email}")
    print(f"Temp Password: '{temp_password}'")
    print(f"Password Length: {len(temp_password)}")

    # Get a database session
    async for db_session in get_db():
        try:
            print("\n1. Checking user in database...")

            # Find the user
            result = await db_session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                print(f"ERROR: No user found with email {email}")
                return False

            print(f"SUCCESS: User found - ID: {user.id}")
            print(f"User Details:")
            print(f"  - Name: {user.first_name} {user.last_name}")
            print(f"  - Active: {user.is_active}")
            print(f"  - Admin: {user.is_admin}")
            print(f"  - Created: {user.created_at}")
            print(f"  - Updated: {user.updated_at}")
            print(f"  - Has Password: {bool(user.hashed_password)}")

            if user.is_active:
                print("WARNING: User is already active! This might be the issue.")
                print("Solution: User account is already activated.")
                return False

            if not user.hashed_password:
                print("ERROR: User has no hashed password set!")
                print("Solution: Admin needs to reset temporary password.")
                return False

            print("\n2. Testing password verification...")

            # Test the exact password
            is_valid = auth_service.verify_password(temp_password, user.hashed_password)
            print(f"Password verification result: {is_valid}")

            if not is_valid:
                print("ERROR: Password does not match what's stored in database!")
                print("Possible causes:")
                print("1. Temporary password was changed/reset after email was sent")
                print("2. Different password was stored than what was emailed")
                print("3. Password corruption during storage")

                # Test some variations
                print("\n3. Testing password variations...")
                variations = [
                    temp_password,
                    temp_password.strip(),
                    temp_password.lower(),
                    temp_password.upper(),
                ]

                for variation in variations:
                    result = auth_service.verify_password(variation, user.hashed_password)
                    status = "MATCH" if result else "NO MATCH"
                    print(f"  '{variation}' -> {status}")

                return False
            else:
                print("SUCCESS: Password matches database!")
                print("The password verification should work.")

            print("\n4. Testing full activation API...")

            async with AsyncClient(app=app, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/activate",
                    json={
                        "userId": user.id,
                        "email": email,
                        "temporaryPassword": temp_password,
                        "newPassword": "Password@123"
                    }
                )

                print(f"API Response Status: {response.status_code}")

                if response.status_code == 200:
                    print("SUCCESS: Activation API works!")
                    data = response.json()
                    print(f"Response: {data.get('message', 'No message')}")
                    return True
                else:
                    print("ERROR: Activation API failed!")
                    try:
                        error_data = response.json()
                        print(f"Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        print(f"Raw response: {response.text}")
                    return False

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await db_session.rollback()
            break

if __name__ == "__main__":
    success = asyncio.run(debug_specific_user())
    if success:
        print("\nCONCLUSION: Activation should work with these credentials")
    else:
        print("\nCONCLUSION: There's an issue that needs admin attention")