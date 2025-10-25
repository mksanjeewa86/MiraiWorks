"""Test GET messages API endpoint."""

import asyncio

from app.database import AsyncSessionLocal
from app.services.message_service import message_service


async def test_get_messages():
    """Test getting messages between User 124 and User 129."""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("GET Messages API Test")
        print("=" * 60)
        print("User 124 (admin@miraiworks.com) → User 129 (recruiter@innovatelab.jp)")
        print("=" * 60)

        # Get messages
        messages = await message_service.get_messages_with_user(
            db=db, current_user_id=124, other_user_id=129, limit=50
        )

        print(f"\nFound {len(messages)} messages:\n")

        for msg in messages:
            sender_name = msg.sender.first_name if msg.sender else "Unknown"
            print(f"  Message {msg.id}:")
            print(f"    From: {sender_name} (User {msg.sender_id})")
            print(f"    To: User {msg.recipient_id}")
            print(f"    Content: {msg.content}")
            print(f"    Created: {msg.created_at}")
            print()

        print("=" * 60)

        if len(messages) > 0:
            print(f"[SUCCESS] Found {len(messages)} messages!")
        else:
            print("[FAILED] No messages found!")

        return len(messages) > 0


if __name__ == "__main__":
    result = asyncio.run(test_get_messages())
    exit(0 if result else 1)
