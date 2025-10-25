"""Test if admin@miraiworks.com can message recruiter@innovatelab.jp."""
import asyncio

from app.database import AsyncSessionLocal
from app.services.company_connection_service import company_connection_service


async def test_interaction():
    """Test if User 124 (admin@miraiworks.com) can message User 129 (recruiter@innovatelab.jp)."""
    async with AsyncSessionLocal() as db:
        # Test interaction
        can_interact = await company_connection_service.can_users_interact(
            db=db,
            user1_id=124,  # admin@miraiworks.com (Company 88)
            user2_id=129,  # recruiter@innovatelab.jp (Company 90)
        )

        print("=" * 60)
        print("User Interaction Test")
        print("=" * 60)
        print("User 124 (admin@miraiworks.com) -> User 129 (recruiter@innovatelab.jp)")
        print(f"Can interact: {can_interact}")
        print("=" * 60)

        if can_interact:
            print("[SUCCESS] Users can interact!")
        else:
            print("[FAILED] Users CANNOT interact!")
            print("\nDebugging:")

            # Get both users
            from sqlalchemy import select

            from app.models.user import User

            result = await db.execute(select(User).where(User.id.in_([124, 129])))
            users = result.scalars().all()

            for user in users:
                print(f"  User {user.id}: {user.email}, Company {user.company_id}")


if __name__ == "__main__":
    result = asyncio.run(test_interaction())
