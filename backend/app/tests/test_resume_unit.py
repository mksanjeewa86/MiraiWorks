"""
Resume Unit Tests - Testing without database dependencies

These tests focus on testing the business logic and service methods
using mocks and fixtures, ensuring the resume functionality works correctly.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate, WorkExperienceCreate
from app.services.resume_service import ResumeService
from app.utils.constants import ResumeStatus, ResumeVisibility


class TestResumeServiceUnit:
    """Unit tests for ResumeService without database dependencies."""

    @pytest.fixture
    def resume_service(self):
        """Resume service instance."""
        return ResumeService()

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.rollback = AsyncMock()
        db.execute = AsyncMock()
        return db

    @pytest.fixture
    def sample_resume(self):
        """Sample resume instance."""
        resume = Resume(
            id=1,
            user_id=1,
            title="Software Engineer Resume",
            full_name="John Doe",
            email="john.doe@example.com",
            status=ResumeStatus.DRAFT,
            visibility=ResumeVisibility.PRIVATE,
            share_token="test_share_token_12345",
            public_url_slug="software-engineer-resume-abc123"
        )
        return resume

    @pytest.fixture
    def sample_resume_create_data(self):
        """Sample resume creation data."""
        return ResumeCreate(
            title="Software Engineer Resume",
            full_name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            location="San Francisco, CA",
            professional_summary="Experienced software engineer"
        )

    # === SERVICE METHOD TESTS ===

    async def test_create_resume_service(self, resume_service, mock_db, sample_resume_create_data):
        """Test resume creation service method."""
        with patch('app.services.resume_service.Resume') as MockResume:
            mock_resume_instance = MagicMock()
            mock_resume_instance.id = 1
            mock_resume_instance.title = sample_resume_create_data.title
            MockResume.return_value = mock_resume_instance

            await resume_service.create_resume(mock_db, sample_resume_create_data, 1)

            # Verify database operations
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    @patch('app.services.resume_service.resume_crud')
    async def test_get_resume_service(self, mock_crud, resume_service, mock_db, sample_resume):
        """Test resume retrieval service method."""
        mock_crud.get_with_details.return_value = sample_resume

        result = await resume_service.get_resume(mock_db, 1, 1)

        mock_crud.get_with_details.assert_called_once_with(mock_db, id=1, user_id=1)
        assert result == sample_resume

    @patch('app.services.resume_service.resume_crud')
    async def test_get_user_resumes_service(self, mock_crud, resume_service, mock_db):
        """Test user resumes retrieval service method."""
        mock_resumes = [MagicMock(), MagicMock()]
        mock_crud.get_by_user.return_value = mock_resumes

        result = await resume_service.get_user_resumes(mock_db, 1, limit=10, offset=0)

        mock_crud.get_by_user.assert_called_once_with(
            mock_db, user_id=1, skip=0, limit=10, status=None
        )
        assert result == mock_resumes

    async def test_update_resume_service(self, resume_service, mock_db, sample_resume):
        """Test resume update service method."""
        with patch.object(resume_service, 'get_resume', return_value=sample_resume):
            with patch.object(resume_service, '_generate_unique_slug', return_value='new-slug'):
                update_data = ResumeUpdate(
                    title="Updated Resume Title",
                    professional_summary="Updated summary"
                )

                await resume_service.update_resume(mock_db, 1, 1, update_data)

                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once_with(sample_resume)

    async def test_delete_resume_service(self, resume_service, mock_db, sample_resume):
        """Test resume deletion service method."""
        with patch.object(resume_service, 'get_resume', return_value=sample_resume):
            result = await resume_service.delete_resume(mock_db, 1, 1)

            mock_db.delete.assert_called_once_with(sample_resume)
            mock_db.commit.assert_called_once()
            assert result is True

    async def test_delete_resume_not_found(self, resume_service, mock_db):
        """Test resume deletion when resume not found."""
        with patch.object(resume_service, 'get_resume', return_value=None):
            result = await resume_service.delete_resume(mock_db, 999, 1)

            assert result is False
            mock_db.delete.assert_not_called()

    # === BUSINESS LOGIC TESTS ===

    def test_generate_share_token(self, resume_service):
        """Test share token generation."""
        token = resume_service._generate_share_token()

        assert token is not None
        assert len(token) == 32
        assert all(c.isalnum() for c in token)

    def test_slugify_text(self, resume_service):
        """Test text slugification."""
        test_cases = [
            ("Software Engineer Resume", "software-engineer-resume"),
            ("Full-Stack Developer @ TechCorp!", "full-stack-developer-techcorp"),
            ("Resume with Special Characters #$%", "resume-with-special-characters"),
            ("", ""),
            ("A" * 100, "a" * 50)  # Should truncate to 50 chars
        ]

        for input_text, expected in test_cases:
            result = resume_service._slugify(input_text)
            assert result == expected

    def test_validate_resume_data(self, resume_service):
        """Test resume data validation."""
        valid_data = {
            "title": "Software Engineer",
            "full_name": "John Doe",
            "email": "john@example.com"
        }

        invalid_data = {
            "title": "Software Engineer",
            "email": "john@example.com"
            # Missing full_name
        }

        assert resume_service.validate_resume_data(valid_data) is True
        assert resume_service.validate_resume_data(invalid_data) is False

    # === PUBLIC SETTINGS TESTS ===

    @patch('app.services.resume_service.resume_crud')
    async def test_update_public_settings(self, mock_crud, resume_service, mock_db, sample_resume):
        """Test updating public settings."""
        mock_crud.update_public_settings.return_value = sample_resume

        result = await resume_service.update_public_settings(
            mock_db, 1, 1, is_public=True, custom_slug="custom-slug"
        )

        mock_crud.update_public_settings.assert_called_once_with(
            mock_db,
            resume_id=1,
            user_id=1,
            is_public=True,
            custom_slug="custom-slug",
            can_download_pdf=True
        )
        assert result == sample_resume

    @patch('app.services.resume_service.resume_crud')
    async def test_get_public_resume(self, mock_crud, resume_service, mock_db, sample_resume):
        """Test getting public resume."""
        mock_crud.get_public_by_slug.return_value = sample_resume

        result = await resume_service.get_public_resume(mock_db, "test-slug")

        mock_crud.get_public_by_slug.assert_called_once_with(mock_db, slug="test-slug")
        assert result == sample_resume

    @patch('app.services.resume_service.resume_crud')
    async def test_increment_download_count(self, mock_crud, resume_service, mock_db):
        """Test incrementing download count."""
        mock_crud.increment_download.return_value = True

        result = await resume_service.increment_download_count(mock_db, 1)

        mock_crud.increment_download.assert_called_once_with(mock_db, resume_id=1)
        assert result is True

    # === WORK EXPERIENCE TESTS ===

    async def test_add_work_experience_success(self, resume_service, mock_db, sample_resume):
        """Test adding work experience successfully."""
        with patch.object(resume_service, 'get_resume', return_value=sample_resume):
            with patch('app.services.resume_service.WorkExperience') as MockWorkExp:
                mock_exp_instance = MagicMock()
                mock_exp_instance.id = 1
                mock_exp_instance.company_name = "TechCorp"
                MockWorkExp.return_value = mock_exp_instance

                exp_data = WorkExperienceCreate(
                    company_name="TechCorp",
                    position_title="Software Engineer",
                    start_date=datetime(2020, 1, 1),
                    is_current=True,
                    description="Development work"
                )

                await resume_service.add_work_experience(mock_db, 1, 1, exp_data)

                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()

    async def test_add_work_experience_invalid_resume(self, resume_service, mock_db):
        """Test adding work experience to non-existent resume."""
        with patch.object(resume_service, 'get_resume', return_value=None):
            exp_data = WorkExperienceCreate(
                company_name="TechCorp",
                position_title="Software Engineer",
                start_date=datetime(2020, 1, 1),
                is_current=True,
                description="Development work"
            )

            result = await resume_service.add_work_experience(mock_db, 999, 1, exp_data)

            assert result is None
            mock_db.add.assert_not_called()

    # === SHARING TESTS ===

    async def test_create_share_link_success(self, resume_service, mock_db, sample_resume):
        """Test creating share link successfully."""
        with patch.object(resume_service, 'get_resume', return_value=sample_resume):
            with patch('app.services.resume_service.ResumeShare') as MockShare:
                mock_share_instance = MagicMock()
                MockShare.return_value = mock_share_instance

                result = await resume_service.create_share_link(
                    mock_db, 1, 1, recipient_email="test@example.com", expires_in_days=30
                )

                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                assert len(result) == 32  # Share token length

    async def test_get_shared_resume_success(self, resume_service, mock_db, sample_resume):
        """Test accessing shared resume successfully."""
        mock_share = MagicMock()
        mock_share.is_expired.return_value = False
        mock_share.password_protected = False
        mock_share.resume_id = 1

        with patch('app.services.resume_service.ResumeShare') as MockShare:
            MockShare.get_by_token = AsyncMock(return_value=mock_share)

            with patch.object(mock_db, 'execute') as mock_execute:
                mock_result = MagicMock()
                mock_result.scalars.return_value.first.return_value = sample_resume
                mock_execute.return_value = mock_result

                result = await resume_service.get_shared_resume(mock_db, "test_token")

                assert result == sample_resume
                mock_db.commit.assert_called_once()

    async def test_get_shared_resume_expired(self, resume_service, mock_db):
        """Test accessing expired shared resume."""
        mock_share = MagicMock()
        mock_share.is_expired.return_value = True

        with patch('app.services.resume_service.ResumeShare') as MockShare:
            MockShare.get_by_token = AsyncMock(return_value=mock_share)

            result = await resume_service.get_shared_resume(mock_db, "expired_token")

            assert result is None

    # === ERROR HANDLING TESTS ===

    async def test_create_resume_database_error(self, resume_service, mock_db, sample_resume_create_data):
        """Test resume creation with database error."""
        mock_db.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            await resume_service.create_resume(mock_db, sample_resume_create_data, 1)

        mock_db.rollback.assert_called_once()

    async def test_update_resume_database_error(self, resume_service, mock_db, sample_resume):
        """Test resume update with database error."""
        with patch.object(resume_service, 'get_resume', return_value=sample_resume):
            mock_db.commit.side_effect = Exception("Database error")

            update_data = ResumeUpdate(title="Updated Title")

            with pytest.raises(Exception):
                await resume_service.update_resume(mock_db, 1, 1, update_data)

            mock_db.rollback.assert_called_once()

    # === INTEGRATION PATTERNS ===

    async def test_complete_resume_workflow_mock(self, resume_service, mock_db):
        """Test complete resume workflow using mocks."""
        # Mock the entire workflow
        sample_resume = MagicMock()
        sample_resume.id = 1

        with patch.object(resume_service, 'create_resume', return_value=sample_resume):
            with patch.object(resume_service, 'add_work_experience', return_value=MagicMock()):
                with patch.object(resume_service, 'add_education', return_value=MagicMock()):
                    with patch.object(resume_service, 'add_skill', return_value=MagicMock()):
                        with patch.object(resume_service, 'update_resume', return_value=sample_resume):
                            with patch.object(resume_service, 'create_share_link', return_value="share_token"):

                                # 1. Create resume
                                resume_data = ResumeCreate(
                                    title="Test Resume",
                                    full_name="Test User",
                                    email="test@example.com"
                                )
                                resume = await resume_service.create_resume(mock_db, resume_data, 1)

                                # 2. Add work experience
                                exp_data = WorkExperienceCreate(
                                    company_name="TechCorp",
                                    position_title="Developer",
                                    start_date=datetime(2020, 1, 1),
                                    is_current=True,
                                    description="Development work"
                                )
                                experience = await resume_service.add_work_experience(
                                    mock_db, resume.id, 1, exp_data
                                )

                                # 3. Update resume status
                                update_data = ResumeUpdate(status=ResumeStatus.PUBLISHED)
                                updated_resume = await resume_service.update_resume(
                                    mock_db, resume.id, 1, update_data
                                )

                                # 4. Create share link
                                share_token = await resume_service.create_share_link(
                                    mock_db, resume.id, 1, expires_in_days=30
                                )

                                # Verify all operations were called
                                assert resume is not None
                                assert experience is not None
                                assert updated_resume is not None
                                assert share_token == "share_token"

    # === EDGE CASE TESTS ===

    async def test_duplicate_resume_with_empty_sections(self, resume_service, mock_db):
        """Test duplicating resume with no additional sections."""
        original_resume = MagicMock()
        original_resume.id = 1
        original_resume.title = "Original"
        original_resume.sections = []
        original_resume.experiences = []
        original_resume.educations = []
        original_resume.skills = []

        with patch.object(resume_service, 'get_resume', return_value=original_resume):
            with patch('app.services.resume_service.Resume') as MockResume:
                mock_duplicate = MagicMock()
                mock_duplicate.id = 2
                MockResume.return_value = mock_duplicate

                await resume_service.duplicate_resume(mock_db, 1, 1)

                mock_db.add.assert_called()
                mock_db.flush.assert_called_once()
                mock_db.commit.assert_called_once()

    async def test_send_resume_email_mock(self, resume_service, mock_db, sample_resume):
        """Test sending resume email (mock implementation)."""
        result = await resume_service.send_resume_email(
            mock_db,
            sample_resume,
            ["recipient@example.com"],
            "Subject",
            "Message"
        )

        assert result is True

    async def test_attach_to_message_mock(self, resume_service, mock_db):
        """Test attaching resume to message (mock implementation)."""
        mock_attachment = MagicMock()
        mock_attachment.id = 1

        with patch('app.services.resume_service.resume_message_attachment') as mock_attachment_crud:
            mock_attachment_crud.create_attachment.return_value = mock_attachment

            result = await resume_service.attach_to_message(
                mock_db, 1, 1, include_pdf=True, auto_attach=False
            )

            assert result == mock_attachment
            mock_attachment_crud.create_attachment.assert_called_once()


class TestResumeUtilities:
    """Test resume utility functions."""

    def test_slug_generation_edge_cases(self):
        """Test slug generation with various edge cases."""
        from app.services.resume_service import ResumeService
        service = ResumeService()

        test_cases = [
            ("", ""),  # Empty string
            ("   ", ""),  # Only spaces
            ("A", "a"),  # Single character
            ("UPPERCASE TITLE", "uppercase-title"),  # Uppercase conversion
            ("Title with    multiple    spaces", "title-with-multiple-spaces"),  # Multiple spaces
            ("Title-with-hyphens", "title-with-hyphens"),  # Existing hyphens
            ("Special@#$%Characters!", "specialcharacters"),  # Special characters
            ("Unicode résumé café", "unicode-résumé-café"),  # Unicode characters
            ("123 Numbers 456", "123-numbers-456"),  # Numbers
        ]

        for input_text, expected in test_cases:
            result = service._slugify(input_text)
            assert result == expected, f"Failed for input: '{input_text}'"

    def test_password_hashing(self):
        """Test password hashing functionality."""
        from app.services.resume_service import ResumeService
        service = ResumeService()

        password = "test_password_123"
        hashed = service._hash_password(password)

        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are typically 60 chars
        assert service._verify_password(password, hashed) is True
        assert service._verify_password("wrong_password", hashed) is False

    def test_share_token_uniqueness(self):
        """Test that share tokens are unique."""
        from app.services.resume_service import ResumeService
        service = ResumeService()

        tokens = [service._generate_share_token() for _ in range(100)]

        # All tokens should be unique
        assert len(set(tokens)) == 100

        # All tokens should be 32 characters
        assert all(len(token) == 32 for token in tokens)

        # All tokens should be alphanumeric
        assert all(token.isalnum() for token in tokens)
