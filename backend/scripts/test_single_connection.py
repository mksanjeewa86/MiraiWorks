"""Test that single bidirectional connection record works correctly."""

import asyncio

from app.database import AsyncSessionLocal
from app.services.company_connection_service import company_connection_service


async def test_bidirectional_connection():
    """Test that users from both companies can interact with single connection record."""
    async with AsyncSessionLocal() as db:
        # Test User 124 (Company 88) -> User 129 (Company 90)
        can_124_to_129 = await company_connection_service.can_users_interact(
            db=db, user1_id=124, user2_id=129
        )

        # Test User 129 (Company 90) -> User 124 (Company 88)
        can_129_to_124 = await company_connection_service.can_users_interact(
            db=db, user1_id=129, user2_id=124
        )

        print("=" * 60)
        print("Bidirectional Connection Test (Single Record)")
        print("=" * 60)
        print(f"User 124 (Company 88) -> User 129 (Company 90): {can_124_to_129}")
        print(f"User 129 (Company 90) -> User 124 (Company 88): {can_129_to_124}")
        print("=" * 60)

        if can_124_to_129 and can_129_to_124:
            print("[SUCCESS] Bidirectional connection works with single record!")
            return True
        else:
            print("[FAILED] Connection check failed!")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_bidirectional_connection())
    exit(0 if result else 1)
