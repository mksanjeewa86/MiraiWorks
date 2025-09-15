import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.direct_message import DirectMessage
from app.models.role import Role, UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import MessageType, UserRole as UserRoleEnum


class TestDirectMessages:
    """Comprehensive tests for direct messages functionality."""

    @pytest_asyncio.fixture
    async def company_admin_user(self, db_session: AsyncSession, test_company: Company):
        """Create a company admin user for testing role-based messaging."""
        user = User(
            email="companyadmin@test.com",
            first_name="Company",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Add company admin role (check if exists first)
        from sqlalchemy import select
        result = await db_session.execute(select(Role).where(Role.name == "company_admin"))
        company_admin_role = result.scalar_one_or_none()
        if not company_admin_role:
            company_admin_role = Role(name="company_admin", description="Company Administrator")
            db_session.add(company_admin_role)
            await db_session.commit()
            await db_session.refresh(company_admin_role)

        user_role = UserRole(user_id=user.id, role_id=company_admin_role.id)
        db_session.add(user_role)
        await db_session.commit()

        return user

    @pytest_asyncio.fixture
    async def super_admin_user(self, db_session: AsyncSession, test_company: Company):
        """Create a super admin user for testing role-based messaging."""
        user = User(
            email="superadmin@test.com",
            first_name="Super",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Add super admin role (check if exists first)
        from sqlalchemy import select
        result = await db_session.execute(select(Role).where(Role.name == "super_admin"))
        super_admin_role = result.scalar_one_or_none()
        if not super_admin_role:
            super_admin_role = Role(name="super_admin", description="Super Administrator")
            db_session.add(super_admin_role)
            await db_session.commit()
            await db_session.refresh(super_admin_role)

        user_role = UserRole(user_id=user.id, role_id=super_admin_role.id)
        db_session.add(user_role)
        await db_session.commit()

        return user

    @pytest_asyncio.fixture
    async def other_user(self, db_session: AsyncSession, test_company: Company, test_roles: dict):
        """Create another regular user for testing."""
        user = User(
            email="other@test.com",
            first_name="Other",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assign recruiter role
        user_role = UserRole(
            user_id=user.id, role_id=test_roles[UserRoleEnum.RECRUITER.value].id
        )
        db_session.add(user_role)
        await db_session.commit()

        return user

    @pytest.mark.asyncio
    async def test_get_conversations_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test successful retrieval of conversations."""
        # Create messages between users
        message1 = DirectMessage(
            sender_id=test_user.id,
            recipient_id=other_user.id,
            content="Hello from test user",
            type=MessageType.TEXT.value,
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        message2 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Reply from other user",
            type=MessageType.TEXT.value,
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.add(message1)
        db_session.add(message2)
        await db_session.commit()

        response = await client.get(
            "/api/direct-messages/conversations",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversations" in data
        assert "total" in data
        assert isinstance(data["conversations"], list)
        assert data["total"] >= 1

        # Verify conversation content
        if data["conversations"]:
            conversation = data["conversations"][0]
            assert "other_user_id" in conversation
            assert "other_user_name" in conversation
            assert "other_user_email" in conversation
            assert "last_message" in conversation
            assert "unread_count" in conversation
            assert "last_activity" in conversation

    @pytest.mark.asyncio
    async def test_get_conversations_with_search(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test conversation search functionality."""
        # Create a message
        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=other_user.id,
            content="Test message",
            type=MessageType.TEXT.value
        )
        db_session.add(message)
        await db_session.commit()

        # Search for conversations
        response = await client.get(
            f"/api/direct-messages/conversations?search={other_user.first_name}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data

    @pytest.mark.asyncio
    async def test_get_conversations_unauthorized(self, client: AsyncClient):
        """Test conversations access without authentication fails."""
        response = await client.get("/api/direct-messages/conversations")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_messages_with_user_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test successful retrieval of messages with specific user."""
        # Create messages
        message1 = DirectMessage(
            sender_id=test_user.id,
            recipient_id=other_user.id,
            content="First message",
            type=MessageType.TEXT.value,
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        message2 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Second message",
            type=MessageType.TEXT.value,
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.add(message1)
        db_session.add(message2)
        await db_session.commit()

        response = await client.get(
            f"/api/direct-messages/with/{other_user.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "messages" in data
        assert "total" in data
        assert "has_more" in data
        assert isinstance(data["messages"], list)
        assert data["total"] >= 2

        # Verify message content
        if data["messages"]:
            message = data["messages"][0]
            assert "id" in message
            assert "sender_id" in message
            assert "recipient_id" in message
            assert "sender_name" in message
            assert "recipient_name" in message
            assert "content" in message
            assert "type" in message
            assert "is_read" in message
            assert "created_at" in message

    @pytest.mark.asyncio
    async def test_get_messages_with_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test message retrieval with pagination."""
        # Create multiple messages
        for i in range(10):
            message = DirectMessage(
                sender_id=test_user.id,
                recipient_id=other_user.id,
                content=f"Message {i}",
                type=MessageType.TEXT.value,
                created_at=datetime.utcnow() - timedelta(hours=i)
            )
            db_session.add(message)
        await db_session.commit()

        # Test with limit
        response = await client.get(
            f"/api/direct-messages/with/{other_user.id}?limit=5",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) <= 5

    @pytest.mark.asyncio
    async def test_get_messages_unauthorized(self, client: AsyncClient):
        """Test message retrieval without authentication fails."""
        response = await client.get("/api/direct-messages/with/1")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_send_message_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test successful message sending."""
        message_data = {
            "recipient_id": other_user.id,
            "content": "Test message",
            "type": "text"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["sender_id"] == test_user.id
        assert data["recipient_id"] == other_user.id
        assert data["content"] == message_data["content"]
        assert data["type"] == message_data["type"]
        assert data["is_read"] is False

    @pytest.mark.asyncio
    async def test_send_message_with_file(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test sending message with file attachment."""
        message_data = {
            "recipient_id": other_user.id,
            "content": "Message with file",
            "type": "file",
            "file_url": "https://test.com/file.pdf",
            "file_name": "document.pdf",
            "file_size": 1024,
            "file_type": "application/pdf"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["file_url"] == message_data["file_url"]
        assert data["file_name"] == message_data["file_name"]
        assert data["file_size"] == message_data["file_size"]
        assert data["file_type"] == message_data["file_type"]

    @pytest.mark.asyncio
    async def test_send_message_unauthorized(self, client: AsyncClient):
        """Test message sending without authentication fails."""
        message_data = {
            "recipient_id": 1,
            "content": "Test message"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_send_message_role_permission_super_admin_to_company_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        super_admin_user: User,
        company_admin_user: User
    ):
        """Test super admin can message company admin."""
        # Get auth headers for super admin
        access_token = auth_service.create_access_token(data={"sub": str(super_admin_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        message_data = {
            "recipient_id": company_admin_user.id,
            "content": "Super admin to company admin"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_send_message_role_permission_company_admin_to_super_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        super_admin_user: User,
        company_admin_user: User
    ):
        """Test company admin can message super admin."""
        # Get auth headers for company admin
        access_token = auth_service.create_access_token(data={"sub": str(company_admin_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        message_data = {
            "recipient_id": super_admin_user.id,
            "content": "Company admin to super admin"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_send_message_role_permission_forbidden(
        self,
        client: AsyncClient,
        auth_headers: dict,
        company_admin_user: User
    ):
        """Test regular user cannot message company admin."""
        message_data = {
            "recipient_id": company_admin_user.id,
            "content": "Regular user to company admin"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=auth_headers
        )

        assert response.status_code == 403
        error_detail = response.json()["detail"]
        assert "Only super admins can message company admins" in error_detail

    @pytest.mark.asyncio
    async def test_search_messages_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test successful message search."""
        # Create messages with searchable content
        message1 = DirectMessage(
            sender_id=test_user.id,
            recipient_id=other_user.id,
            content="This is a searchable message",
            type=MessageType.TEXT.value
        )
        message2 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Another message with different content",
            type=MessageType.TEXT.value
        )
        db_session.add(message1)
        db_session.add(message2)
        await db_session.commit()

        search_data = {
            "query": "searchable",
            "limit": 10,
            "offset": 0
        }

        response = await client.post(
            "/api/direct-messages/search",
            json=search_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "messages" in data
        assert "total" in data
        assert "has_more" in data

        # Should find at least one message
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_messages_with_user_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test message search with user filter."""
        # Create message
        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=other_user.id,
            content="Test message",
            type=MessageType.TEXT.value
        )
        db_session.add(message)
        await db_session.commit()

        search_data = {
            "with_user_id": other_user.id,
            "limit": 10,
            "offset": 0
        }

        response = await client.post(
            "/api/direct-messages/search",
            json=search_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data

    @pytest.mark.asyncio
    async def test_search_messages_unauthorized(self, client: AsyncClient):
        """Test message search without authentication fails."""
        search_data = {
            "query": "test",
            "limit": 10,
            "offset": 0
        }

        response = await client.post(
            "/api/direct-messages/search",
            json=search_data
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_mark_messages_as_read_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test successful marking of messages as read."""
        # Create unread messages
        message1 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Unread message 1",
            type=MessageType.TEXT.value,
            is_read=False
        )
        message2 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Unread message 2",
            type=MessageType.TEXT.value,
            is_read=False
        )
        db_session.add(message1)
        db_session.add(message2)
        await db_session.commit()
        await db_session.refresh(message1)
        await db_session.refresh(message2)

        read_data = {
            "message_ids": [message1.id, message2.id]
        }

        response = await client.put(
            "/api/direct-messages/mark-read",
            json=read_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Marked" in data["message"]

    @pytest.mark.asyncio
    async def test_mark_messages_as_read_unauthorized(self, client: AsyncClient):
        """Test marking messages as read without authentication fails."""
        read_data = {
            "message_ids": [1, 2]
        }

        response = await client.put(
            "/api/direct-messages/mark-read",
            json=read_data
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_mark_conversation_as_read_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test successful marking of conversation as read."""
        # Create unread messages from other user
        message1 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Unread message 1",
            type=MessageType.TEXT.value,
            is_read=False
        )
        message2 = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Unread message 2",
            type=MessageType.TEXT.value,
            is_read=False
        )
        db_session.add(message1)
        db_session.add(message2)
        await db_session.commit()

        response = await client.put(
            f"/api/direct-messages/mark-conversation-read/{other_user.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Marked" in data["message"]

    @pytest.mark.asyncio
    async def test_mark_conversation_as_read_unauthorized(self, client: AsyncClient):
        """Test marking conversation as read without authentication fails."""
        response = await client.put("/api/direct-messages/mark-conversation-read/1")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_message_participants_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        other_user: User
    ):
        """Test successful retrieval of message participants."""
        response = await client.get(
            "/api/direct-messages/participants",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "participants" in data
        assert isinstance(data["participants"], list)

        # Should include at least the other user
        if data["participants"]:
            participant = data["participants"][0]
            assert "id" in participant
            assert "email" in participant
            assert "full_name" in participant
            assert "company_name" in participant
            assert "is_online" in participant

    @pytest.mark.asyncio
    async def test_get_message_participants_with_query(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        other_user: User
    ):
        """Test message participants search with query."""
        response = await client.get(
            f"/api/direct-messages/participants?query={other_user.first_name}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "participants" in data

    @pytest.mark.asyncio
    async def test_get_message_participants_with_limit(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test message participants with custom limit."""
        response = await client.get(
            "/api/direct-messages/participants?limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["participants"]) <= 10

    @pytest.mark.asyncio
    async def test_get_message_participants_unauthorized(self, client: AsyncClient):
        """Test message participants access without authentication fails."""
        response = await client.get("/api/direct-messages/participants")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_message_with_reply_to(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test sending message as reply to another message."""
        # Create original message
        original_message = DirectMessage(
            sender_id=other_user.id,
            recipient_id=test_user.id,
            content="Original message",
            type=MessageType.TEXT.value
        )
        db_session.add(original_message)
        await db_session.commit()
        await db_session.refresh(original_message)

        # Send reply
        message_data = {
            "recipient_id": other_user.id,
            "content": "Reply message",
            "type": "text",
            "reply_to_id": original_message.id
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reply_to_id"] == original_message.id

    @pytest.mark.asyncio
    async def test_message_validation_empty_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user: User
    ):
        """Test message validation with empty content."""
        message_data = {
            "recipient_id": other_user.id,
            "content": "",
            "type": "text"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=auth_headers
        )

        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_message_validation_invalid_recipient(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test message sending to non-existent recipient."""
        message_data = {
            "recipient_id": 99999,  # Non-existent user
            "content": "Test message",
            "type": "text"
        }

        response = await client.post(
            "/api/direct-messages/send",
            json=message_data,
            headers=auth_headers
        )

        # Should fail with not found or forbidden
        assert response.status_code in [404, 403]

    @pytest.mark.asyncio
    async def test_search_messages_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test message search with pagination."""
        # Create multiple messages
        for i in range(20):
            message = DirectMessage(
                sender_id=test_user.id,
                recipient_id=other_user.id,
                content=f"Searchable message {i}",
                type=MessageType.TEXT.value
            )
            db_session.add(message)
        await db_session.commit()

        # Test first page
        search_data = {
            "query": "Searchable",
            "limit": 10,
            "offset": 0
        }

        response = await client.post(
            "/api/direct-messages/search",
            json=search_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) <= 10
        assert data["has_more"] in [True, False]

        # Test second page
        search_data["offset"] = 10

        response = await client.post(
            "/api/direct-messages/search",
            json=search_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) <= 10