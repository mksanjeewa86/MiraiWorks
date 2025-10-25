"""
Comprehensive Resume Functionality Tests

This test suite provides complete coverage of resume functionality
including CRUD operations, sharing, templates, and integration scenarios.
Tests use real database data and API endpoints.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.services.resume_service import ResumeService
from app.utils.constants import (
    ResumeFormat,
    ResumeLanguage,
    ResumeStatus,
    ResumeVisibility,
)


class TestResumeComprehensive:
    """Comprehensive tests for resume functionality."""

    @pytest.fixture
    def resume_service(self):
        """Resume service instance."""
        return ResumeService()

    @pytest.fixture
    async def test_user(self, db: AsyncSession):
        """Create test user."""
        user = User(
            email="testuser@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="$2b$12$test_hash",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @pytest.fixture
    async def sample_resume_data(self):
        """Sample resume data for testing."""
        return {
            "title": "Software Engineer Resume",
            "description": "My professional resume",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "website": "https://johndoe.dev",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "github_url": "https://github.com/johndoe",
            "professional_summary": "Experienced software engineer with 5+ years in web development.",
            "objective": "Seeking a senior software engineer position to leverage my expertise in full-stack development.",
            "template_id": "modern",
            "theme_color": "#2563eb",
            "font_family": "Inter",
        }

    # === SUCCESS SCENARIOS ===

    async def test_create_resume_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test successful resume creation."""
        from app.schemas.resume import ResumeCreate

        resume_data = ResumeCreate(**sample_resume_data)

        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        assert resume is not None
        assert resume.title == sample_resume_data["title"]
        assert resume.user_id == test_user.id
        assert resume.status == ResumeStatus.DRAFT
        assert resume.visibility == ResumeVisibility.PRIVATE
        assert resume.share_token is not None
        assert len(resume.share_token) > 20  # Should have a secure token

    async def test_get_resume_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test successful resume retrieval."""
        from app.schemas.resume import ResumeCreate

        # Create resume first
        resume_data = ResumeCreate(**sample_resume_data)
        created_resume = await resume_service.create_resume(
            db, resume_data, test_user.id
        )

        # Retrieve resume
        retrieved_resume = await resume_service.get_resume(
            db, created_resume.id, test_user.id
        )

        assert retrieved_resume is not None
        assert retrieved_resume.id == created_resume.id
        assert retrieved_resume.title == sample_resume_data["title"]

    async def test_update_resume_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test successful resume update."""
        from app.schemas.resume import ResumeCreate, ResumeUpdate

        # Create resume first
        resume_data = ResumeCreate(**sample_resume_data)
        created_resume = await resume_service.create_resume(
            db, resume_data, test_user.id
        )

        # Update resume
        update_data = ResumeUpdate(
            title="Updated Software Engineer Resume",
            professional_summary="Updated professional summary with more experience.",
        )

        updated_resume = await resume_service.update_resume(
            db, created_resume.id, test_user.id, update_data
        )

        assert updated_resume is not None
        assert updated_resume.title == "Updated Software Engineer Resume"
        assert (
            updated_resume.professional_summary
            == "Updated professional summary with more experience."
        )

    async def test_delete_resume_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test successful resume deletion."""
        from app.schemas.resume import ResumeCreate

        # Create resume first
        resume_data = ResumeCreate(**sample_resume_data)
        created_resume = await resume_service.create_resume(
            db, resume_data, test_user.id
        )

        # Delete resume
        success = await resume_service.delete_resume(
            db, created_resume.id, test_user.id
        )

        assert success is True

        # Verify resume is deleted
        deleted_resume = await resume_service.get_resume(
            db, created_resume.id, test_user.id
        )
        assert deleted_resume is None

    async def test_add_work_experience_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test successful work experience addition."""
        from app.schemas.resume import ResumeCreate, WorkExperienceCreate

        # Create resume first
        resume_data = ResumeCreate(**sample_resume_data)
        created_resume = await resume_service.create_resume(
            db, resume_data, test_user.id
        )

        # Add work experience
        exp_data = WorkExperienceCreate(
            company_name="TechCorp Inc.",
            position_title="Senior Software Engineer",
            location="San Francisco, CA",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 12, 31),
            is_current=False,
            description="Led development of microservices architecture",
            achievements=[
                "Improved system performance by 40%",
                "Mentored 3 junior developers",
            ],
            technologies=["Python", "FastAPI", "PostgreSQL", "Docker"],
        )

        experience = await resume_service.add_work_experience(
            db, created_resume.id, test_user.id, exp_data
        )

        assert experience is not None
        assert experience.company_name == "TechCorp Inc."
        assert experience.position_title == "Senior Software Engineer"
        assert len(experience.achievements) == 2
        assert len(experience.technologies) == 4

    async def test_duplicate_resume_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test successful resume duplication."""
        from app.schemas.resume import ResumeCreate

        # Create resume first
        resume_data = ResumeCreate(**sample_resume_data)
        original_resume = await resume_service.create_resume(
            db, resume_data, test_user.id
        )

        # Duplicate resume
        duplicated_resume = await resume_service.duplicate_resume(
            db, original_resume.id, test_user.id
        )

        assert duplicated_resume is not None
        assert duplicated_resume.id != original_resume.id
        assert duplicated_resume.title == f"{original_resume.title} (Copy)"
        assert duplicated_resume.full_name == original_resume.full_name
        assert duplicated_resume.status == ResumeStatus.DRAFT

    # === ERROR SCENARIOS ===

    async def test_get_resume_unauthorized(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test resume retrieval with wrong user ID fails."""
        from app.schemas.resume import ResumeCreate

        # Create resume
        resume_data = ResumeCreate(**sample_resume_data)
        created_resume = await resume_service.create_resume(
            db, resume_data, test_user.id
        )

        # Try to access with wrong user ID
        retrieved_resume = await resume_service.get_resume(
            db, created_resume.id, test_user.id + 999
        )

        assert retrieved_resume is None

    async def test_update_resume_not_found(
        self, db: AsyncSession, test_user: User, resume_service: ResumeService
    ):
        """Test updating non-existent resume fails."""
        from app.schemas.resume import ResumeUpdate

        update_data = ResumeUpdate(title="Updated Title")

        updated_resume = await resume_service.update_resume(
            db, 999999, test_user.id, update_data
        )

        assert updated_resume is None

    async def test_delete_resume_not_found(
        self, db: AsyncSession, test_user: User, resume_service: ResumeService
    ):
        """Test deleting non-existent resume fails."""
        success = await resume_service.delete_resume(db, 999999, test_user.id)

        assert success is False

    async def test_add_work_experience_invalid_resume(
        self, db: AsyncSession, test_user: User, resume_service: ResumeService
    ):
        """Test adding work experience to non-existent resume fails."""
        from app.schemas.resume import WorkExperienceCreate

        exp_data = WorkExperienceCreate(
            company_name="TechCorp Inc.",
            position_title="Senior Software Engineer",
            start_date=datetime(2020, 1, 1),
            is_current=True,
            description="Test description",
        )

        experience = await resume_service.add_work_experience(
            db, 999999, test_user.id, exp_data
        )

        assert experience is None

    # === BUSINESS LOGIC TESTS ===

    async def test_resume_status_transitions(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test resume status transitions."""
        from app.schemas.resume import ResumeCreate, ResumeUpdate

        # Create draft resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        assert resume.status == ResumeStatus.DRAFT

        # Publish resume
        updated_resume = await resume_service.update_resume(
            db, resume.id, test_user.id, ResumeUpdate(status=ResumeStatus.PUBLISHED)
        )

        assert updated_resume.status == ResumeStatus.PUBLISHED

        # Archive resume
        archived_resume = await resume_service.update_resume(
            db, resume.id, test_user.id, ResumeUpdate(status=ResumeStatus.ARCHIVED)
        )

        assert archived_resume.status == ResumeStatus.ARCHIVED

    async def test_resume_visibility_settings(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test resume visibility settings."""
        from app.schemas.resume import ResumeCreate, ResumeUpdate

        # Create private resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        assert resume.visibility == ResumeVisibility.PRIVATE

        # Make public
        public_resume = await resume_service.update_resume(
            db,
            resume.id,
            test_user.id,
            ResumeUpdate(visibility=ResumeVisibility.PUBLIC),
        )

        assert public_resume.visibility == ResumeVisibility.PUBLIC

    async def test_japanese_resume_format(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test Japanese resume format (履歴書)."""
        from app.schemas.resume import ResumeCreate, ResumeUpdate

        # Create resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        # Convert to Japanese format
        japanese_resume = await resume_service.update_resume(
            db,
            resume.id,
            test_user.id,
            ResumeUpdate(
                resume_format=ResumeFormat.RIREKISHO,
                resume_language=ResumeLanguage.JAPANESE,
                furigana_name="ジョン ドウ",
                birth_date=datetime(1990, 1, 1),
                gender="male",
                nationality="American",
            ),
        )

        assert japanese_resume.resume_format == ResumeFormat.RIREKISHO
        assert japanese_resume.resume_language == ResumeLanguage.JAPANESE
        assert japanese_resume.furigana_name == "ジョン ドウ"

    # === SHARING FUNCTIONALITY TESTS ===

    async def test_create_share_link_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test creating share link."""
        from app.schemas.resume import ResumeCreate

        # Create resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        # Create share link
        share_token = await resume_service.create_share_link(
            db,
            resume.id,
            test_user.id,
            recipient_email="recipient@example.com",
            expires_in_days=30,
            max_views=10,
        )

        assert share_token is not None
        assert len(share_token) > 20

    async def test_get_shared_resume_success(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test accessing shared resume."""
        from app.schemas.resume import ResumeCreate

        # Create resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        # Create share link
        share_token = await resume_service.create_share_link(
            db, resume.id, test_user.id, expires_in_days=30
        )

        # Access shared resume
        shared_resume = await resume_service.get_shared_resume(db, share_token)

        assert shared_resume is not None
        assert shared_resume.id == resume.id

    # === PUBLIC ACCESS TESTS ===

    async def test_public_resume_access(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test public resume access by slug."""
        from app.schemas.resume import ResumeCreate

        # Create resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        # Make public
        await resume_service.update_public_settings(
            db, resume.id, test_user.id, is_public=True, can_download_pdf=True
        )

        # Access public resume
        public_resume = await resume_service.get_public_resume(
            db, resume.public_url_slug
        )

        assert public_resume is not None
        assert public_resume.id == resume.id

    # === EDGE CASES ===

    async def test_resume_with_empty_sections(
        self, db: AsyncSession, test_user: User, resume_service: ResumeService
    ):
        """Test resume creation with minimal data."""
        from app.schemas.resume import ResumeCreate

        minimal_data = ResumeCreate(
            title="Minimal Resume", full_name="Test User", email="test@example.com"
        )

        resume = await resume_service.create_resume(db, minimal_data, test_user.id)

        assert resume is not None
        assert resume.title == "Minimal Resume"
        assert resume.description is None
        assert resume.professional_summary is None

    async def test_resume_with_maximum_data(
        self, db: AsyncSession, test_user: User, resume_service: ResumeService
    ):
        """Test resume with all fields populated."""
        from app.schemas.resume import ResumeCreate

        max_data = ResumeCreate(
            title="Complete Software Engineer Resume",
            description="Comprehensive resume with all details",
            full_name="Jane Smith",
            email="jane.smith@example.com",
            phone="+1-555-0199",
            location="Seattle, WA",
            website="https://janesmith.dev",
            linkedin_url="https://linkedin.com/in/janesmith",
            github_url="https://github.com/janesmith",
            professional_summary="Highly experienced software engineer with expertise in multiple domains.",
            objective="Seeking a lead engineer position to drive technical innovation.",
            template_id="professional",
            theme_color="#059669",
            font_family="Source Sans Pro",
        )

        resume = await resume_service.create_resume(db, max_data, test_user.id)

        assert resume is not None
        assert all(
            [
                resume.title,
                resume.description,
                resume.full_name,
                resume.email,
                resume.phone,
                resume.location,
                resume.website,
                resume.linkedin_url,
                resume.github_url,
                resume.professional_summary,
                resume.objective,
            ]
        )

    # === PERFORMANCE TESTS ===

    async def test_bulk_resume_operations(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test creating multiple resumes."""
        from app.schemas.resume import ResumeCreate

        resumes = []

        # Create 5 resumes
        for i in range(5):
            data = sample_resume_data.copy()
            data["title"] = f"Resume {i + 1}"
            data["email"] = f"user{i + 1}@example.com"

            resume_data = ResumeCreate(**data)
            resume = await resume_service.create_resume(db, resume_data, test_user.id)
            resumes.append(resume)

        assert len(resumes) == 5

        # Verify all resumes exist
        user_resumes = await resume_service.get_user_resumes(db, test_user.id, limit=10)
        assert len(user_resumes) == 5

    async def test_resume_with_all_sections(
        self,
        db: AsyncSession,
        test_user: User,
        sample_resume_data: dict,
        resume_service: ResumeService,
    ):
        """Test resume with work experience, education, and skills."""
        from app.schemas.resume import (
            EducationCreate,
            ResumeCreate,
            SkillCreate,
            WorkExperienceCreate,
        )

        # Create resume
        resume_data = ResumeCreate(**sample_resume_data)
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        # Add work experience
        exp_data = WorkExperienceCreate(
            company_name="TechCorp",
            position_title="Software Engineer",
            start_date=datetime(2020, 1, 1),
            is_current=True,
            description="Full-stack development",
        )
        await resume_service.add_work_experience(db, resume.id, test_user.id, exp_data)

        # Add education
        edu_data = EducationCreate(
            institution_name="University of Technology",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            start_date=datetime(2016, 9, 1),
            end_date=datetime(2020, 5, 31),
            gpa="3.8/4.0",
        )
        await resume_service.add_education(db, resume.id, test_user.id, edu_data)

        # Add skills
        skill_data = SkillCreate(
            name="Python",
            category="Programming Languages",
            proficiency_level=5,
            proficiency_label="Expert",
        )
        await resume_service.add_skill(db, resume.id, test_user.id, skill_data)

        # Verify all sections
        complete_resume = await resume_service.get_resume(db, resume.id, test_user.id)

        assert len(complete_resume.experiences) == 1
        assert len(complete_resume.educations) == 1
        assert len(complete_resume.skills) == 1
        assert complete_resume.experiences[0].company_name == "TechCorp"
        assert (
            complete_resume.educations[0].institution_name == "University of Technology"
        )
        assert complete_resume.skills[0].name == "Python"


class TestResumeEndpoints:
    """Test resume API endpoints with real HTTP requests."""

    @pytest.fixture
    def client(self):
        """Test client for API calls."""
        return TestClient(app)

    @pytest.fixture
    async def auth_headers(self, client: TestClient, test_user: User):
        """Authentication headers for API calls."""
        # This would typically involve login to get JWT token
        # For now, we'll mock the authentication
        return {"Authorization": f"Bearer mock_jwt_token_user_{test_user.id}"}

    async def test_create_resume_endpoint(
        self, client: TestClient, auth_headers: dict, sample_resume_data: dict
    ):
        """Test POST /api/resumes endpoint."""
        response = client.post(
            "/api/resumes/", json=sample_resume_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_resume_data["title"]
        assert "id" in data
        assert "created_at" in data

    async def test_get_resume_endpoint(
        self, client: TestClient, auth_headers: dict, sample_resume_data: dict
    ):
        """Test GET /api/resumes/{id} endpoint."""
        # Create resume first
        create_response = client.post(
            "/api/resumes/", json=sample_resume_data, headers=auth_headers
        )
        resume_id = create_response.json()["id"]

        # Get resume
        response = client.get(f"/api/resumes/{resume_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume_id
        assert data["title"] == sample_resume_data["title"]

    async def test_list_resumes_endpoint(self, client: TestClient, auth_headers: dict):
        """Test GET /api/resumes endpoint."""
        response = client.get("/api/resumes/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "resumes" in data
        assert "total" in data
        assert "has_more" in data

    async def test_update_resume_endpoint(
        self, client: TestClient, auth_headers: dict, sample_resume_data: dict
    ):
        """Test PUT /api/resumes/{id} endpoint."""
        # Create resume first
        create_response = client.post(
            "/api/resumes/", json=sample_resume_data, headers=auth_headers
        )
        resume_id = create_response.json()["id"]

        # Update resume
        update_data = {
            "title": "Updated Resume Title",
            "professional_summary": "Updated summary",
        }

        response = client.put(
            f"/api/resumes/{resume_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Resume Title"
        assert data["professional_summary"] == "Updated summary"

    async def test_delete_resume_endpoint(
        self, client: TestClient, auth_headers: dict, sample_resume_data: dict
    ):
        """Test DELETE /api/resumes/{id} endpoint."""
        # Create resume first
        create_response = client.post(
            "/api/resumes/", json=sample_resume_data, headers=auth_headers
        )
        resume_id = create_response.json()["id"]

        # Delete resume
        response = client.delete(f"/api/resumes/{resume_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_get_resume_stats_endpoint(
        self, client: TestClient, auth_headers: dict
    ):
        """Test GET /api/resumes/stats endpoint."""
        response = client.get("/api/resumes/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_resumes" in data
        assert "by_status" in data
        assert "total_views" in data
        assert "total_downloads" in data

    # === ERROR ENDPOINT TESTS ===

    async def test_get_resume_unauthorized_endpoint(self, client: TestClient):
        """Test accessing resume without authentication."""
        response = client.get("/api/resumes/1")

        assert response.status_code == 401

    async def test_get_nonexistent_resume_endpoint(
        self, client: TestClient, auth_headers: dict
    ):
        """Test accessing non-existent resume."""
        response = client.get("/api/resumes/999999", headers=auth_headers)

        assert response.status_code == 404

    async def test_create_resume_invalid_data_endpoint(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating resume with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "email": "invalid-email",  # Invalid email format
        }

        response = client.post("/api/resumes/", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422
        assert "detail" in response.json()


# === INTEGRATION SCENARIOS ===


class TestResumeIntegrationScenarios:
    """Integration tests combining multiple resume operations."""

    async def test_complete_resume_lifecycle(
        self, db: AsyncSession, test_user: User, resume_service: ResumeService
    ):
        """Test complete resume lifecycle from creation to deletion."""
        from app.schemas.resume import (
            EducationCreate,
            ResumeCreate,
            ResumeUpdate,
            SkillCreate,
            WorkExperienceCreate,
        )

        # 1. Create resume
        resume_data = ResumeCreate(
            title="Complete Lifecycle Resume",
            full_name="Test User",
            email="test@example.com",
            professional_summary="Initial summary",
        )
        resume = await resume_service.create_resume(db, resume_data, test_user.id)

        # 2. Add work experience
        exp_data = WorkExperienceCreate(
            company_name="StartupCorp",
            position_title="Junior Developer",
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 12, 31),
            description="First job experience",
        )
        await resume_service.add_work_experience(db, resume.id, test_user.id, exp_data)

        # 3. Add education
        edu_data = EducationCreate(
            institution_name="Tech University",
            degree="Bachelor's",
            field_of_study="Computer Science",
            start_date=datetime(2017, 9, 1),
            end_date=datetime(2021, 5, 31),
        )
        await resume_service.add_education(db, resume.id, test_user.id, edu_data)

        # 4. Add skills
        skill_data = SkillCreate(
            name="JavaScript", category="Programming", proficiency_level=4
        )
        await resume_service.add_skill(db, resume.id, test_user.id, skill_data)

        # 5. Update resume status
        await resume_service.update_resume(
            db, resume.id, test_user.id, ResumeUpdate(status=ResumeStatus.PUBLISHED)
        )

        # 6. Make resume public
        await resume_service.update_public_settings(
            db, resume.id, test_user.id, is_public=True
        )

        # 7. Create share link
        share_token = await resume_service.create_share_link(
            db, resume.id, test_user.id, expires_in_days=30
        )

        # 8. Duplicate resume
        duplicate = await resume_service.duplicate_resume(db, resume.id, test_user.id)

        # 9. Verify final state
        final_resume = await resume_service.get_resume(db, resume.id, test_user.id)

        assert final_resume.status == ResumeStatus.PUBLISHED
        assert final_resume.is_public is True
        assert len(final_resume.experiences) == 1
        assert len(final_resume.educations) == 1
        assert len(final_resume.skills) == 1
        assert duplicate is not None
        assert share_token is not None

    async def test_multi_user_resume_isolation(
        self, db: AsyncSession, resume_service: ResumeService
    ):
        """Test that users can only access their own resumes."""
        from app.schemas.resume import ResumeCreate

        # Create two users
        user1 = User(
            email="user1@example.com",
            username="user1",
            full_name="User One",
            hashed_password="$2b$12$test_hash",
            is_active=True,
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            full_name="User Two",
            hashed_password="$2b$12$test_hash",
            is_active=True,
        )

        db.add(user1)
        db.add(user2)
        await db.commit()
        await db.refresh(user1)
        await db.refresh(user2)

        # Create resume for user1
        resume_data = ResumeCreate(
            title="User 1 Resume", full_name="User One", email="user1@example.com"
        )
        user1_resume = await resume_service.create_resume(db, resume_data, user1.id)

        # Create resume for user2
        resume_data.title = "User 2 Resume"
        resume_data.email = "user2@example.com"
        user2_resume = await resume_service.create_resume(db, resume_data, user2.id)

        # Verify isolation
        user1_resumes = await resume_service.get_user_resumes(db, user1.id)
        user2_resumes = await resume_service.get_user_resumes(db, user2.id)

        assert len(user1_resumes) == 1
        assert len(user2_resumes) == 1
        assert user1_resumes[0].id == user1_resume.id
        assert user2_resumes[0].id == user2_resume.id

        # User1 cannot access user2's resume
        unauthorized_access = await resume_service.get_resume(
            db, user2_resume.id, user1.id
        )
        assert unauthorized_access is None
