"""
Comprehensive Resume Endpoints Testing

Tests all resume-related endpoints with proper authentication, enum validation,
and edge cases to ensure 100% functionality.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import (
    ResumeFormat,
    ResumeLanguage,
    ResumeStatus,
    ResumeVisibility,
)


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user for authentication."""
    from app.models.role import Role, UserRole
    from app.schemas.user import UserCreate

    # Create test user
    UserCreate(email="test@example.com", full_name="Test User", password="testpassword")

    # Create user with hash password
    hashed_password = auth_service.get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=hashed_password,
        is_active=True,
    )

    db.add(user)
    await db.flush()

    # Add candidate role
    role = Role(name="candidate", description="Candidate role")
    db.add(role)
    await db.flush()

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)

    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_token(test_user: User):
    """Generate auth token for test user."""
    access_token = auth_service.create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "roles": ["candidate"],
        }
    )
    return access_token


@pytest.fixture
def auth_headers(auth_token: str):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_resume(db: AsyncSession, test_user: User):
    """Create a test resume."""
    resume = Resume(
        user_id=test_user.id,
        title="Test Resume",
        full_name="Test User",
        email="test@example.com",
        status=ResumeStatus.DRAFT,
        visibility=ResumeVisibility.PRIVATE,
        resume_format=ResumeFormat.INTERNATIONAL,
        resume_language=ResumeLanguage.ENGLISH,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


class TestResumeEndpointsAuthentication:
    """Test authentication for all resume endpoints."""

    async def test_get_resumes_unauthorized(self, client: AsyncClient):
        """Test getting resumes without authentication fails."""
        response = await client.get("/api/resumes/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    async def test_get_resumes_invalid_token(self, client: AsyncClient):
        """Test getting resumes with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/resumes/", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    async def test_create_resume_unauthorized(self, client: AsyncClient):
        """Test creating resume without authentication fails."""
        resume_data = {"title": "Test Resume", "full_name": "Test User"}
        response = await client.post("/api/resumes/", json=resume_data)
        assert response.status_code == 401

    async def test_update_resume_unauthorized(
        self, client: AsyncClient, test_resume: Resume
    ):
        """Test updating resume without authentication fails."""
        response = await client.put(
            f"/api/resumes/{test_resume.id}", json={"title": "Updated"}
        )
        assert response.status_code == 401

    async def test_delete_resume_unauthorized(
        self, client: AsyncClient, test_resume: Resume
    ):
        """Test deleting resume without authentication fails."""
        response = await client.delete(f"/api/resumes/{test_resume.id}")
        assert response.status_code == 401


class TestResumeEndpointsValidAuthentication:
    """Test endpoints with valid authentication."""

    async def test_get_resumes_success(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test getting resumes with valid authentication succeeds."""
        response = await client.get("/api/resumes/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "resumes" in data
        assert len(data["resumes"]) >= 1

        # Verify resume data structure
        resume = data["resumes"][0]
        assert "id" in resume
        assert "title" in resume
        assert "status" in resume
        assert "visibility" in resume

    async def test_create_resume_success(self, client: AsyncClient, auth_headers: dict):
        """Test creating resume with valid data succeeds."""
        resume_data = {
            "title": "Software Engineer Resume",
            "full_name": "John Doe",
            "email": "john@example.com",
            "status": "draft",
            "visibility": "private",
            "resume_format": "international",
            "resume_language": "en",
        }

        response = await client.post(
            "/api/resumes/", json=resume_data, headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == resume_data["title"]
        assert data["full_name"] == resume_data["full_name"]
        assert data["status"] == "draft"
        assert data["visibility"] == "private"

    async def test_get_resume_by_id_success(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test getting specific resume by ID succeeds."""
        response = await client.get(
            f"/api/resumes/{test_resume.id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == test_resume.id
        assert data["title"] == test_resume.title

    async def test_update_resume_success(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test updating resume succeeds."""
        update_data = {"title": "Updated Resume Title", "status": "published"}

        response = await client.put(
            f"/api/resumes/{test_resume.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Resume Title"
        assert data["status"] == "published"

    async def test_delete_resume_success(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test deleting resume succeeds."""
        response = await client.delete(
            f"/api/resumes/{test_resume.id}", headers=auth_headers
        )
        assert response.status_code == 200

        # Verify resume is deleted
        get_response = await client.get(
            f"/api/resumes/{test_resume.id}", headers=auth_headers
        )
        assert get_response.status_code == 404


class TestEnumValidation:
    """Test enum value validation for all resume-related enums."""

    async def test_valid_status_values(self, client: AsyncClient, auth_headers: dict):
        """Test all valid status enum values are accepted."""
        valid_statuses = ["draft", "published", "archived"]

        for status in valid_statuses:
            resume_data = {
                "title": f"Resume with {status} status",
                "full_name": "Test User",
                "status": status,
            }

            response = await client.post(
                "/api/resumes/", json=resume_data, headers=auth_headers
            )
            assert response.status_code == 201
            assert response.json()["status"] == status

    async def test_invalid_status_values(self, client: AsyncClient, auth_headers: dict):
        """Test invalid status enum values are rejected."""
        invalid_statuses = ["DRAFT", "PUBLISHED", "invalid", "Draft", "Published"]

        for status in invalid_statuses:
            resume_data = {
                "title": "Test Resume",
                "full_name": "Test User",
                "status": status,
            }

            response = await client.post(
                "/api/resumes/", json=resume_data, headers=auth_headers
            )
            assert response.status_code == 422  # Validation error

    async def test_valid_visibility_values(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test all valid visibility enum values are accepted."""
        valid_visibilities = ["private", "public", "unlisted"]

        for visibility in valid_visibilities:
            resume_data = {
                "title": f"Resume with {visibility} visibility",
                "full_name": "Test User",
                "visibility": visibility,
            }

            response = await client.post(
                "/api/resumes/", json=resume_data, headers=auth_headers
            )
            assert response.status_code == 201
            assert response.json()["visibility"] == visibility

    async def test_invalid_visibility_values(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test invalid visibility enum values are rejected."""
        invalid_visibilities = ["PRIVATE", "PUBLIC", "invalid", "Private", "hidden"]

        for visibility in invalid_visibilities:
            resume_data = {
                "title": "Test Resume",
                "full_name": "Test User",
                "visibility": visibility,
            }

            response = await client.post(
                "/api/resumes/", json=resume_data, headers=auth_headers
            )
            assert response.status_code == 422  # Validation error

    async def test_valid_format_values(self, client: AsyncClient, auth_headers: dict):
        """Test all valid format enum values are accepted."""
        valid_formats = [
            "rirekisho",
            "shokumu_keirekisho",
            "international",
            "modern",
            "creative",
        ]

        for format_val in valid_formats:
            resume_data = {
                "title": f"Resume with {format_val} format",
                "full_name": "Test User",
                "resume_format": format_val,
            }

            response = await client.post(
                "/api/resumes/", json=resume_data, headers=auth_headers
            )
            assert response.status_code == 201
            assert response.json()["resume_format"] == format_val

    async def test_valid_language_values(self, client: AsyncClient, auth_headers: dict):
        """Test all valid language enum values are accepted."""
        valid_languages = ["ja", "en", "bilingual"]

        for language in valid_languages:
            resume_data = {
                "title": f"Resume in {language}",
                "full_name": "Test User",
                "resume_language": language,
            }

            response = await client.post(
                "/api/resumes/", json=resume_data, headers=auth_headers
            )
            assert response.status_code == 201
            assert response.json()["resume_language"] == language


class TestStatusTransitions:
    """Test valid status transitions."""

    async def test_draft_to_published(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test transitioning from draft to published."""
        # Ensure resume starts as draft
        assert test_resume.status == ResumeStatus.DRAFT

        # Update to published
        response = await client.put(
            f"/api/resumes/{test_resume.id}",
            json={"status": "published"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "published"

    async def test_published_to_archived(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test transitioning from published to archived."""
        # First set to published
        await client.put(
            f"/api/resumes/{test_resume.id}",
            json={"status": "published"},
            headers=auth_headers,
        )

        # Then archive
        response = await client.put(
            f"/api/resumes/{test_resume.id}",
            json={"status": "archived"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "archived"


class TestVisibilityAndPublicAccess:
    """Test visibility settings and public access."""

    async def test_toggle_public_visibility(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test toggling public visibility."""
        response = await client.post(
            f"/api/resumes/{test_resume.id}/toggle-public", headers=auth_headers
        )
        assert response.status_code == 200

        # Should now be public
        data = response.json()
        assert data["is_public"] is True

    async def test_update_public_settings(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test updating public sharing settings."""
        settings_data = {
            "is_public": True,
            "custom_slug": "my-awesome-resume",
            "can_download_pdf": True,
        }

        response = await client.put(
            f"/api/resumes/{test_resume.id}/public-settings",
            json=settings_data,
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["is_public"] is True
        assert data["can_download_pdf"] is True


class TestErrorHandling:
    """Test error handling and edge cases."""

    async def test_get_nonexistent_resume(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent resume returns 404."""
        response = await client.get("/api/resumes/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_nonexistent_resume(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent resume returns 404."""
        response = await client.put(
            "/api/resumes/99999", json={"title": "New Title"}, headers=auth_headers
        )
        assert response.status_code == 404

    async def test_delete_nonexistent_resume(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent resume returns 404."""
        response = await client.delete("/api/resumes/99999", headers=auth_headers)
        assert response.status_code == 404

    async def test_create_resume_missing_required_fields(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating resume with missing required fields fails."""
        incomplete_data = {
            "title": "Test Resume"
            # Missing full_name and other required fields
        }

        response = await client.post(
            "/api/resumes/", json=incomplete_data, headers=auth_headers
        )
        assert response.status_code == 422

    async def test_create_resume_invalid_data_types(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating resume with invalid data types fails."""
        invalid_data = {
            "title": 123,  # Should be string
            "full_name": "Test User",
            "is_primary": "yes",  # Should be boolean
        }

        response = await client.post(
            "/api/resumes/", json=invalid_data, headers=auth_headers
        )
        assert response.status_code == 422


class TestPagination:
    """Test pagination functionality."""

    async def test_resumes_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test resume list pagination."""
        # Test with limit and offset
        response = await client.get(
            "/api/resumes/?limit=5&offset=0", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "resumes" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    async def test_resumes_filtering(self, client: AsyncClient, auth_headers: dict):
        """Test resume list filtering by status."""
        response = await client.get("/api/resumes/?status=draft", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # All returned resumes should have draft status
        for resume in data["resumes"]:
            assert resume["status"] == "draft"


class TestConcurrency:
    """Test concurrent access scenarios."""

    async def test_concurrent_resume_updates(
        self, client: AsyncClient, auth_headers: dict, test_resume: Resume
    ):
        """Test concurrent updates to the same resume."""
        import asyncio

        async def update_resume(title: str):
            return await client.put(
                f"/api/resumes/{test_resume.id}",
                json={"title": title},
                headers=auth_headers,
            )

        # Simulate concurrent updates
        tasks = [
            update_resume("Title 1"),
            update_resume("Title 2"),
            update_resume("Title 3"),
        ]

        responses = await asyncio.gather(*tasks)

        # All should succeed (last one wins)
        for response in responses:
            assert response.status_code == 200
