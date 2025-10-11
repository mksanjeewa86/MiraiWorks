"""Test the /api/user/connections/my-connections endpoint."""
import asyncio
from app.database import AsyncSessionLocal
from app.services.company_connection_service import company_connection_service


async def test_connected_users_api():
    """Test getting connected users for User 124 (admin@miraiworks.com)."""
    async with AsyncSessionLocal() as db:
        # Get connected users for User 124 (Company 88)
        connected_users = await company_connection_service.get_connected_users(
            db=db,
            user_id=124
        )

        print("=" * 60)
        print("Connected Users API Test")
        print("=" * 60)
        print(f"User 124 (admin@miraiworks.com, Company 88)")
        print(f"Found {len(connected_users)} connected users:\n")

        for user in connected_users:
            print(f"  - User {user.id}: {user.email} (Company {user.company_id})")

        print("\n" + "=" * 60)

        # Check if User 129 is in the list
        user_129_found = any(u.id == 129 for u in connected_users)
        print(f"User 129 (recruiter@innovatelab.jp) in connected users: {user_129_found}")

        if user_129_found:
            print("[SUCCESS] User 129 is in the connected users list!")
        else:
            print("[FAILED] User 129 is NOT in the connected users list!")
            print("\nThis explains why the frontend doesn't show them in contacts!")

        print("=" * 60)

        return user_129_found


if __name__ == "__main__":
    result = asyncio.run(test_connected_users_api())
    exit(0 if result else 1)
