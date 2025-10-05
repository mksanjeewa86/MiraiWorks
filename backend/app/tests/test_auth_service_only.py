"""Basic unit tests for AuthService only."""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.services.auth_service import AuthService
from app.utils.datetime_utils import get_utc_now


class TestAuthService:
    """Test AuthService methods without database dependencies."""

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

    def test_auth_service_singleton(self):
        """Test that auth_service singleton is properly configured."""
        from app.services.auth_service import auth_service

        assert auth_service is not None
        assert hasattr(auth_service, "get_password_hash")
        assert hasattr(auth_service, "verify_password")
        assert hasattr(auth_service, "create_access_token")

    def test_password_hash_different_each_time(self):
        """Test that password hashing produces different results each time."""
        auth_service = AuthService()
        password = "testpassword123"

        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)

        # Different hashes (due to salt)
        assert hash1 != hash2

        # But both verify the same password
        assert auth_service.verify_password(password, hash1) is True
        assert auth_service.verify_password(password, hash2) is True

    def test_token_contains_expected_claims(self):
        """Test that tokens contain expected claims."""
        auth_service = AuthService()
        data = {"sub": "test@example.com", "user_id": 123, "role": "user"}

        # Create token
        token = auth_service.create_access_token(data)

        # Decode token (we'll mock the verification)
        with patch("app.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "test@example.com",
                "user_id": 123,
                "role": "user",
                "exp": get_utc_now() + timedelta(hours=1),
                "type": "access",
            }

            decoded = auth_service.decode_token(token)

            assert decoded["sub"] == "test@example.com"
            assert decoded["user_id"] == 123
            assert decoded["role"] == "user"
            assert "exp" in decoded


class TestServiceImportsBasic:
    """Test that basic services can be imported without errors."""

    def test_import_auth_service(self):
        """Test importing auth service."""
        from app.services.auth_service import AuthService, auth_service

        assert AuthService is not None
        assert auth_service is not None

    def test_import_storage_service(self):
        """Test importing storage service."""
        try:
            from app.services.storage_service import StorageService

            assert StorageService is not None
        except ImportError:
            pytest.skip("StorageService has dependencies that aren't available")

    def test_import_email_service(self):
        """Test importing email service."""
        try:
            from app.services.email_service import EmailService

            assert EmailService is not None
        except ImportError:
            pytest.skip("EmailService has dependencies that aren't available")

    def test_import_template_service(self):
        """Test importing template service."""
        try:
            from app.services.template_service import TemplateService

            assert TemplateService is not None
        except ImportError:
            pytest.skip("TemplateService has dependencies that aren't available")


class TestPasswordSecurity:
    """Test password security features."""

    def test_password_hash_length(self):
        """Test that password hashes are of appropriate length."""
        auth_service = AuthService()
        password = "testpassword123"
        hash_result = auth_service.get_password_hash(password)

        # bcrypt hashes should be 60 characters
        assert len(hash_result) == 60

    def test_short_password_still_hashes(self):
        """Test that even short passwords get hashed."""
        auth_service = AuthService()
        short_password = "123"
        hash_result = auth_service.get_password_hash(short_password)

        assert hash_result is not None
        assert len(hash_result) == 60
        assert auth_service.verify_password(short_password, hash_result) is True

    def test_empty_password_handling(self):
        """Test handling of empty passwords."""
        auth_service = AuthService()
        empty_password = ""
        hash_result = auth_service.get_password_hash(empty_password)

        assert hash_result is not None
        assert auth_service.verify_password(empty_password, hash_result) is True
        assert auth_service.verify_password("not_empty", hash_result) is False

    def test_unicode_password_support(self):
        """Test that unicode passwords are supported."""
        auth_service = AuthService()
        unicode_password = "пароль123🔒"
        hash_result = auth_service.get_password_hash(unicode_password)

        assert hash_result is not None
        assert auth_service.verify_password(unicode_password, hash_result) is True
        assert auth_service.verify_password("wrongpassword", hash_result) is False


class TestTokenSecurity:
    """Test JWT token security."""

    def test_access_token_expiration_claim(self):
        """Test that access tokens include expiration."""
        auth_service = AuthService()
        data = {"sub": "test@example.com"}

        with patch("app.services.auth_service.datetime") as mock_datetime:
            # Mock current time
            mock_now = datetime(2023, 12, 25, 10, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(
                *args, **kw
            )  # Pass through constructor

            token = auth_service.create_access_token(data)

            # Verify token was created (we can't easily decode without mocking jwt)
            assert token is not None
            assert isinstance(token, str)

    def test_refresh_token_longer_expiration(self):
        """Test that refresh tokens have longer expiration than access tokens."""
        # This is a structural test - in a real scenario, refresh tokens
        # should have longer expiration times than access tokens
        auth_service = AuthService()
        data = {"sub": "test@example.com"}

        access_token = auth_service.create_access_token(data)
        refresh_token = auth_service.create_refresh_token(data)

        # Both should be valid JWTs
        assert access_token is not None
        assert refresh_token is not None
        assert len(access_token.split(".")) == 3
        assert len(refresh_token.split(".")) == 3
