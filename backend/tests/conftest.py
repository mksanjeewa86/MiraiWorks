"""Test configuration and fixtures for MiraiWorks messaging system."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.company import Company
from app.models.direct_message import DirectMessage
from app.models.notification import Notification
from app.models.role import Role, UserRole
from app.models.user import User
from app.models.user_settings import UserSettings
from app.services.email_service import email_service
from app.services.notification_service import notification_service
from app.utils.constants import CompanyType

# Test database URL - use MySQL
TEST_DATABASE_URL = "mysql+asyncmy://hrms:hrms@localhost:3306/test_miraiworks"

# Create test async engine
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=3600
)

# Test session factory
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create test database engine."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client."""

    # Override database dependency
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_company(db_session: AsyncSession) -> Company:
    """Create test company."""
    company = Company(
        name="Test Company",
        domain="test.com",
        type=CompanyType.EMPLOYER,
        email="test@testcompany.com",
        website="https://testcompany.com",
        description="A test company for testing purposes",
        is_active="1",
    )
    db_session.add(company)
    await db_session.flush()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def test_roles(db_session: AsyncSession) -> dict[str, Role]:
    """Create test roles."""
    roles = {}
    role_names = ["candidate", "recruiter", "employer", "company_admin", "super_admin"]

    for role_name in role_names:
        role = Role(name=role_name, description=f"Test {role_name} role")
        db_session.add(role)
        roles[role_name] = role

    await db_session.flush()
    return roles


@pytest_asyncio.fixture
async def test_user(
    db_session: AsyncSession, test_company: Company, test_roles: dict[str, Role]
) -> User:
    """Create test user."""
    user = User(
        email="test@test.com",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        company_id=test_company.id,
        hashed_password="test_hash",
        is_active=True,
        require_2fa=False,
    )
    db_session.add(user)
    await db_session.flush()

    # Add user role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles["candidate"].id, scope="default"
    )
    db_session.add(user_role)

    # Add user settings
    settings = UserSettings(
        user_id=user.id, message_notifications=True, email_notifications=True
    )
    db_session.add(settings)

    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user2(
    db_session: AsyncSession, test_company: Company, test_roles: dict[str, Role]
) -> User:
    """Create second test user."""
    user = User(
        email="test2@test.com",
        first_name="Test2",
        last_name="User2",
        phone="1234567891",
        company_id=test_company.id,
        hashed_password="test_hash2",
        is_active=True,
        require_2fa=False,
    )
    db_session.add(user)
    await db_session.flush()

    # Add user role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles["recruiter"].id, scope="default"
    )
    db_session.add(user_role)

    # Add user settings
    settings = UserSettings(
        user_id=user.id, message_notifications=True, email_notifications=True
    )
    db_session.add(settings)

    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin_user(
    db_session: AsyncSession, test_company: Company, test_roles: dict[str, Role]
) -> User:
    """Create test admin user."""
    user = User(
        email="admin@test.com",
        first_name="Admin",
        last_name="User",
        phone="1234567892",
        company_id=test_company.id,
        hashed_password="admin_hash",
        is_active=True,
        require_2fa=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Add admin role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles["company_admin"].id, scope="default"
    )
    db_session.add(user_role)

    # Add user settings
    settings = UserSettings(
        user_id=user.id,
        message_notifications=False,  # Admin has notifications disabled
        email_notifications=False,
    )
    db_session.add(settings)

    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_message(
    db_session: AsyncSession, test_user: User, test_user2: User
) -> DirectMessage:
    """Create test direct message."""
    message = DirectMessage(
        sender_id=test_user.id,
        recipient_id=test_user2.id,
        content="Test message content",
        type="text",
        is_read=False,
    )
    db_session.add(message)
    await db_session.flush()
    await db_session.refresh(message)
    return message


@pytest_asyncio.fixture
async def test_messages(
    db_session: AsyncSession, test_user: User, test_user2: User
) -> list[DirectMessage]:
    """Create multiple test messages for conversation."""
    messages = []

    # Create a conversation with multiple messages
    for i in range(5):
        sender = test_user if i % 2 == 0 else test_user2
        recipient = test_user2 if i % 2 == 0 else test_user

        message = DirectMessage(
            sender_id=sender.id,
            recipient_id=recipient.id,
            content=f"Test message {i+1}",
            type="text",
            is_read=i < 3,  # First 3 messages are read
        )
        db_session.add(message)
        messages.append(message)

    await db_session.flush()
    return messages


@pytest_asyncio.fixture
async def test_notification(db_session: AsyncSession, test_user: User) -> Notification:
    """Create test notification."""
    notification = Notification(
        user_id=test_user.id,
        type="new_message",
        title="New Message",
        message="You have a new message",
        payload={"sender_id": 2, "message_id": 1},
        is_read=False,
    )
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    with pytest.mock.patch.object(
        email_service, "send_email", new_callable=AsyncMock
    ) as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing."""
    with pytest.mock.patch.object(
        notification_service, "create_notification", new_callable=AsyncMock
    ) as mock:
        yield mock


@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing real-time features."""
    mock = MagicMock()
    mock.accept = AsyncMock()
    mock.send_text = AsyncMock()
    mock.receive_text = AsyncMock()
    mock.close = AsyncMock()
    return mock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_test_data(engine):
    """Cleanup test data after each test."""
    yield

    # Clean up all tables after each test
    async with TestSessionLocal() as session:
        # Delete in reverse order to avoid foreign key constraints
        table_names = [
            "direct_messages",
            "user_settings",
            "user_roles",
            "roles",
            "users",
            "companies",
        ]

        for table_name in table_names:
            await session.execute(text(f"DELETE FROM {table_name}"))

        await session.commit()


# Test utilities
class TestUtils:
    """Utility functions for tests."""

    @staticmethod
    async def create_test_conversation(
        db_session: AsyncSession, user1: User, user2: User, message_count: int = 5
    ) -> list[DirectMessage]:
        """Create test conversation between two users."""
        messages = []

        for i in range(message_count):
            sender = user1 if i % 2 == 0 else user2
            recipient = user2 if i % 2 == 0 else user1

            message = DirectMessage(
                sender_id=sender.id,
                recipient_id=recipient.id,
                content=f"Conversation message {i+1}",
                type="text",
                is_read=False,
            )
            db_session.add(message)
            messages.append(message)

        await db_session.flush()
        return messages

    @staticmethod
    def get_auth_headers(user_id: int) -> dict[str, str]:
        """Get authentication headers for test requests."""
        # This would normally generate a JWT token
        # For tests, we can use a simple mock token
        return {
            "Authorization": f"Bearer mock-token-user-{user_id}",
            "Content-Type": "application/json",
        }


@pytest.fixture
def test_utils():
    """Test utilities fixture."""
    return TestUtils
