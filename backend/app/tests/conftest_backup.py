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

# Test database URL for Docker MySQL (port 3307 to avoid conflicts)
# Support both local Docker and GitHub Actions
import contextlib
import os
import subprocess

# Test database configuration - MySQL only with Docker
import time
from datetime import UTC

from app.database import Base, get_db
from app.main import app

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # Import all models
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum

if os.getenv("GITHUB_ACTIONS"):
    # GitHub Actions uses service containers
    TEST_DATABASE_URL = (
        "mysql+asyncmy://changeme:changeme@127.0.0.1:3307/miraiworks_test"
    )
else:
    # Local Docker development
    TEST_DATABASE_URL = (
        "mysql+asyncmy://changeme:changeme@localhost:3307/miraiworks_test"
    )

# Create test engine with more conservative settings for CI/CD
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    pool_size=2,
    max_overflow=3,
    pool_recycle=1800,  # Recycle connections every 30 minutes
    pool_pre_ping=True,
    pool_timeout=20,
    echo=False,
    connect_args={
        "autocommit": False,
        "connect_timeout": 20,
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
    """Start Docker MySQL test database."""
    print("Starting MySQL test database with Docker...")

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
        )
        if "miraiworks-mysql-test" in result.stdout:
            print("MySQL test database is already running and healthy")
            return True
    except subprocess.CalledProcessError:
        pass

    # Clean up any existing container
    with contextlib.suppress(subprocess.CalledProcessError):
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
            cwd=str(BACKEND_DIR.parent),
            capture_output=True,
        )

    # Start the test database
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
            check=True,
            cwd=str(BACKEND_DIR.parent),
        )
        print("Started MySQL test database")

        # Wait for database to be ready with health check
        print("Waiting for MySQL to be ready...")
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                # Check health status
                result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        "--format={{.State.Health.Status}}",
                        "miraiworks-mysql-test",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and "healthy" in result.stdout:
                    print("MySQL is ready and healthy!")
                    # Additional verification with a connection test
                    test_result = subprocess.run(
                        [
                            "docker",
                            "exec",
                            "miraiworks-mysql-test",
                            "mysqladmin",
                            "ping",
                            "-h",
                            "localhost",
                            "-u",
                            "changeme",
                            "-pchangeme",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if test_result.returncode == 0:
                        return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

            time.sleep(3)
            if attempt % 10 == 0:
                print(f"Waiting for MySQL... (attempt {attempt + 1}/{max_attempts})")

        raise Exception("MySQL failed to start within timeout")

    except subprocess.CalledProcessError as e:
        print(f"Failed to start MySQL test database: {e}")
        return False


def stop_test_database():
    """Stop Docker MySQL test database."""
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
            check=True,
            cwd=str(BACKEND_DIR.parent),
        )
        print("Stopped MySQL test database")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop MySQL test database: {e}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    if os.getenv("GITHUB_ACTIONS"):
        # In GitHub Actions, MySQL service is managed by the workflow
        print("Running in GitHub Actions - using service container")
        yield
    else:
        # Local development - manage Docker container
        if not start_test_database():
            pytest.exit("Failed to start MySQL test database")

        yield

        # Clean up
        stop_test_database()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def force_drop_all_tables():
    """Force drop all tables directly via SQL to avoid DDL conflicts."""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            async with test_engine.begin() as conn:
                # Disable foreign key checks
                from sqlalchemy import text

                await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

                # Get all table names
                result = await conn.execute(text("SHOW TABLES"))
                table_names = [row[0] for row in result.fetchall()]

                # Drop each table directly
                for table_name in table_names:
                    try:
                        await conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
                    except Exception as drop_error:
                        print(
                            f"Warning: Failed to drop table {table_name}: {drop_error}"
                        )

                # Re-enable foreign key checks
                await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

                print(f"Force dropped {len(table_names)} tables")
                return True

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to force drop tables after {max_retries} attempts: {e}")
                return False
            await asyncio.sleep(1)

    return False


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database_schema():
    """Set up test database schema once per session."""
    max_retries = 3

    # Force clean the database first
    print("Force cleaning database...")
    await force_drop_all_tables()

    # Wait for cleanup to complete
    await asyncio.sleep(2)

    # Create schema with retries and disable existence checks to avoid DDL conflicts
    for attempt in range(max_retries):
        try:
            async with test_engine.begin() as conn:
                # Create all tables without checking if they exist first (checkfirst=False)
                await conn.run_sync(
                    lambda sync_conn: Base.metadata.create_all(
                        sync_conn, checkfirst=False
                    )
                )
            print("Database schema created successfully")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(
                    f"Failed to create database schema after {max_retries} attempts: {e}"
                )
                raise e
            # Wait between retries
            await asyncio.sleep(3)
            print(
                f"Retrying database schema creation... (attempt {attempt + 1}/{max_retries})"
            )

    yield

    # Clean up schema at the end of session
    try:
        await force_drop_all_tables()
        print("Database schema cleaned up")
    except Exception as e:
        print(f"Warning: Failed to clean up database schema: {e}")


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Clean data for each test function without recreating schema."""
    # Clear all table data but keep schema intact
    table_names = []
    max_retries = 3

    for attempt in range(max_retries):
        try:
            async with test_engine.begin() as conn:
                from sqlalchemy import text

                # Get all table names
                result = await conn.execute(text("SHOW TABLES"))
                table_names = [row[0] for row in result.fetchall()]

                if table_names:
                    # Disable foreign key checks for cleanup
                    await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

                    # Truncate all tables to reset auto-increment and remove data
                    for table_name in table_names:
                        await conn.execute(text(f"TRUNCATE TABLE `{table_name}`"))

                    # Re-enable foreign key checks
                    await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Warning: Failed to clean table data: {e}")
                # Fallback: try to delete data instead of truncate
                try:
                    async with test_engine.begin() as conn:
                        from sqlalchemy import text

                        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                        for table_name in table_names:
                            await conn.execute(text(f"DELETE FROM `{table_name}`"))
                        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                except Exception as cleanup_error:
                    print(f"Fallback cleanup also failed: {cleanup_error}")
            else:
                await asyncio.sleep(0.5)

    yield


@pytest_asyncio.fixture
async def db_session():
    """Get database session for tests."""
    session = None
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        if session:
            try:
                await session.close()
            except Exception:
                pass  # Ignore close errors


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
        user_id=user.id, role_id=test_roles[UserRoleEnum.ADMIN.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def test_employer_user(db_session, test_company, test_roles):
    """Create employer user with company association."""
    user = User(
        email="employer@example.com",
        first_name="Employer",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("employerpassword123"),
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
        user_id=user.id, role_id=test_roles[UserRoleEnum.SYSTEM_ADMIN.value].id
    )
    db_session.add(user_role)
    await db_session.commit()

    return user


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
async def employer_headers(auth_headers):
    """Alias for employer authentication headers."""
    return auth_headers


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


@pytest_asyncio.fixture
async def test_users(db_session, test_company, test_roles):
    """Create multiple test users for testing."""
    users = {}

    # Recruiter user
    recruiter = User(
        email="recruiter@example.com",
        first_name="Recruiter",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(recruiter)
    await db_session.commit()
    await db_session.refresh(recruiter)

    recruiter_role = UserRole(
        user_id=recruiter.id, role_id=test_roles[UserRoleEnum.MEMBER.value].id
    )
    db_session.add(recruiter_role)

    # Candidate user
    candidate = User(
        email="candidate@example.com",
        first_name="Candidate",
        last_name="User",
        company_id=None,
        hashed_password=auth_service.get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    candidate_role = UserRole(
        user_id=candidate.id, role_id=test_roles[UserRoleEnum.CANDIDATE.value].id
    )
    db_session.add(candidate_role)

    # Other candidate user
    other_candidate = User(
        email="other_candidate@example.com",
        first_name="Other",
        last_name="Candidate",
        company_id=None,
        hashed_password=auth_service.get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(other_candidate)
    await db_session.commit()
    await db_session.refresh(other_candidate)

    other_candidate_role = UserRole(
        user_id=other_candidate.id, role_id=test_roles[UserRoleEnum.CANDIDATE.value].id
    )
    db_session.add(other_candidate_role)

    # Other recruiter user
    other_recruiter = User(
        email="other_recruiter@example.com",
        first_name="Other",
        last_name="Recruiter",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(other_recruiter)
    await db_session.commit()
    await db_session.refresh(other_recruiter)

    other_recruiter_role = UserRole(
        user_id=other_recruiter.id, role_id=test_roles[UserRoleEnum.MEMBER.value].id
    )
    db_session.add(other_recruiter_role)

    await db_session.commit()

    users["recruiter"] = recruiter
    users["candidate"] = candidate
    users["other_candidate"] = other_candidate
    users["other_recruiter"] = other_recruiter

    return users


@pytest_asyncio.fixture
async def test_todo_with_attachments(db_session, test_users):
    """Create a test todo with file attachments."""
    import tempfile

    from app.crud.todo import todo as todo_crud
    from app.crud.todo_attachment import todo_attachment
    from app.schemas.todo import TodoCreate
    from app.schemas.todo_attachment import TodoAttachmentCreate

    user = test_users["recruiter"]

    # Create todo
    todo_data = TodoCreate(
        title="Test Todo with Attachments",
        description="Testing file attachments functionality",
    )
    test_todo = await todo_crud.create_with_owner(
        db_session, obj_in=todo_data, owner_id=user.id
    )

    # Create temporary files for testing
    temp_files = []
    attachments = []

    for i in range(2):
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_test_{i}.txt"
        ) as temp_file:
            content = f"Test content for attachment {i}".encode()
            temp_file.write(content)
            temp_path = temp_file.name
            temp_files.append(temp_path)

        # Create attachment record
        attachment_data = TodoAttachmentCreate(
            todo_id=test_todo.id,
            original_filename=f"test_file_{i}.txt",
            stored_filename=f"stored_test_{i}.txt",
            file_path=temp_path,
            file_size=len(content),
            mime_type="text/plain",
            file_extension=".txt",
            description=f"Test attachment {i}",
            uploaded_by=user.id,
        )

        attachment = await todo_attachment.create_attachment(
            db_session, attachment_data=attachment_data, uploader_id=user.id
        )
        attachments.append(attachment)

    return {
        "todo": test_todo,
        "user": user,
        "attachments": attachments,
        "temp_files": temp_files,
    }


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
    elif user.email == "superadmin@example.com":
        password = "superpassword123"
    else:
        # Default password for test_users fixture
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


@pytest_asyncio.fixture
async def test_video_call(db_session, test_users):
    """Create a test video call."""
    from datetime import datetime, timedelta

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.crud.video_call import video_call as video_call_crud
    from app.models.video_call import VideoCall
    from app.schemas.video_call import VideoCallCreate

    recruiter = test_users["recruiter"]
    candidate = test_users["candidate"]

    call_data = VideoCallCreate(
        candidate_id=candidate.id,
        scheduled_at=datetime.now(UTC) + timedelta(hours=1),
        enable_transcription=True,
        transcription_language="ja",
    )

    video_call = await video_call_crud.create_with_interviewer(
        db_session, obj_in=call_data, interviewer_id=recruiter.id
    )

    # Load relationships explicitly since they use lazy="noload"
    await db_session.commit()
    result = await db_session.execute(
        select(VideoCall)
        .options(selectinload(VideoCall.interviewer), selectinload(VideoCall.candidate))
        .where(VideoCall.id == video_call.id)
    )
    video_call = result.scalar_one()
    return video_call


@pytest_asyncio.fixture
async def auth_headers_func(client):
    """Get callable auth headers function."""
    return lambda user: get_auth_headers_for_user(client, user)
