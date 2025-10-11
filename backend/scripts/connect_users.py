"""Script to connect admin and candidate users."""
import asyncio
from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User
from app.services.user_connection_service import user_connection_service


async def connect_admin_and_candidate():
    """Connect admin@miraiworks.com and candidate@example.com."""
    async with async_session_maker() as db:
        # Get user IDs
        result = await db.execute(
            select(User.id, User.email).where(
                User.email.in_(['admin@miraiworks.com', 'candidate@example.com'])
            )
        )
        users = {email: user_id for user_id, email in result.all()}

        if 'admin@miraiworks.com' not in users:
            print("Error: admin@miraiworks.com not found")
            return

        if 'candidate@example.com' not in users:
            print("Error: candidate@example.com not found")
            return

        admin_id = users['admin@miraiworks.com']
        candidate_id = users['candidate@example.com']

        print(f"Admin ID: {admin_id}")
        print(f"Candidate ID: {candidate_id}")

        # Create connection
        try:
            connection = await user_connection_service.connect_users(
                db=db,
                user_id=admin_id,
                connected_user_id=candidate_id,
                creation_type="manual",
                created_by=admin_id
            )
            print(f"✓ Connection created successfully (ID: {connection.id})")
            print(f"  {users['admin@miraiworks.com']} <-> {users['candidate@example.com']}")
        except Exception as e:
            print(f"Error creating connection: {e}")


if __name__ == "__main__":
    asyncio.run(connect_admin_and_candidate())
