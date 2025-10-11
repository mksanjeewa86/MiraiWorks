"""
Seed Notification Data Script

This script adds sample notifications to the database.
Run this script to populate the database with realistic notification examples.

USAGE:
    cd backend
    PYTHONPATH=. python scripts/seed_notifications.py
"""

import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("ENVIRONMENT", "development")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.seeds.notification_data import seed_notification_data


async def get_user_ids(db: AsyncSession) -> dict:
    """Get user IDs for seeding notifications."""
    print("   Fetching user IDs...")

    # Get any 3 users from the database to seed notifications
    result = await db.execute(select(User).limit(4))
    users = result.scalars().all()

    if len(users) < 3:
        print("   Warning: Not enough users found. Please run full seeding first.")
        print(f"   Found {len(users)} users, need at least 3")
        return None

    # Use the first 4 users for the different roles
    return {
        "user_ids": {
            "admin": users[0].id,
            "recruiter": users[1].id if len(users) > 1 else users[0].id,
            "candidate": users[2].id if len(users) > 2 else users[0].id,
            "hr_manager": users[3].id if len(users) > 3 else users[0].id,
        }
    }


async def main():
    """Main function to seed notification data."""
    print("\n" + "="*70)
    print("MiraiWorks - Notification Data Seeding")
    print("="*70 + "\n")

    try:
        async with AsyncSessionLocal() as db:
            print("[OK] Database connection established\n")

            # Get user IDs
            auth_result = await get_user_ids(db)

            if not auth_result:
                print("\n[ERROR] Seeding failed: Required users not found")
                print("   Please run the main seeding script first:")
                print("   PYTHONPATH=. python app/seeds/seed_data.py\n")
                return

            print("[OK] Found required users\n")

            # Seed notification data
            print("Seeding Notifications:")
            result = await seed_notification_data(db, auth_result)

            print("\n" + "="*70)
            print("Notification Seeding Summary:")
            print("="*70)
            print(f"[OK] Total notifications created: {result['notifications']}")
            print(f"  - Unread: {result['unread']}")
            print(f"  - Read: {result['read']}")
            print("\nNotification Types:")
            for notification_type, count in result['types'].items():
                print(f"  - {notification_type.replace('_', ' ').title()}: {count}")
            print("="*70 + "\n")

            print("[SUCCESS] Notification seeding completed successfully!\n")

    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
