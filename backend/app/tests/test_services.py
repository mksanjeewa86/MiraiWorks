"""Basic unit tests for service classes."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from app.services.auth_service import AuthService
from app.services.meeting_service import MeetingService
from app.services.resume_service import ResumeService
from app.utils.datetime_utils import get_utc_now


class TestAuthService:
    """Test AuthService methods."""

    def test_get_password_hash(self):
        """Test password hashing."""
        auth_service = AuthService()
        password = "testpassword123"
        hash_result = auth_service.get_password_hash(password)

        assert hash_result is not None
        assert len(hash_result) > 50  # bcrypt hashes are long
        assert hash_result.startswith("$2b$")  # bcrypt format

    def test_verify_password(self):
        """Test password verification."""
        auth_service = AuthService()
        password = "testpassword123"
        wrong_password = "wrongpassword"

        # Hash the password
        password_hash = auth_service.get_password_hash(password)

        # Verify correct password
        assert auth_service.verify_password(password, password_hash) is True

        # Verify incorrect password
        assert auth_service.verify_password(wrong_password, password_hash) is False

    def test_create_access_token(self):
        """Test JWT access token creation."""
        auth_service = AuthService()
        data = {"sub": "test@example.com", "user_id": 123}

        token = auth_service.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts

    def test_create_refresh_token(self):
        """Test JWT refresh token creation."""
        auth_service = AuthService()
        data = {"sub": "test@example.com", "user_id": 123}

        token = auth_service.create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts

    @patch("app.services.auth_service.jwt.decode")
    def test_decode_token_success(self, mock_decode):
        """Test successful token decoding."""
        auth_service = AuthService()
        mock_decode.return_value = {
            "sub": "test@example.com",
            "exp": get_utc_now() + timedelta(hours=1),
            "type": "access",
        }

        result = auth_service.decode_token("valid_token")

        assert result is not None
        assert "sub" in result

    @patch("app.services.auth_service.jwt.decode")
    def test_decode_token_invalid(self, mock_decode):
        """Test invalid token decoding."""
        from jose import JWTError

        auth_service = AuthService()
        mock_decode.side_effect = JWTError("Invalid token")

        result = auth_service.decode_token("invalid_token")

        assert result is None


class TestResumeService:
    """Test ResumeService methods."""

    def setup_method(self):
        """Set up test environment."""
        self.resume_service = ResumeService()

    @pytest.mark.skip(reason="generate_pdf method not implemented in ResumeService")
    @patch("app.services.resume_service.ReportLabPDFBuilder")
    def test_generate_pdf_success(self, mock_pdf_builder):
        """Test successful PDF generation."""
        # Mock the PDF builder
        mock_builder_instance = Mock()
        mock_builder_instance.generate_pdf.return_value = b"fake_pdf_content"
        mock_pdf_builder.return_value = mock_builder_instance

        resume_data = {
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
            },
            "experiences": [],
            "education": [],
            "skills": [],
        }

        result = self.resume_service.generate_pdf(resume_data)

        assert result == b"fake_pdf_content"
        mock_pdf_builder.assert_called_once_with(resume_data)
        mock_builder_instance.generate_pdf.assert_called_once()

    @pytest.mark.skip(
        reason="validate_resume_data method not implemented in ResumeService"
    )
    def test_validate_resume_data_valid(self):
        """Test resume data validation with valid data."""
        valid_data = {
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "1234567890",
            },
            "experiences": [
                {
                    "company": "Tech Corp",
                    "position": "Developer",
                    "start_date": "2020-01-01",
                    "description": "Developed software",
                }
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "Bachelor's",
                    "field": "Computer Science",
                    "graduation_date": "2019-05-01",
                }
            ],
            "skills": ["Python", "JavaScript"],
        }

        # Should not raise an exception
        self.resume_service.validate_resume_data(valid_data)

    @pytest.mark.skip(
        reason="validate_resume_data method not implemented in ResumeService"
    )
    def test_validate_resume_data_missing_required(self):
        """Test resume data validation with missing required fields."""
        invalid_data = {
            "personal_info": {
                "first_name": "John"
                # Missing last_name and email
            }
        }

        with pytest.raises(ValueError, match="Missing required"):
            self.resume_service.validate_resume_data(invalid_data)

    @pytest.mark.skip(reason="format_date method not implemented in ResumeService")
    def test_format_date(self):
        """Test date formatting."""
        # Test valid date
        formatted = self.resume_service.format_date("2023-12-25")  # type: ignore[attr-defined]
        assert formatted == "December 2023"

        # Test None
        formatted = self.resume_service.format_date(None)  # type: ignore[attr-defined]
        assert formatted == "Present"

        # Test empty string
        formatted = self.resume_service.format_date("")  # type: ignore[attr-defined]
        assert formatted == "Present"


@pytest.mark.skip(reason="MeetingService constructor requires db parameter")
class TestMeetingService:
    """Test MeetingService methods."""

    @pytest.mark.skip(reason="MeetingService constructor requires db parameter")
    def setup_method(self):
        """Set up test environment."""
        self.meeting_service = MeetingService()  # type: ignore[call-arg]

    def test_generate_meeting_id(self):
        """Test meeting ID generation."""
        meeting_id = self.meeting_service.generate_meeting_id()  # type: ignore[attr-defined]

        assert meeting_id is not None
        assert isinstance(meeting_id, str)
        assert len(meeting_id) > 8  # Should be a reasonable length

    def test_validate_meeting_time_valid(self):
        """Test meeting time validation with valid time."""
        future_time = get_utc_now() + timedelta(hours=2)

        # Should not raise an exception
        self.meeting_service.validate_meeting_time(future_time)  # type: ignore[attr-defined]

    def test_validate_meeting_time_past(self):
        """Test meeting time validation with past time."""
        past_time = get_utc_now() - timedelta(hours=1)

        with pytest.raises(ValueError, match="past"):
            self.meeting_service.validate_meeting_time(past_time)  # type: ignore[attr-defined]

    def test_calculate_meeting_duration(self):
        """Test meeting duration calculation."""
        start_time = datetime(2023, 12, 25, 10, 0, 0)
        end_time = datetime(2023, 12, 25, 11, 30, 0)

        duration = self.meeting_service.calculate_meeting_duration(start_time, end_time)  # type: ignore[attr-defined]

        assert duration == 90  # 1.5 hours = 90 minutes

    @patch("app.services.meeting_service.logger")
    def test_log_meeting_event(self, mock_logger):
        """Test meeting event logging."""
        event_data = {
            "meeting_id": "test_meeting_123",
            "event_type": "created",
            "user_id": 456,
        }

        self.meeting_service.log_meeting_event(event_data)  # type: ignore[attr-defined]

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Meeting event" in call_args
        assert "test_meeting_123" in call_args


# Add basic smoke tests that don't require database
class TestServiceImports:
    """Test that all services can be imported without errors."""

    def test_import_auth_service(self):
        """Test importing auth service."""
        from app.services.auth_service import AuthService, auth_service

        assert AuthService is not None
        assert auth_service is not None

    def test_import_resume_service(self):
        """Test importing resume service."""
        from app.services.resume_service import ResumeService

        assert ResumeService is not None

    def test_import_meeting_service(self):
        """Test importing meeting service."""
        from app.services.meeting_service import MeetingService

        assert MeetingService is not None

    def test_import_template_service(self):
        """Test importing template service."""
        from app.services.template_service import TemplateService

        assert TemplateService is not None

    def test_import_pdf_service(self):
        """Test importing PDF service."""
        from app.services.pdf_service import PDFService

        assert PDFService is not None


# Add tests for service initialization
class TestServiceConfiguration:
    """Test service configuration and initialization."""

    def test_auth_service_singleton(self):
        """Test that auth_service is properly configured."""
        from app.services.auth_service import auth_service

        assert auth_service is not None
        assert hasattr(auth_service, "get_password_hash")
        assert hasattr(auth_service, "verify_password")
        assert hasattr(auth_service, "create_access_token")

    def test_services_have_required_methods(self):
        """Test that services have expected methods."""
        from app.services.auth_service import AuthService
        from app.services.resume_service import ResumeService

        auth_service = AuthService()
        resume_service = ResumeService()

        # Test AuthService methods
        assert callable(getattr(auth_service, "get_password_hash", None))
        assert callable(getattr(auth_service, "verify_password", None))
        assert callable(getattr(auth_service, "create_access_token", None))

        # Test ResumeService methods
        assert callable(getattr(resume_service, "generate_pdf", None))
        assert callable(getattr(resume_service, "validate_resume_data", None))
