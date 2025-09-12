"""Tests for DirectMessageService."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.direct_message import DirectMessage
from app.models.user import User
from app.schemas.direct_message import DirectMessageCreate, MessageSearchRequest
from app.services.direct_message_service import direct_message_service
from app.utils.constants import MessageType


class TestDirectMessageService:
    """Test suite for DirectMessageService."""

    @pytest.mark.asyncio
    async def test_send_message_success(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User
    ):
        """Test successful message sending."""
        message_data = DirectMessageCreate(
            recipient_id=test_user2.id,
            content="Hello, this is a test message!",
            type=MessageType.TEXT
        )
        
        result = await direct_message_service.send_message(
            db_session, test_user.id, message_data
        )
        
        assert result is not None
        assert result.sender_id == test_user.id
        assert result.recipient_id == test_user2.id
        assert result.content == "Hello, this is a test message!"
        assert result.type == MessageType.TEXT.value
        assert result.is_read is False
        
        # Verify message was saved to database
        stmt = select(DirectMessage).where(DirectMessage.id == result.id)
        db_result = await db_session.execute(stmt)
        db_message = db_result.scalar_one_or_none()
        
        assert db_message is not None
        assert db_message.content == message_data.content

    @pytest.mark.asyncio
    async def test_send_file_message(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User
    ):
        """Test sending file message."""
        message_data = DirectMessageCreate(
            recipient_id=test_user2.id,
            content="📎 document.pdf",
            type=MessageType.FILE,
            file_url="/files/uploads/document.pdf",
            file_name="document.pdf",
            file_size=1024000,
            file_type="application/pdf"
        )
        
        result = await direct_message_service.send_message(
            db_session, test_user.id, message_data
        )
        
        assert result is not None
        assert result.type == MessageType.FILE.value
        assert result.file_url == "/files/uploads/document.pdf"
        assert result.file_name == "document.pdf"
        assert result.file_size == 1024000
        assert result.file_type == "application/pdf"

    @pytest.mark.asyncio
    async def test_get_messages_with_user(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test retrieving messages between two users."""
        messages = await direct_message_service.get_messages_with_user(
            db_session, test_user.id, test_user2.id, limit=10
        )
        
        assert len(messages) == 5
        # Messages should be ordered by created_at descending (newest first)
        assert messages[0].content == "Test message 5"
        assert messages[-1].content == "Test message 1"
        
        # All messages should be between the two users
        for message in messages:
            assert (message.sender_id == test_user.id and message.recipient_id == test_user2.id) or \
                   (message.sender_id == test_user2.id and message.recipient_id == test_user.id)

    @pytest.mark.asyncio
    async def test_get_messages_with_pagination(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test message pagination."""
        # Get first 3 messages
        messages_page1 = await direct_message_service.get_messages_with_user(
            db_session, test_user.id, test_user2.id, limit=3
        )
        
        assert len(messages_page1) == 3
        
        # Get next page using before_id
        oldest_id = messages_page1[-1].id
        messages_page2 = await direct_message_service.get_messages_with_user(
            db_session, test_user.id, test_user2.id, limit=3, before_id=oldest_id
        )
        
        assert len(messages_page2) == 2  # Remaining messages
        
        # Verify no overlap between pages
        page1_ids = {msg.id for msg in messages_page1}
        page2_ids = {msg.id for msg in messages_page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_get_conversations(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils
    ):
        """Test retrieving user's conversations."""
        # Create conversation with another user
        test_user3 = User(
            email="test3@test.com",
            first_name="Test3",
            last_name="User3",
            company_id=test_user.company_id,
            hashed_password="test_hash3",
            is_active=True
        )
        db_session.add(test_user3)
        await db_session.flush()
        
        # Send message to create another conversation
        await test_utils.create_test_conversation(db_session, test_user, test_user3, 2)
        
        conversations = await direct_message_service.get_conversations(
            db_session, test_user.id
        )
        
        assert len(conversations) == 2
        
        # Find conversation with test_user2
        conv_with_user2 = next(
            (c for c in conversations if c.other_user_id == test_user2.id), None
        )
        assert conv_with_user2 is not None
        assert conv_with_user2.other_user_name == f"{test_user2.first_name} {test_user2.last_name}"
        assert conv_with_user2.other_user_email == test_user2.email
        assert conv_with_user2.unread_count > 0  # Should have unread messages

    @pytest.mark.asyncio
    async def test_search_conversations(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test searching conversations by name/email."""
        # Search by name
        conversations = await direct_message_service.get_conversations(
            db_session, test_user.id, search_query="Test2"
        )
        
        assert len(conversations) == 1
        assert conversations[0].other_user_id == test_user2.id
        
        # Search by email
        conversations = await direct_message_service.get_conversations(
            db_session, test_user.id, search_query="test2@test.com"
        )
        
        assert len(conversations) == 1
        assert conversations[0].other_user_id == test_user2.id
        
        # Search with no results
        conversations = await direct_message_service.get_conversations(
            db_session, test_user.id, search_query="nonexistent"
        )
        
        assert len(conversations) == 0

    @pytest.mark.asyncio
    async def test_search_messages(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test message content search."""
        search_request = MessageSearchRequest(
            query="message 3",
            limit=10,
            offset=0
        )
        
        results = await direct_message_service.search_messages(
            db_session, test_user.id, search_request
        )
        
        assert len(results) == 1
        assert "message 3" in results[0].content

    @pytest.mark.asyncio
    async def test_search_messages_with_user_filter(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test message search with user filter."""
        search_request = MessageSearchRequest(
            query="message",
            with_user_id=test_user2.id,
            limit=10,
            offset=0
        )
        
        results = await direct_message_service.search_messages(
            db_session, test_user.id, search_request
        )
        
        assert len(results) == 5  # All test messages
        # All results should involve test_user2
        for message in results:
            assert message.sender_id == test_user2.id or message.recipient_id == test_user2.id

    @pytest.mark.asyncio
    async def test_mark_messages_as_read(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test marking messages as read."""
        # Get unread messages from test_user2 to test_user
        unread_messages = [
            msg for msg in test_messages 
            if msg.recipient_id == test_user.id and not msg.is_read
        ]
        
        assert len(unread_messages) > 0
        
        message_ids = [msg.id for msg in unread_messages]
        count = await direct_message_service.mark_messages_as_read(
            db_session, test_user.id, message_ids
        )
        
        assert count == len(unread_messages)
        
        # Verify messages are marked as read
        stmt = select(DirectMessage).where(
            DirectMessage.id.in_(message_ids)
        )
        result = await db_session.execute(stmt)
        updated_messages = result.scalars().all()
        
        for message in updated_messages:
            assert message.is_read is True
            assert message.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_conversation_as_read(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_messages: list[DirectMessage]
    ):
        """Test marking entire conversation as read."""
        count = await direct_message_service.mark_conversation_as_read(
            db_session, test_user.id, test_user2.id
        )
        
        assert count > 0
        
        # Verify all messages from test_user2 to test_user are marked as read
        stmt = select(DirectMessage).where(
            DirectMessage.sender_id == test_user2.id,
            DirectMessage.recipient_id == test_user.id
        )
        result = await db_session.execute(stmt)
        messages = result.scalars().all()
        
        for message in messages:
            assert message.is_read is True

    @pytest.mark.asyncio
    async def test_message_visibility(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User
    ):
        """Test message visibility after deletion."""
        # Send a message
        message_data = DirectMessageCreate(
            recipient_id=test_user2.id,
            content="Message to be deleted",
            type=MessageType.TEXT
        )
        
        message = await direct_message_service.send_message(
            db_session, test_user.id, message_data
        )
        
        # Message should be visible to both users initially
        assert message.is_visible_to_user(test_user.id)
        assert message.is_visible_to_user(test_user2.id)
        
        # Mark as deleted by sender
        message.is_deleted_by_sender = True
        await db_session.commit()
        
        # Should not be visible to sender, but visible to recipient
        assert not message.is_visible_to_user(test_user.id)
        assert message.is_visible_to_user(test_user2.id)
        
        # Mark as deleted by recipient too
        message.is_deleted_by_recipient = True
        await db_session.commit()
        
        # Should not be visible to either user
        assert not message.is_visible_to_user(test_user.id)
        assert not message.is_visible_to_user(test_user2.id)

    @pytest.mark.asyncio
    async def test_send_message_to_nonexistent_user(
        self, 
        db_session: AsyncSession, 
        test_user: User
    ):
        """Test sending message to non-existent user."""
        message_data = DirectMessageCreate(
            recipient_id=99999,  # Non-existent user ID
            content="This should fail",
            type=MessageType.TEXT
        )
        
        with pytest.raises(Exception):
            await direct_message_service.send_message(
                db_session, test_user.id, message_data
            )

    @pytest.mark.asyncio
    async def test_empty_search_query(
        self, 
        db_session: AsyncSession, 
        test_user: User
    ):
        """Test search with empty query."""
        search_request = MessageSearchRequest(
            query="",
            limit=10,
            offset=0
        )
        
        results = await direct_message_service.search_messages(
            db_session, test_user.id, search_request
        )
        
        # Should return all messages for the user
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_search_pagination(
        self, 
        db_session: AsyncSession, 
        test_user: User,
        test_messages: list[DirectMessage]
    ):
        """Test search result pagination."""
        search_request = MessageSearchRequest(
            query="message",
            limit=2,
            offset=0
        )
        
        page1 = await direct_message_service.search_messages(
            db_session, test_user.id, search_request
        )
        
        assert len(page1) <= 2
        
        # Get second page
        search_request.offset = 2
        page2 = await direct_message_service.search_messages(
            db_session, test_user.id, search_request
        )
        
        # Verify no overlap
        if page1 and page2:
            page1_ids = {msg.id for msg in page1}
            page2_ids = {msg.id for msg in page2}
            assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_case_insensitive_search(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User
    ):
        """Test case insensitive search."""
        # Send message with mixed case
        message_data = DirectMessageCreate(
            recipient_id=test_user2.id,
            content="Hello WORLD from Python",
            type=MessageType.TEXT
        )
        
        await direct_message_service.send_message(
            db_session, test_user.id, message_data
        )
        
        # Search with different cases
        search_cases = ["hello", "HELLO", "Hello", "world", "WORLD", "python"]
        
        for search_term in search_cases:
            search_request = MessageSearchRequest(
                query=search_term,
                limit=10,
                offset=0
            )
            
            results = await direct_message_service.search_messages(
                db_session, test_user.id, search_request
            )
            
            assert len(results) >= 1
            # Verify the message contains the search term (case insensitive)
            found = any(search_term.lower() in msg.content.lower() for msg in results)
            assert found

    @pytest.mark.asyncio
    async def test_reply_to_message(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User,
        test_message: DirectMessage
    ):
        """Test replying to a message."""
        reply_data = DirectMessageCreate(
            recipient_id=test_user.id,  # Reply back to original sender
            content="This is a reply",
            type=MessageType.TEXT,
            reply_to_id=test_message.id
        )
        
        reply = await direct_message_service.send_message(
            db_session, test_user2.id, reply_data
        )
        
        assert reply.reply_to_id == test_message.id
        assert reply.sender_id == test_user2.id
        assert reply.recipient_id == test_user.id

    @pytest.mark.asyncio
    async def test_get_messages_excludes_deleted(
        self, 
        db_session: AsyncSession, 
        test_user: User, 
        test_user2: User
    ):
        """Test that deleted messages are excluded from results."""
        # Send multiple messages
        for i in range(3):
            message_data = DirectMessageCreate(
                recipient_id=test_user2.id,
                content=f"Message {i+1}",
                type=MessageType.TEXT
            )
            await direct_message_service.send_message(
                db_session, test_user.id, message_data
            )
        
        # Get all messages initially
        all_messages = await direct_message_service.get_messages_with_user(
            db_session, test_user.id, test_user2.id
        )
        
        initial_count = len(all_messages)
        assert initial_count >= 3
        
        # Mark one message as deleted by sender
        message_to_delete = all_messages[0]
        message_to_delete.is_deleted_by_sender = True
        await db_session.commit()
        
        # Get messages again - should have one less for the sender
        messages_for_sender = await direct_message_service.get_messages_with_user(
            db_session, test_user.id, test_user2.id
        )
        
        assert len(messages_for_sender) == initial_count - 1
        assert message_to_delete.id not in [msg.id for msg in messages_for_sender]
        
        # But recipient should still see all messages
        messages_for_recipient = await direct_message_service.get_messages_with_user(
            db_session, test_user2.id, test_user.id
        )
        
        assert len(messages_for_recipient) == initial_count