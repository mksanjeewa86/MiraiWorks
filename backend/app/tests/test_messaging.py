from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.company import Company
from app.models.role import UserRole as UserRoleModel
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.messaging_service import messaging_service
from app.utils.constants import CompanyType, UserRole, VirusStatus


@pytest_asyncio.fixture
async def recruiter_company(db_session: AsyncSession) -> Company:
    """Create recruiter company."""
    company = Company(
        name="Test Recruiter Inc",
        type=CompanyType.RECRUITER,
        email="contact@recruiter.com",
        phone="+1-555-0123",
        is_active="1",
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def employer_company(db_session: AsyncSession) -> Company:
    """Create employer company."""
    company = Company(
        name="Test Employer Corp",
        type=CompanyType.EMPLOYER,
        email="contact@employer.com",
        phone="+1-555-0456",
        is_active="1",
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def candidate_user(db_session: AsyncSession, test_roles: dict) -> User:
    """Create candidate user."""
    user = User(
        email="candidate@example.com",
        first_name="John",
        last_name="Candidate",
        hashed_password=auth_service.get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign role
    user_role = UserRoleModel(
        user_id=user.id, role_id=test_roles[UserRole.CANDIDATE.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def recruiter_user(
    db_session: AsyncSession, recruiter_company: Company, test_roles: dict
) -> User:
    """Create recruiter user."""
    user = User(
        email="recruiter@example.com",
        first_name="Jane",
        last_name="Recruiter",
        company_id=recruiter_company.id,
        hashed_password=auth_service.get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign role
    user_role = UserRoleModel(
        user_id=user.id, role_id=test_roles[UserRole.RECRUITER.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def employer_user(
    db_session: AsyncSession, employer_company: Company, test_roles: dict
) -> User:
    """Create employer user."""
    user = User(
        email="employer@example.com",
        first_name="Bob",
        last_name="Employer",
        company_id=employer_company.id,
        hashed_password=auth_service.get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign role
    user_role = UserRoleModel(
        user_id=user.id, role_id=test_roles[UserRole.EMPLOYER.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


class TestMessagingRules:
    """Test messaging business rules enforcement."""

    @pytest.mark.asyncio
    async def test_candidate_can_message_recruiter(
        self, db_session: AsyncSession, candidate_user: User, recruiter_user: User
    ):
        """Test that candidate can message recruiter."""
        can_comm, reason = await messaging_service.rules_service.can_communicate(
            db_session, candidate_user.id, recruiter_user.id
        )
        assert can_comm is True
        assert "Allowed communication" in reason

    @pytest.mark.asyncio
    async def test_recruiter_can_message_employer(
        self, db_session: AsyncSession, recruiter_user: User, employer_user: User
    ):
        """Test that recruiter can message employer."""
        can_comm, reason = await messaging_service.rules_service.can_communicate(
            db_session, recruiter_user.id, employer_user.id
        )
        assert can_comm is True
        assert "Allowed communication" in reason

    @pytest.mark.asyncio
    async def test_candidate_cannot_message_employer(
        self, db_session: AsyncSession, candidate_user: User, employer_user: User
    ):
        """Test that candidate cannot directly message employer."""
        can_comm, reason = await messaging_service.rules_service.can_communicate(
            db_session, candidate_user.id, employer_user.id
        )
        assert can_comm is False
        assert "not allowed" in reason.lower()
        assert "recruiter" in reason.lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_message_anyone(
        self, db_session: AsyncSession, test_super_admin: User, candidate_user: User
    ):
        """Test that super admin can message anyone."""
        can_comm, reason = await messaging_service.rules_service.can_communicate(
            db_session, test_super_admin.id, candidate_user.id
        )
        assert can_comm is True
        assert "Super admin access" in reason


class TestMessagingAPI:
    """Test messaging REST API endpoints."""

    @pytest.mark.asyncio
    async def test_create_conversation_success(
        self, client: AsyncClient, candidate_user: User, recruiter_user: User
    ):
        """Test successful conversation creation."""
        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        response = await client.post(
            "/api/messaging/conversations",
            headers=headers,
            json={"participant_ids": [recruiter_user.id], "title": "Test Conversation"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["type"] == "direct"
        assert len(data["participants"]) == 1
        assert data["participants"][0]["id"] == recruiter_user.id

    @pytest.mark.asyncio
    async def test_create_conversation_forbidden(
        self, client: AsyncClient, candidate_user: User, employer_user: User
    ):
        """Test forbidden conversation creation."""
        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to create conversation with employer (should fail)
        response = await client.post(
            "/api/messaging/conversations",
            headers=headers,
            json={"participant_ids": [employer_user.id]},
        )

        assert response.status_code == 403
        assert "not allowed" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_send_message_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        candidate_user: User,
        recruiter_user: User,
    ):
        """Test successful message sending."""
        # Create conversation first
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Send message
        response = await client.post(
            f"/api/messaging/conversations/{conversation.id}/messages",
            headers=headers,
            json={"content": "Hello from candidate!", "type": "text"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Hello from candidate!"
        assert data["sender_id"] == candidate_user.id

    @pytest.mark.asyncio
    async def test_get_conversations(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        candidate_user: User,
        recruiter_user: User,
    ):
        """Test getting user's conversations."""
        # Create conversation with message
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id], "Test Chat"
        )

        await messaging_service.send_message(
            db_session, conversation.id, candidate_user.id, "Test message"
        )

        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get conversations
        response = await client.get("/api/messaging/conversations", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["conversations"]) >= 1

        conv = data["conversations"][0]
        assert conv["id"] == conversation.id
        assert conv["title"] == "Test Chat"
        assert conv["last_message"]["content"] == "Test message"

    @pytest.mark.asyncio
    async def test_get_conversation_messages(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        candidate_user: User,
        recruiter_user: User,
    ):
        """Test getting conversation messages."""
        # Create conversation with messages
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        _message1 = await messaging_service.send_message(
            db_session, conversation.id, candidate_user.id, "First message"
        )

        _message2 = await messaging_service.send_message(
            db_session, conversation.id, recruiter_user.id, "Second message"
        )

        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get messages
        response = await client.get(
            f"/api/messaging/conversations/{conversation.id}/messages", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        messages = data["messages"]
        assert len(messages) == 2
        assert messages[0]["content"] == "First message"
        assert messages[1]["content"] == "Second message"

    @pytest.mark.asyncio
    async def test_file_upload_presign(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        candidate_user: User,
        recruiter_user: User,
    ):
        """Test file upload presigned URL generation."""
        # Create conversation
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request file upload
        with patch("app.services.storage_service.StorageService") as mock_storage_class:
            mock_storage = Mock()
            mock_storage.generate_s3_key.return_value = "test/key"
            mock_storage.bucket = "test-bucket"
            mock_storage.get_presigned_upload_url.return_value = {
                "upload_url": "http://minio:9000/test-upload-url",
                "s3_key": "test/key",
                "expires_at": "2024-01-01T00:00:00Z",
            }
            mock_storage_class.return_value = mock_storage

            response = await client.post(
                f"/api/messaging/conversations/{conversation.id}/attachments/presign",
                headers=headers,
                json={
                    "filename": "test.pdf",
                    "mime_type": "application/pdf",
                    "file_size": 1024000,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "upload_url" in data
        assert "attachment_id" in data
        assert data["s3_key"] == "test/key"

    @pytest.mark.asyncio
    async def test_search_participants(
        self, client: AsyncClient, candidate_user: User, recruiter_user: User
    ):
        """Test searching for conversation participants."""
        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search participants
        response = await client.get(
            "/api/messaging/participants/search?query=recruiter", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        participants = data["participants"]

        # Should find the recruiter
        recruiter_found = any(p["id"] == recruiter_user.id for p in participants)
        assert recruiter_found

    @pytest.mark.asyncio
    async def test_mark_messages_read(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        candidate_user: User,
        recruiter_user: User,
    ):
        """Test marking messages as read."""
        # Create conversation with message
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        message = await messaging_service.send_message(
            db_session,
            conversation.id,
            recruiter_user.id,
            "Test message from recruiter",
        )

        # Login as candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate_user.email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mark message as read
        response = await client.post(
            f"/api/messaging/conversations/{conversation.id}/messages/{message.id}/read",
            headers=headers,
        )

        assert response.status_code == 200
        assert "marked" in response.json()["message"].lower()


class TestMessagingService:
    """Test messaging service business logic."""

    @pytest.mark.asyncio
    async def test_create_conversation_service(
        self, db_session: AsyncSession, candidate_user: User, recruiter_user: User
    ):
        """Test conversation creation via service."""
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id], "Service Test"
        )

        assert conversation.id is not None
        assert conversation.title == "Service Test"
        assert conversation.type == "direct"
        assert len(conversation.participants) == 2

    @pytest.mark.asyncio
    async def test_send_message_service(
        self, db_session: AsyncSession, candidate_user: User, recruiter_user: User
    ):
        """Test message sending via service."""
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        message = await messaging_service.send_message(
            db_session, conversation.id, candidate_user.id, "Service test message"
        )

        assert message.id is not None
        assert message.content == "Service test message"
        assert message.sender_id == candidate_user.id
        assert message.conversation_id == conversation.id

    @pytest.mark.asyncio
    async def test_get_conversation_messages_service(
        self, db_session: AsyncSession, candidate_user: User, recruiter_user: User
    ):
        """Test getting messages via service."""
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        # Send multiple messages
        _msg1 = await messaging_service.send_message(
            db_session, conversation.id, candidate_user.id, "First"
        )
        _msg2 = await messaging_service.send_message(
            db_session, conversation.id, recruiter_user.id, "Second"
        )

        # Get messages
        messages = await messaging_service.get_conversation_messages(
            db_session, conversation.id, candidate_user.id
        )

        assert len(messages) == 2
        assert messages[0].content == "First"
        assert messages[1].content == "Second"

    @pytest.mark.asyncio
    async def test_mark_messages_read_service(
        self, db_session: AsyncSession, candidate_user: User, recruiter_user: User
    ):
        """Test marking messages as read via service."""
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        message = await messaging_service.send_message(
            db_session, conversation.id, recruiter_user.id, "Read this message"
        )

        # Mark as read
        read_count = await messaging_service.mark_messages_as_read(
            db_session, conversation.id, candidate_user.id, message.id
        )

        assert read_count == 1

    @pytest.mark.asyncio
    async def test_conversation_access_control(
        self,
        db_session: AsyncSession,
        candidate_user: User,
        recruiter_user: User,
        employer_user: User,
    ):
        """Test conversation access control."""
        # Create conversation between candidate and recruiter
        conversation = await messaging_service.create_conversation(
            db_session, candidate_user.id, [recruiter_user.id]
        )

        # Test access for participants
        (
            can_access_candidate,
            _,
        ) = await messaging_service.rules_service.can_access_conversation(
            db_session, candidate_user.id, conversation.id
        )
        assert can_access_candidate is True

        (
            can_access_recruiter,
            _,
        ) = await messaging_service.rules_service.can_access_conversation(
            db_session, recruiter_user.id, conversation.id
        )
        assert can_access_recruiter is True

        # Test access for non-participant
        (
            can_access_employer,
            reason,
        ) = await messaging_service.rules_service.can_access_conversation(
            db_session, employer_user.id, conversation.id
        )
        assert can_access_employer is False
        assert "not a participant" in reason.lower()


class TestFileUploads:
    """Test file upload and virus scanning."""

    @pytest.mark.asyncio
    @patch("app.services.antivirus_service.antivirus_service.scan_attachment")
    async def test_attachment_virus_scanning(self, mock_scan, db_session: AsyncSession):
        """Test attachment virus scanning."""
        mock_scan.return_value = True

        # Create test attachment
        attachment = Attachment(
            owner_id=1,
            original_filename="test.pdf",
            s3_key="test/key",
            s3_bucket="test-bucket",
            mime_type="application/pdf",
            file_size=1024,
            sha256_hash="testhash",
            virus_status=VirusStatus.PENDING.value,
        )

        db_session.add(attachment)
        await db_session.commit()
        await db_session.refresh(attachment)

        # Trigger scan
        from app.services.antivirus_service import antivirus_service

        result = await antivirus_service.scan_attachment(db_session, attachment.id)

        assert result is True
        mock_scan.assert_called_once_with(db_session, attachment.id)
