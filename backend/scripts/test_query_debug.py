"""Debug the messages query."""
import asyncio

from sqlalchemy import and_, or_, select

from app.database import AsyncSessionLocal
from app.models.message import Message


async def test_query():
    """Test the actual query used by get_messages_with_user."""
    async with AsyncSessionLocal() as db:
        current_user_id = 124
        other_user_id = 129
        limit = 50

        print("=" * 60)
        print("Query Debug Test")
        print("=" * 60)

        # Build the exact same query as the service (without relationships)
        query = (
            select(Message)
            .where(
                or_(
                    and_(
                        Message.sender_id == current_user_id,
                        Message.recipient_id == other_user_id,
                        Message.is_deleted_by_sender is False,
                    ),
                    and_(
                        Message.sender_id == other_user_id,
                        Message.recipient_id == current_user_id,
                        Message.is_deleted_by_recipient is False,
                    ),
                )
            )
            .order_by(Message.created_at)
            .limit(limit)
        )

        print(f"Query: {query}")
        print("\n" + "=" * 60)

        result = await db.execute(query)
        messages = result.scalars().all()

        print(f"Found {len(messages)} messages:\n")

        for msg in messages:
            print(f"  Message {msg.id}: {msg.content}")

        print("=" * 60)

        # Also try a simpler query
        print("\nTrying simpler query without deletion flags:")
        simple_query = (
            select(Message)
            .where(
                or_(
                    and_(
                        Message.sender_id == current_user_id,
                        Message.recipient_id == other_user_id,
                    ),
                    and_(
                        Message.sender_id == other_user_id,
                        Message.recipient_id == current_user_id,
                    ),
                )
            )
            .order_by(Message.created_at)
        )

        result2 = await db.execute(simple_query)
        simple_messages = result2.scalars().all()

        print(f"Found {len(simple_messages)} messages with simple query:\n")

        for msg in simple_messages:
            print(
                f"  Message {msg.id}: sender={msg.sender_id}, recipient={msg.recipient_id}"
            )
            print(f"    is_deleted_by_sender: {msg.is_deleted_by_sender}")
            print(f"    is_deleted_by_recipient: {msg.is_deleted_by_recipient}")

        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_query())
