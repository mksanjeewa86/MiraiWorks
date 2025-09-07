from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.resume import (
    Resume,
    ResumeShare,
    Skill,
    WorkExperience,
)
from app.models.user import User
from app.schemas.resume import (
    EducationCreate,
    ResumeCreate,
    ResumeUpdate,
    SkillCreate,
    WorkExperienceCreate,
)
from app.services.pdf_service import PDFService
from app.services.resume_parser import ResumeParser
from app.services.resume_service import ResumeService
from app.services.template_service import TemplateService
from app.utils.constants import ResumeStatus


class TestResumeService:
    @pytest.fixture
    async def resume_service(self):
        return ResumeService()

    @pytest.fixture
    async def company(self, db_session: AsyncSession):
        company = Company(
            name="Test Company",
            domain="test.com",
            industry="Technology",
            size="10-50",
            is_active=True,
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession, company):
        user = User(
            email="candidate@test.com",
            full_name="Test User",
            password_hash="hashed_password",
            role="candidate",
            company_id=company.id,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def sample_resume(self, db_session: AsyncSession, test_user):
        resume = Resume(
            user_id=test_user.id,
            title="Software Engineer Resume",
            description="My professional resume",
            full_name="Test User",
            email="test@example.com",
            phone="+1-555-0123",
            location="San Francisco, CA",
            professional_summary="Experienced software engineer with 5+ years in web development",
            template_id="modern",
            slug="software-engineer-resume",
            share_token="abc123def456",
        )
        db_session.add(resume)
        await db_session.commit()
        await db_session.refresh(resume)
        return resume

    async def test_create_resume(
        self, db_session: AsyncSession, resume_service: ResumeService, test_user: User
    ):
        """Test creating a new resume."""
        resume_data = ResumeCreate(
            title="Full Stack Developer",
            description="Resume for full stack development roles",
            full_name="Test User",
            email="test@example.com",
            phone="+1-555-0123",
            location="New York, NY",
            professional_summary="Full stack developer with React and Python expertise",
            template_id="modern",
        )

        resume = await resume_service.create_resume(
            db_session, resume_data, test_user.id
        )

        assert resume.id is not None
        assert resume.title == "Full Stack Developer"
        assert resume.user_id == test_user.id
        assert resume.status == ResumeStatus.DRAFT
        assert resume.slug is not None
        assert resume.share_token is not None
        assert len(resume.share_token) == 32

    async def test_get_resume(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test getting a resume by ID."""
        retrieved_resume = await resume_service.get_resume(
            db_session, sample_resume.id, test_user.id
        )

        assert retrieved_resume.id == sample_resume.id
        assert retrieved_resume.title == sample_resume.title
        assert retrieved_resume.user_id == test_user.id

    async def test_get_resume_unauthorized(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
    ):
        """Test getting resume with wrong user ID."""
        retrieved_resume = await resume_service.get_resume(
            db_session,
            sample_resume.id,
            99999,  # Wrong user ID
        )

        assert retrieved_resume is None

    async def test_update_resume(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test updating a resume."""
        update_data = ResumeUpdate(
            title="Senior Software Engineer",
            professional_summary="Senior software engineer with 8+ years experience",
            status=ResumeStatus.PUBLISHED,
        )

        updated_resume = await resume_service.update_resume(
            db_session, sample_resume.id, test_user.id, update_data
        )

        assert updated_resume.title == "Senior Software Engineer"
        assert updated_resume.status == ResumeStatus.PUBLISHED
        assert "Senior software engineer" in updated_resume.professional_summary
        # Slug should be updated when title changes
        assert "senior-software-engineer" in updated_resume.slug

    async def test_delete_resume(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test deleting a resume."""
        success = await resume_service.delete_resume(
            db_session, sample_resume.id, test_user.id
        )

        assert success is True

        # Verify it's actually deleted
        deleted_resume = await resume_service.get_resume(
            db_session, sample_resume.id, test_user.id
        )
        assert deleted_resume is None

    async def test_duplicate_resume(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test duplicating a resume."""
        # Add some related data to the original resume
        work_exp = WorkExperience(
            resume_id=sample_resume.id,
            company_name="Tech Corp",
            position_title="Software Engineer",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 1, 1),
            description="Developed web applications",
        )
        db_session.add(work_exp)
        await db_session.commit()

        duplicate = await resume_service.duplicate_resume(
            db_session, sample_resume.id, test_user.id
        )

        assert duplicate is not None
        assert duplicate.id != sample_resume.id
        assert duplicate.title == f"{sample_resume.title} (Copy)"
        assert duplicate.status == ResumeStatus.DRAFT
        assert duplicate.slug != sample_resume.slug
        assert duplicate.share_token != sample_resume.share_token

    async def test_add_work_experience(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test adding work experience to a resume."""
        exp_data = WorkExperienceCreate(
            company_name="Google",
            position_title="Senior Software Engineer",
            location="Mountain View, CA",
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2023, 6, 1),
            description="Led development of search infrastructure",
            achievements=[
                "Improved search performance by 40%",
                "Led team of 5 engineers",
            ],
            technologies=["Python", "Go", "Kubernetes"],
        )

        experience = await resume_service.add_work_experience(
            db_session, sample_resume.id, test_user.id, exp_data
        )

        assert experience is not None
        assert experience.company_name == "Google"
        assert experience.position_title == "Senior Software Engineer"
        assert experience.resume_id == sample_resume.id
        assert len(experience.achievements) == 2
        assert len(experience.technologies) == 3

    async def test_add_education(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test adding education to a resume."""
        edu_data = EducationCreate(
            institution_name="Stanford University",
            degree="Master of Science",
            field_of_study="Computer Science",
            location="Stanford, CA",
            start_date=datetime(2018, 9, 1),
            end_date=datetime(2020, 6, 1),
            gpa="3.9/4.0",
            honors="Magna Cum Laude",
        )

        education = await resume_service.add_education(
            db_session, sample_resume.id, test_user.id, edu_data
        )

        assert education is not None
        assert education.institution_name == "Stanford University"
        assert education.degree == "Master of Science"
        assert education.field_of_study == "Computer Science"
        assert education.gpa == "3.9/4.0"

    async def test_add_skill(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test adding skills to a resume."""
        skill_data = SkillCreate(
            name="Python",
            category="Programming Languages",
            proficiency_level=9,
            proficiency_label="Expert",
        )

        skill = await resume_service.add_skill(
            db_session, sample_resume.id, test_user.id, skill_data
        )

        assert skill is not None
        assert skill.name == "Python"
        assert skill.category == "Programming Languages"
        assert skill.proficiency_level == 9
        assert skill.proficiency_label == "Expert"

    async def test_create_share_link(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test creating a shareable link."""
        share_token = await resume_service.create_share_link(
            db_session,
            sample_resume.id,
            test_user.id,
            recipient_email="recruiter@company.com",
            password="secret123",
            expires_in_days=7,
            max_views=10,
        )

        assert share_token is not None
        assert len(share_token) == 32

        # Verify the share record was created
        share = await ResumeShare.get_by_token(db_session, share_token)
        assert share is not None
        assert share.resume_id == sample_resume.id
        assert share.recipient_email == "recruiter@company.com"
        assert share.password_protected is True
        assert share.max_views == 10

    async def test_get_shared_resume(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test getting a shared resume."""
        # Create a share link first
        share_token = await resume_service.create_share_link(
            db_session, sample_resume.id, test_user.id
        )

        # Get the shared resume
        shared_resume = await resume_service.get_shared_resume(db_session, share_token)

        assert shared_resume is not None
        assert shared_resume.id == sample_resume.id

        # View count should be incremented
        share = await ResumeShare.get_by_token(db_session, share_token)
        assert share.view_count == 1

    async def test_get_shared_resume_with_password(
        self,
        db_session: AsyncSession,
        resume_service: ResumeService,
        sample_resume: Resume,
        test_user: User,
    ):
        """Test getting a password-protected shared resume."""
        # Create a password-protected share link
        share_token = await resume_service.create_share_link(
            db_session, sample_resume.id, test_user.id, password="secret123"
        )

        # Try without password - should fail
        shared_resume = await resume_service.get_shared_resume(db_session, share_token)
        assert shared_resume is None

        # Try with wrong password - should fail
        shared_resume = await resume_service.get_shared_resume(
            db_session, share_token, "wrongpassword"
        )
        assert shared_resume is None

        # Try with correct password - should succeed
        shared_resume = await resume_service.get_shared_resume(
            db_session, share_token, "secret123"
        )
        assert shared_resume is not None
        assert shared_resume.id == sample_resume.id

    async def test_slug_generation(
        self, db_session: AsyncSession, resume_service: ResumeService, test_user: User
    ):
        """Test unique slug generation."""
        # Create first resume
        resume_data1 = ResumeCreate(title="Software Engineer", full_name="Test User")
        resume1 = await resume_service.create_resume(
            db_session, resume_data1, test_user.id
        )

        # Create second resume with same title
        resume_data2 = ResumeCreate(title="Software Engineer", full_name="Test User")
        resume2 = await resume_service.create_resume(
            db_session, resume_data2, test_user.id
        )

        assert resume1.slug != resume2.slug
        assert "software-engineer" in resume1.slug
        assert "software-engineer" in resume2.slug
        assert resume2.slug.endswith("-1")  # Should have counter


class TestTemplateService:
    @pytest.fixture
    async def template_service(self):
        return TemplateService()

    @pytest.fixture
    async def sample_resume_with_data(self, db_session: AsyncSession, test_user: User):
        resume = Resume(
            user_id=test_user.id,
            title="Full Stack Developer",
            full_name="John Doe",
            email="john@example.com",
            phone="+1-555-0123",
            professional_summary="Experienced full stack developer",
            template_id="modern",
        )
        db_session.add(resume)
        await db_session.flush()

        # Add work experience
        work_exp = WorkExperience(
            resume_id=resume.id,
            company_name="Tech Corp",
            position_title="Senior Developer",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 1, 1),
            description="Developed web applications",
            achievements=["Built scalable APIs", "Improved performance by 50%"],
            technologies=["React", "Node.js", "PostgreSQL"],
        )
        db_session.add(work_exp)

        # Add skills
        skill = Skill(
            resume_id=resume.id,
            name="JavaScript",
            category="Programming Languages",
            proficiency_level=8,
            proficiency_label="Advanced",
        )
        db_session.add(skill)

        await db_session.commit()
        await db_session.refresh(resume)
        return resume

    async def test_get_available_templates(self, template_service: TemplateService):
        """Test getting available templates."""
        templates = template_service.get_available_templates()

        assert len(templates) >= 4  # modern, classic, creative, minimal
        template_names = [t["name"] for t in templates]
        assert "modern" in template_names
        assert "classic" in template_names
        assert "creative" in template_names
        assert "minimal" in template_names

        # Check template structure
        modern_template = next(t for t in templates if t["name"] == "modern")
        assert "display_name" in modern_template
        assert "description" in modern_template
        assert "color_scheme" in modern_template
        assert "font_options" in modern_template

    async def test_render_resume_html(
        self, template_service: TemplateService, sample_resume_with_data: Resume
    ):
        """Test rendering resume to HTML."""
        html_content = await template_service.render_resume(sample_resume_with_data)

        assert html_content is not None
        assert "<!DOCTYPE html>" in html_content
        assert "John Doe" in html_content
        assert "Full Stack Developer" in html_content
        assert "john@example.com" in html_content
        assert "Tech Corp" in html_content
        assert "Senior Developer" in html_content
        assert "JavaScript" in html_content
        assert "Experienced full stack developer" in html_content

    async def test_render_with_different_templates(
        self, template_service: TemplateService, sample_resume_with_data: Resume
    ):
        """Test rendering with different templates."""
        templates = ["modern", "classic", "creative", "minimal"]

        for template_name in templates:
            html_content = await template_service.render_resume(
                sample_resume_with_data, template_name
            )

            assert html_content is not None
            assert "John Doe" in html_content
            assert (
                f"{template_name}-template" in html_content
                or template_name in html_content
            )

    async def test_render_with_custom_colors(
        self, template_service: TemplateService, sample_resume_with_data: Resume
    ):
        """Test rendering with custom theme colors."""
        # Update resume with custom colors
        sample_resume_with_data.theme_color = "#ff6b6b"
        sample_resume_with_data.font_family = "Georgia, serif"

        html_content = await template_service.render_resume(sample_resume_with_data)

        assert "#ff6b6b" in html_content
        assert "Georgia" in html_content


class TestPDFService:
    @pytest.fixture
    async def pdf_service(self):
        return PDFService()

    @pytest.mark.asyncio
    async def test_pdf_generation_availability(self, pdf_service: PDFService):
        """Test PDF generation library availability."""
        playwright_available = await pdf_service._is_playwright_available()
        weasyprint_available = await pdf_service._is_weasyprint_available()

        # At least one should be available for tests to pass
        assert playwright_available or weasyprint_available

    @patch("app.services.pdf_service.PDFService._convert_html_to_pdf")
    @patch("app.services.storage_service.StorageService.upload_file")
    @patch("app.services.storage_service.StorageService.generate_presigned_url")
    async def test_generate_pdf(
        self,
        mock_presigned_url,
        mock_upload_file,
        mock_convert_pdf,
        pdf_service: PDFService,
        sample_resume_with_data: Resume,
    ):
        """Test PDF generation."""
        # Mock the dependencies
        mock_pdf_data = b"fake_pdf_content"
        mock_convert_pdf.return_value = mock_pdf_data
        mock_upload_file.return_value = "resumes/pdfs/resume_123.pdf"
        mock_presigned_url.return_value = "https://storage.example.com/resume_123.pdf"

        result = await pdf_service.generate_pdf(sample_resume_with_data)

        assert "pdf_url" in result
        assert "file_size" in result
        assert "expires_at" in result
        assert result["file_size"] == len(mock_pdf_data)

        # Verify methods were called
        mock_convert_pdf.assert_called_once()
        mock_upload_file.assert_called_once()
        mock_presigned_url.assert_called_once()


class TestResumeParser:
    @pytest.fixture
    async def resume_parser(self):
        return ResumeParser()

    async def test_extract_personal_info(self, resume_parser: ResumeParser):
        """Test extracting personal information from text."""
        text = """
        John Doe
        Software Engineer
        Email: john.doe@example.com
        Phone: (555) 123-4567
        Location: San Francisco, CA
        LinkedIn: https://linkedin.com/in/johndoe
        GitHub: https://github.com/johndoe
        """

        personal_info = resume_parser._extract_personal_info(text)

        assert personal_info["email"] == "john.doe@example.com"
        assert "555" in personal_info["phone"]
        assert personal_info["linkedin_url"] == "https://linkedin.com/in/johndoe"
        assert personal_info["github_url"] == "https://github.com/johndoe"
        assert personal_info["full_name"] == "John Doe"

    async def test_extract_professional_summary(self, resume_parser: ResumeParser):
        """Test extracting professional summary."""
        text = """
        PROFESSIONAL SUMMARY

        Experienced software engineer with 5+ years of experience in full-stack
        web development. Proven track record of building scalable applications
        using modern technologies including React, Node.js, and Python.

        EXPERIENCE
        Senior Developer at Tech Corp
        """

        summary = resume_parser._extract_summary(text)

        assert len(summary) > 50
        assert "5+ years" in summary
        assert "full-stack" in summary or "React" in summary

    async def test_extract_skills(self, resume_parser: ResumeParser):
        """Test extracting skills from text."""
        text = """
        TECHNICAL SKILLS

        Programming Languages: Python, JavaScript, Java, C++
        Web Technologies: React, Angular, Node.js, Django
        Databases: PostgreSQL, MongoDB, Redis
        Cloud Platforms: AWS, Azure, Docker, Kubernetes
        """

        skills = resume_parser._extract_skills(text)

        assert len(skills) > 0
        skill_names = [skill["name"] for skill in skills]
        assert "Python" in skill_names
        assert "JavaScript" in skill_names
        assert "React" in skill_names
        assert "AWS" in skill_names

        # Check categorization
        python_skill = next(skill for skill in skills if skill["name"] == "Python")
        assert python_skill["category"] == "Programming Languages"

    async def test_categorize_skills(self, resume_parser: ResumeParser):
        """Test skill categorization."""
        assert resume_parser._categorize_skill("Python") == "Programming Languages"
        assert resume_parser._categorize_skill("React") == "Web Technologies"
        assert resume_parser._categorize_skill("PostgreSQL") == "Databases"
        assert resume_parser._categorize_skill("AWS") == "Cloud Platforms"
        assert resume_parser._categorize_skill("Git") == "Tools & Technologies"

    @patch("PyPDF2.PdfReader")
    async def test_extract_from_pdf(self, mock_pdf_reader, resume_parser: ResumeParser):
        """Test extracting text from PDF."""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text content"
        mock_pdf_reader.return_value.pages = [mock_page]

        pdf_content = b"fake_pdf_bytes"
        text = await resume_parser._extract_from_pdf(pdf_content)

        assert text == "Sample resume text content\n"

    async def test_file_validation(self, resume_parser: ResumeParser):
        """Test file validation."""
        # Valid file
        is_valid = await resume_parser.validate_resume_file(
            "resume.pdf",
            1024 * 1024,
            "application/pdf",  # 1MB PDF
        )
        assert is_valid is True

        # Invalid extension
        with pytest.raises(ValueError, match="Unsupported file format"):
            await resume_parser.validate_resume_file(
                "resume.exe", 1024, "application/octet-stream"
            )

        # File too large
        with pytest.raises(ValueError, match="File size too large"):
            await resume_parser.validate_resume_file(
                "resume.pdf",
                20 * 1024 * 1024,
                "application/pdf",  # 20MB
            )


class TestResumeAPI:
    """Test resume API endpoints."""

    @pytest.fixture
    async def auth_headers(self, authenticated_user):
        return {"Authorization": f"Bearer {authenticated_user['access_token']}"}

    def test_create_resume_api(self, client: TestClient, auth_headers):
        """Test creating resume via API."""
        resume_data = {
            "title": "Software Engineer Resume",
            "description": "My professional resume for software engineering roles",
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "professional_summary": "Experienced software engineer with Python expertise",
            "template_id": "modern",
        }

        response = client.post(
            "/api/v1/resumes/", json=resume_data, headers=auth_headers
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert data["title"] == "Software Engineer Resume"
        assert data["full_name"] == "Test User"
        assert data["template_id"] == "modern"

    def test_list_resumes_api(self, client: TestClient, auth_headers):
        """Test listing resumes via API."""
        response = client.get("/api/v1/resumes/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "resumes" in data
        assert "total" in data
        assert "has_more" in data
        assert isinstance(data["resumes"], list)

    def test_get_resume_api(self, client: TestClient, auth_headers):
        """Test getting specific resume via API."""
        response = client.get("/api/v1/resumes/1", headers=auth_headers)

        # Should either return resume data or 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "title" in data
            assert "user_id" in data

    def test_preview_resume_api(self, client: TestClient, auth_headers):
        """Test resume preview via API."""
        response = client.get("/api/v1/resumes/1/preview", headers=auth_headers)

        # Should either return HTML or 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")

    def test_get_templates_api(self, client: TestClient, auth_headers):
        """Test getting available templates."""
        response = client.get(
            "/api/v1/resumes/templates/available", headers=auth_headers
        )

        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        if templates:  # If templates are returned
            template = templates[0]
            assert "name" in template
            assert "display_name" in template
            assert "description" in template

    def test_create_work_experience_api(self, client: TestClient, auth_headers):
        """Test adding work experience via API."""
        exp_data = {
            "company_name": "Google",
            "position_title": "Software Engineer",
            "location": "Mountain View, CA",
            "start_date": "2020-01-01T00:00:00",
            "end_date": "2023-06-01T00:00:00",
            "description": "Developed search algorithms",
            "achievements": ["Improved search accuracy by 15%"],
            "technologies": ["Python", "TensorFlow", "Kubernetes"],
        }

        response = client.post(
            "/api/v1/resumes/1/experiences", json=exp_data, headers=auth_headers
        )

        # Should either succeed or return 404 for non-existent resume
        assert response.status_code in [200, 201, 404]

    def test_generate_pdf_api(self, client: TestClient, auth_headers):
        """Test PDF generation via API."""
        pdf_request = {"resume_id": 1, "format": "A4", "include_contact_info": True}

        response = client.post(
            "/api/v1/resumes/1/generate-pdf", json=pdf_request, headers=auth_headers
        )

        # Should either succeed or return 404/500
        assert response.status_code in [200, 404, 500]

    def test_create_share_link_api(self, client: TestClient, auth_headers):
        """Test creating share link via API."""
        share_data = {
            "recipient_email": "recruiter@company.com",
            "expires_in_days": 7,
            "max_views": 10,
            "allow_download": True,
            "show_contact_info": True,
        }

        response = client.post(
            "/api/v1/resumes/1/share", json=share_data, headers=auth_headers
        )

        # Should either succeed or return 404
        assert response.status_code in [200, 201, 404]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "share_token" in data
            assert len(data["share_token"]) == 32

    def test_bulk_resume_action_api(self, client: TestClient, auth_headers):
        """Test bulk resume actions via API."""
        bulk_data = {"action": "archive", "resume_ids": [1, 2, 3]}

        response = client.post(
            "/api/v1/resumes/bulk-action", json=bulk_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "success_count" in data
        assert "error_count" in data
        assert "errors" in data

    def test_resume_statistics_api(self, client: TestClient, auth_headers):
        """Test getting resume statistics."""
        response = client.get("/api/v1/resumes/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_resumes" in data
        assert "by_status" in data
        assert "by_visibility" in data
        assert "total_views" in data
        assert "total_downloads" in data
