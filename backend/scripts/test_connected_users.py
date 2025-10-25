"""Test that get_connected_users works with single connection record."""

import asyncio

from app.database import AsyncSessionLocal
from app.services.company_connection_service import company_connection_service


async def test_connected_users():
    """Test that users from both companies appear in each other's connected users."""
    async with AsyncSessionLocal() as db:
        # Get connected users for User 124 (Company 88)
        users_for_124 = await company_connection_service.get_connected_users(
            db=db, user_id=124
        )

        # Get connected users for User 129 (Company 90)
        users_for_129 = await company_connection_service.get_connected_users(
            db=db, user_id=129
        )

        print("=" * 60)
        print("Connected Users Test (Single Record)")
        print("=" * 60)
        print("\nUser 124 (Company 88) connected users:")
        for user in users_for_124:
            print(f"  - User {user.id}: {user.email} (Company {user.company_id})")

        print("\nUser 129 (Company 90) connected users:")
        for user in users_for_129:
            print(f"  - User {user.id}: {user.email} (Company {user.company_id})")

        # Check if User 129 is in User 124's connected users
        user_129_in_124 = any(u.id == 129 for u in users_for_124)

        # Check if User 124 is in User 129's connected users
        user_124_in_129 = any(u.id == 124 for u in users_for_129)

        print("\n" + "=" * 60)
        print(f"User 129 in User 124's connections: {user_129_in_124}")
        print(f"User 124 in User 129's connections: {user_124_in_129}")
        print("=" * 60)

        if user_129_in_124 and user_124_in_129:
            print("[SUCCESS] get_connected_users works with single record!")
            return True
        else:
            print("[FAILED] Connected users check failed!")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_connected_users())
    exit(0 if result else 1)
