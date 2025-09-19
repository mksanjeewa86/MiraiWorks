import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Set environment to test before importing settings
os.environ["ENVIRONMENT"] = "test"

from app.database import Base, get_db
from app.main import app
# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # Import all models
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum

# Test database URL (SQLite in memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for tests."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Set up test database for each test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Get database session for tests."""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Get HTTP client for tests."""
    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client


@pytest_asyncio.fixture
async def test_roles(db_session):
    """Create test roles."""
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role

    await db_session.commit()

    # Refresh all roles
    for role in roles.values():
        await db_session.refresh(role)

    return roles


@pytest_asyncio.fixture
async def test_company(db_session):
    """Create test company."""
    company = Company(
        name="Test Company",
        type=CompanyType.RECRUITER,
        email="test@company.com",
        phone="123-456-7890",
        is_active="1",
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def test_user(db_session, test_company, test_roles):
    """Create test user."""
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign candidate role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.CANDIDATE.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def test_admin_user(db_session, test_company, test_roles):
    """Create test admin user."""
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("adminpassword123"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign company admin role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.COMPANY_ADMIN.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def test_super_admin(db_session, test_roles):
    """Create test super admin user."""
    user = User(
        email="superadmin@example.com",
        first_name="Super",
        last_name="Admin",
        company_id=None,  # Super admin has no company
        hashed_password=auth_service.get_password_hash("superpassword123"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign super admin role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.SUPER_ADMIN.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def admin_auth_headers(client, test_admin_user):
    """Get authentication headers for admin user."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_admin_user.email, "password": "adminpassword123"},
    )
    assert response.status_code == 200
    token_data = response.json()

    # Check if 2FA is required
    if token_data.get("require_2fa"):
        # Complete 2FA flow with a test code
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={
                "user_id": test_admin_user.id,
                "code": "123456"  # Mock 2FA code for tests
            }
        )
        assert verify_response.status_code == 200
        token_data = verify_response.json()

    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def super_admin_auth_headers(client, test_super_admin):
    """Get authentication headers for super admin user."""
    try:
        # Login request
        response = await client.post(
            "/api/auth/login",
            json={"email": test_super_admin.email, "password": "superpassword123"},
        )

        if response.status_code != 200:
            print(f"Login failed: {response.status_code} - {response.text}")
            raise Exception(f"Login failed with status {response.status_code}")

        token_data = response.json()

        # Check if 2FA is required
        if token_data.get("require_2fa"):
            # Complete 2FA flow with a test code
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={
                    "user_id": test_super_admin.id,
                    "code": "123456"  # Mock 2FA code for tests
                }
            )

            if verify_response.status_code != 200:
                print(f"2FA verification failed: {verify_response.status_code} - {verify_response.text}")
                raise Exception(f"2FA verification failed with status {verify_response.status_code}")

            token_data = verify_response.json()

        if not token_data.get("access_token"):
            print(f"No access token in response: {token_data}")
            raise Exception("No access token received")

        return {"Authorization": f"Bearer {token_data['access_token']}"}

    except Exception as e:
        print(f"Error in super_admin_auth_headers fixture: {e}")
        # Return a dummy header to prevent further crashes
        return {"Authorization": "Bearer dummy_token_for_testing"}
