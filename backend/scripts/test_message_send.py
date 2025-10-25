"""Test message sending validation."""
import asyncio

from app.database import AsyncSessionLocal
from app.schemas.message import MessageCreate
from app.services.message_service import message_service


async def test_message_send():
    """Test if User 124 can send message to User 129."""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("Message Send Test")
        print("=" * 60)
        print("Sender: User 124 (admin@miraiworks.com)")
        print("Recipient: User 129 (recruiter@innovatelab.jp)")
        print("=" * 60)

        # Create test message data
        message_data = MessageCreate(
            recipient_id=129,
            content="Test message from admin to recruiter",
            type="text",
        )

        try:
            # Try to send message
            message = await message_service.send_message(
                db=db, sender_id=124, message_data=message_data
            )

            print("[SUCCESS] Message sent successfully!")
            print(f"Message ID: {message.id}")
            print(f"Content: {message.content}")
            print("=" * 60)
            return True

        except Exception as e:
            print("[FAILED] Message send failed!")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print("=" * 60)
            return False


if __name__ == "__main__":
    result = asyncio.run(test_message_send())
    exit(0 if result else 1)
