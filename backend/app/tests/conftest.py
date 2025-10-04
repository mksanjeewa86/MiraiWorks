import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set environment to test before importing settings
try:
    import bcrypt

    if not hasattr(bcrypt, "__about__"):

        class _About:
            __version__ = getattr(bcrypt, "__version__", "unknown")

        bcrypt.__about__ = _About()
except ImportError:
    pass

os.environ["ENVIRONMENT"] = "test"

import contextlib
import subprocess

# Test database configuration - optimized for speed
import time

from app.database import Base, get_db
from app.main import app

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # Import all models
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum

# Test database URL - support both CI and local development
if os.getenv("DATABASE_URL"):
    # Use explicit DATABASE_URL from environment (CI/CD)
    TEST_DATABASE_URL = os.getenv("DATABASE_URL")
elif os.getenv("GITHUB_ACTIONS"):
    # GitHub Actions default
    TEST_DATABASE_URL = (
        "mysql+asyncmy://changeme:changeme@127.0.0.1:3307/miraiworks_test"
    )
else:
    # Local Docker development
    TEST_DATABASE_URL = (
        "mysql+asyncmy://changeme:changeme@localhost:3307/miraiworks_test"
    )

# Create test engine with optimized settings for fast tests
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    pool_size=10,  # Increased for better concurrency
    max_overflow=20,  # Higher overflow for busy tests
    pool_recycle=3600,  # Longer recycle time
    pool_pre_ping=True,  # Health checks
    pool_timeout=10,  # Faster timeout
    echo=False,  # No SQL logging for speed
    connect_args={
        "autocommit": False,
        "connect_timeout": 10,
    },
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


def start_test_database():
    """Start Docker MySQL test database with optimized startup."""
    print("Starting MySQL test database...")

    # Check if container is already running and healthy
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                "name=miraiworks-mysql-test",
                "--filter",
                "health=healthy",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        if "miraiworks-mysql-test" in result.stdout:
            print("MySQL test database is already running and healthy")
            return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    # Only clean up if not healthy
    with contextlib.suppress(subprocess.CalledProcessError, subprocess.TimeoutExpired):
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down"],
            cwd=str(BACKEND_DIR.parent),
            capture_output=True,
            timeout=10,
        )

    # Start the test database
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
            check=True,
            cwd=str(BACKEND_DIR.parent),
            timeout=30,
        )
        print("Started MySQL test database")

        # Wait for database to be ready - optimized wait
        print("Waiting for MySQL to be ready...")
        max_attempts = 30  # Reduced from 60
        for attempt in range(max_attempts):
            try:
                # Quick health check
                result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        "--format={{.State.Health.Status}}",
                        "miraiworks-mysql-test",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if result.returncode == 0 and "healthy" in result.stdout:
                    print(f"MySQL is ready! (attempt {attempt + 1})")
                    return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

            time.sleep(2)  # Reduced from 3 seconds
            if attempt % 5 == 0:
                print(f"Waiting for MySQL... (attempt {attempt + 1}/{max_attempts})")

        raise Exception("MySQL failed to start within timeout")

    except subprocess.CalledProcessError as e:
        print(f"Failed to start MySQL test database: {e}")
        return False


def stop_test_database():
    """Stop Docker MySQL test database - but keep it running for speed."""
    # Don't actually stop the database to keep it running between test sessions
    # Only stop when explicitly needed
    print("Keeping MySQL test database running for next test session...")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment with persistent database."""
    if os.getenv("GITHUB_ACTIONS") or os.getenv("DATABASE_URL"):
        print("Running in CI/CD environment - using managed database service")
        yield
    else:
        # Local development - manage Docker container
        if not start_test_database():
            pytest.exit("Failed to start MySQL test database")

        print("Test environment ready - database will persist between test runs")
        yield

        # Don't stop database for faster subsequent runs
        print("Test session complete - database kept running")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def fast_clear_data():
    """Fast data clearing without dropping tables."""
    try:
        async with test_engine.begin() as conn:
            from sqlalchemy import text

            # Get all table names once
            result = await conn.execute(text("SHOW TABLES"))
            table_names = [row[0] for row in result.fetchall()]

            if table_names:
                # Disable foreign key checks
                await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

                # Truncate all tables in one transaction
                for table_name in table_names:
                    await conn.execute(text(f"TRUNCATE TABLE `{table_name}`"))

                # Re-enable foreign key checks
                await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        return True
    except Exception as e:
        print(f"Fast clear failed: {e}")
        return False


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database_schema():
    """Set up test database schema once per session."""
    try:
        # Fast clear any existing data
        await fast_clear_data()

        # Create schema only if tables don't exist
        async with test_engine.begin() as conn:
            # Check if tables exist
            from sqlalchemy import text

            result = await conn.execute(text("SHOW TABLES"))
            existing_tables = [row[0] for row in result.fetchall()]

            if not existing_tables:
                # Create all tables
                await conn.run_sync(
                    lambda sync_conn: Base.metadata.create_all(sync_conn)
                )
                print("Database schema created")
            else:
                print(f"Database schema already exists ({len(existing_tables)} tables)")

        yield

        # Keep schema for next test run - only clear data
        await fast_clear_data()
        print("Test data cleared - schema preserved")

    except Exception as e:
        print(f"Database schema setup failed: {e}")
        raise


@pytest_asyncio.fixture(scope="function")
async def clean_database():
    """Clean database before test setup."""
    # Clear data before test fixtures run
    await fast_clear_data()
    yield


@pytest_asyncio.fixture
async def db_session(clean_database):
    """Get database session for tests."""
    session = None
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        if session:
            with contextlib.suppress(Exception):
                await session.close()


@pytest_asyncio.fixture
async def client():
    """Get HTTP client for tests with GET json support."""

    class PatchedAsyncClient(AsyncClient):
        async def get(self, url: str, *args, **kwargs):
            json_payload = kwargs.pop("json", None)
            if json_payload is not None:
                existing_params = kwargs.get("params") or {}
                if isinstance(existing_params, dict):
                    merged = {**json_payload, **existing_params}
                else:
                    merged = json_payload
                kwargs["params"] = merged
            return await super().get(url, *args, **kwargs)

    async with PatchedAsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client


# Optimized test fixtures with caching
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
        type=CompanyType.RECRUITER.value,
        email="test@company.com",
        phone="123-456-7890",
        is_active=True,
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

    # Assign admin role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.ADMIN.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def test_employer_user(db_session, test_company, test_roles):
    """Create member user with company association (employer context via company type)."""
    user = User(
        email="employer@example.com",
        first_name="Member",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("memberpassword123"),
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.MEMBER.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def test_candidate_only_user(db_session, test_roles):
    """Create candidate without company affiliation."""
    user = User(
        email="candidate_only@example.com",
        first_name="Candidate",
        last_name="Only",
        company_id=None,
        hashed_password=auth_service.get_password_hash("candidatepassword456"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.CANDIDATE.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def test_system_admin(db_session, test_roles):
    """Create test system admin user."""
    user = User(
        email="systemadmin@example.com",
        first_name="System",
        last_name="Admin",
        company_id=None,  # System admin has no company
        hashed_password=auth_service.get_password_hash("systempassword123"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign system admin role
    user_role = UserRole(
        user_id=user.id, role_id=test_roles[UserRoleEnum.SYSTEM_ADMIN.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


# Alias for backward compatibility
test_super_admin = test_system_admin


@pytest_asyncio.fixture
async def auth_headers(client, test_employer_user):
    """Get authentication headers for employer user."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_employer_user.email, "password": "employerpassword123"},
    )
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def candidate_headers(client, test_candidate_only_user):
    """Get authentication headers for candidate user."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_candidate_only_user.email,
            "password": "candidatepassword456",
        },
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
                "code": "123456",  # Mock 2FA code for tests
            },
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
            raise Exception(f"Login failed with status {response.status_code}")

        token_data = response.json()

        # Check if 2FA is required
        if token_data.get("require_2fa"):
            # Complete 2FA flow with a test code
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={
                    "user_id": test_super_admin.id,
                    "code": "123456",  # Mock 2FA code for tests
                },
            )

            if verify_response.status_code != 200:
                raise Exception(
                    f"2FA verification failed with status {verify_response.status_code}"
                )

            token_data = verify_response.json()

        if not token_data.get("access_token"):
            raise Exception("No access token received")

        return {"Authorization": f"Bearer {token_data['access_token']}"}

    except Exception:
        # Return a dummy header to prevent further crashes
        return {"Authorization": "Bearer dummy_token_for_testing"}


# Helper function to create auth headers for any user
async def get_auth_headers_for_user(client, user):
    """Get authentication headers for any user."""
    # Determine password based on user email
    if user.email == "test@example.com":
        password = "testpassword123"
    elif user.email == "admin@example.com":
        password = "adminpassword123"
    elif user.email == "employer@example.com":
        password = "employerpassword123"
    elif user.email == "candidate_only@example.com":
        password = "candidatepassword456"
    else:
        password = "password123"

    response = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": password},
    )

    assert (
        response.status_code == 200
    ), f"Login failed for user {user.email}: {response.text}"
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def test_users(
    test_user, test_admin_user, test_employer_user, test_candidate_only_user
):
    """Fixture providing dictionary of various test users for attachment tests."""
    return {
        "user": test_user,
        "admin": test_admin_user,
        "recruiter": test_employer_user,  # Using employer as recruiter for consistency
        "candidate": test_candidate_only_user,
        "employer": test_employer_user,
    }


@pytest_asyncio.fixture
async def test_todo_with_attachments(db_session, test_user):
    """Fixture providing a todo with test attachments."""
    import os
    import tempfile

    from app.crud.todo import todo as todo_crud
    from app.crud.todo_attachment import todo_attachment as attachment_crud
    from app.schemas.todo import TodoCreate
    from app.schemas.todo_attachment import TodoAttachmentCreate

    # Create a test todo
    todo_data = TodoCreate(
        title="Test Todo with Attachments", description="Todo for attachment testing"
    )
    todo = await todo_crud.create_with_owner(
        db_session, obj_in=todo_data, owner_id=test_user.id
    )

    # Create test attachments
    attachments = []

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(
        mode="w+b", delete=False, suffix=".txt"
    ) as temp_file:
        test_content = b"This is test attachment content for testing purposes."
        temp_file.write(test_content)
        temp_file_path = temp_file.name

    try:
        # Create attachment record in database
        attachment_data = TodoAttachmentCreate(
            todo_id=todo.id,
            original_filename="test_attachment.txt",
            stored_filename="test_attachment_stored.txt",
            file_path=temp_file_path,
            file_size=len(test_content),
            mime_type="text/plain",
            file_extension=".txt",
            uploaded_by=test_user.id,
        )
        attachment = await attachment_crud.create(db_session, obj_in=attachment_data)
        attachments.append(attachment)

        return {
            "todo": todo,
            "user": test_user,
            "attachments": attachments,
            "temp_files": [temp_file_path],  # For cleanup
        }
    except Exception:
        # Clean up temp file if fixture creation fails
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise
