import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_settings import UserSettings


class TestUserSettings:
    """Comprehensive tests for user settings functionality."""

    @pytest.mark.asyncio
    async def test_get_user_settings_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test successful retrieval of user settings."""
        # Create user settings
        user_settings = UserSettings(
            user_id=test_user.id,
            job_title="Software Engineer",
            bio="Test bio",
            avatar_url="https://test.com/avatar.jpg",
            email_notifications=True,
            push_notifications=False,
            sms_notifications=False,
            interview_reminders=True,
            application_updates=True,
            message_notifications=True,
            language="en",
            timezone="America/New_York",
            date_format="MM/DD/YYYY"
        )
        db_session.add(user_settings)
        await db_session.commit()

        response = await client.get(
            "/api/user/settings",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify profile settings
        assert data["job_title"] == "Software Engineer"
        assert data["bio"] == "Test bio"
        assert data["avatar_url"] == "https://test.com/avatar.jpg"

        # Verify notification preferences
        assert data["email_notifications"] is True
        assert data["push_notifications"] is False
        assert data["sms_notifications"] is False
        assert data["interview_reminders"] is True
        assert data["application_updates"] is True
        assert data["message_notifications"] is True

        # Verify UI preferences
        assert data["language"] == "en"
        assert data["timezone"] == "America/New_York"
        assert data["date_format"] == "MM/DD/YYYY"

        # Verify security settings
        assert data["require_2fa"] is False

    @pytest.mark.asyncio
    async def test_get_user_settings_default_values(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test user settings with default values when no settings exist."""
        response = await client.get(
            "/api/user/settings",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify default values
        assert data["job_title"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None
        assert data["email_notifications"] is True
        assert data["push_notifications"] is True
        assert data["sms_notifications"] is False
        assert data["interview_reminders"] is True
        assert data["application_updates"] is True
        assert data["message_notifications"] is True
        assert data["language"] == "en"
        assert data["timezone"] == "America/New_York"
        assert data["date_format"] == "MM/DD/YYYY"
        assert data["require_2fa"] is False

    @pytest.mark.asyncio
    async def test_get_user_settings_unauthorized(self, client: AsyncClient):
        """Test user settings access without authentication fails."""
        response = await client.get("/api/user/settings")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_update_user_settings_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test successful update of user settings."""
        update_data = {
            "job_title": "Senior Software Engineer",
            "bio": "Updated bio",
            "avatar_url": "https://test.com/new-avatar.jpg",
            "email_notifications": False,
            "push_notifications": True,
            "interview_reminders": False,
            "language": "es",
            "timezone": "Europe/Madrid",
            "date_format": "DD/MM/YYYY",
            "require_2fa": True
        }

        response = await client.put(
            "/api/user/settings",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify updated values
        assert data["job_title"] == "Senior Software Engineer"
        assert data["bio"] == "Updated bio"
        assert data["avatar_url"] == "https://test.com/new-avatar.jpg"
        assert data["email_notifications"] is False
        assert data["push_notifications"] is True
        assert data["interview_reminders"] is False
        assert data["language"] == "es"
        assert data["timezone"] == "Europe/Madrid"
        assert data["date_format"] == "DD/MM/YYYY"
        assert data["require_2fa"] is True

    @pytest.mark.asyncio
    async def test_update_user_settings_partial(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test partial update of user settings."""
        # Only update some fields
        update_data = {
            "job_title": "Updated Title",
            "email_notifications": False
        }

        response = await client.put(
            "/api/user/settings",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify updated fields
        assert data["job_title"] == "Updated Title"
        assert data["email_notifications"] is False

        # Verify other fields remain default
        assert data["bio"] is None
        assert data["push_notifications"] is True  # Default value

    @pytest.mark.asyncio
    async def test_update_user_settings_sms_without_phone(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test SMS notifications enable fails without phone number."""
        update_data = {
            "sms_notifications": True
        }

        response = await client.put(
            "/api/user/settings",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "SMS notifications require a phone number" in error_detail

    @pytest.mark.asyncio
    async def test_update_user_settings_sms_with_phone(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test SMS notifications enable succeeds with phone number."""
        # Add phone number to user
        test_user.phone = "+1234567890"
        await db_session.commit()

        update_data = {
            "sms_notifications": True
        }

        response = await client.put(
            "/api/user/settings",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sms_notifications"] is True

    @pytest.mark.asyncio
    async def test_update_user_settings_unauthorized(self, client: AsyncClient):
        """Test user settings update without authentication fails."""
        update_data = {
            "job_title": "Test Title"
        }

        response = await client.put(
            "/api/user/settings",
            json=update_data
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_user_profile_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test successful retrieval of user profile."""
        # Create user settings
        user_settings = UserSettings(
            user_id=test_user.id,
            job_title="Software Engineer",
            bio="Test bio",
            avatar_url="https://test.com/avatar.jpg"
        )
        db_session.add(user_settings)
        await db_session.commit()

        response = await client.get(
            "/api/user/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify profile data
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert data["full_name"] == test_user.full_name
        assert data["job_title"] == "Software Engineer"
        assert data["bio"] == "Test bio"
        assert data["avatar_url"] == "https://test.com/avatar.jpg"

    @pytest.mark.asyncio
    async def test_get_user_profile_without_settings(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test user profile retrieval without existing settings."""
        response = await client.get(
            "/api/user/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify basic profile data
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert data["full_name"] == test_user.full_name

        # Settings-related fields should be None
        assert data["job_title"] is None
        assert data["bio"] is None
        assert data["avatar_url"] is None

    @pytest.mark.asyncio
    async def test_get_user_profile_unauthorized(self, client: AsyncClient):
        """Test user profile access without authentication fails."""
        response = await client.get("/api/user/profile")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_update_user_profile_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test successful update of user profile."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1234567890",
            "job_title": "Senior Engineer",
            "bio": "Updated bio",
            "avatar_url": "https://test.com/new-avatar.jpg"
        }

        response = await client.put(
            "/api/user/profile",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify updated values
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+1234567890"
        assert data["job_title"] == "Senior Engineer"
        assert data["bio"] == "Updated bio"
        assert data["avatar_url"] == "https://test.com/new-avatar.jpg"
        assert data["full_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_user_profile_partial(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test partial update of user profile."""
        # Only update some fields
        update_data = {
            "first_name": "NewFirst",
            "job_title": "New Title"
        }

        response = await client.put(
            "/api/user/profile",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify updated fields
        assert data["first_name"] == "NewFirst"
        assert data["job_title"] == "New Title"

        # Verify other fields remain unchanged
        assert data["last_name"] == test_user.last_name
        assert data["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_update_user_profile_unauthorized(self, client: AsyncClient):
        """Test user profile update without authentication fails."""
        update_data = {
            "first_name": "Test"
        }

        response = await client.put(
            "/api/user/profile",
            json=update_data
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_settings_sms_disabled_without_phone(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test SMS notifications are automatically disabled when user has no phone."""
        # Create settings with SMS enabled but user has no phone
        user_settings = UserSettings(
            user_id=test_user.id,
            sms_notifications=True  # This should be overridden
        )
        db_session.add(user_settings)
        await db_session.commit()

        # Ensure user has no phone
        test_user.phone = None
        await db_session.commit()

        response = await client.get(
            "/api/user/settings",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # SMS notifications should be false despite database value
        assert data["sms_notifications"] is False

    @pytest.mark.asyncio
    async def test_settings_sms_disabled_with_empty_phone(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test SMS notifications are disabled when user has empty phone."""
        # Create settings with SMS enabled but user has empty phone
        user_settings = UserSettings(
            user_id=test_user.id,
            sms_notifications=True
        )
        db_session.add(user_settings)
        await db_session.commit()

        # Set empty phone
        test_user.phone = "   "  # Whitespace only
        await db_session.commit()

        response = await client.get(
            "/api/user/settings",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # SMS notifications should be false
        assert data["sms_notifications"] is False

    @pytest.mark.asyncio
    async def test_timezone_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test various timezone settings."""
        timezones = [
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "UTC"
        ]

        for timezone in timezones:
            update_data = {
                "timezone": timezone
            }

            response = await client.put(
                "/api/user/settings",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["timezone"] == timezone

    @pytest.mark.asyncio
    async def test_language_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test various language settings."""
        languages = ["en", "es", "fr", "de", "ja"]

        for language in languages:
            update_data = {
                "language": language
            }

            response = await client.put(
                "/api/user/settings",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["language"] == language

    @pytest.mark.asyncio
    async def test_date_format_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test various date format settings."""
        date_formats = ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"]

        for date_format in date_formats:
            update_data = {
                "date_format": date_format
            }

            response = await client.put(
                "/api/user/settings",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["date_format"] == date_format

    @pytest.mark.asyncio
    async def test_boolean_settings_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test boolean settings validation."""
        boolean_fields = [
            "email_notifications",
            "push_notifications",
            "interview_reminders",
            "application_updates",
            "message_notifications",
            "require_2fa"
        ]

        for field in boolean_fields:
            # Test True
            update_data = {field: True}
            response = await client.put(
                "/api/user/settings",
                json=update_data,
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data[field] is True

            # Test False
            update_data = {field: False}
            response = await client.put(
                "/api/user/settings",
                json=update_data,
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data[field] is False

    @pytest.mark.asyncio
    async def test_profile_phone_number_formats(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test various phone number formats in profile."""
        phone_numbers = [
            "+1234567890",
            "+1 (234) 567-8900",
            "234-567-8900",
            "2345678900"
        ]

        for phone in phone_numbers:
            update_data = {
                "phone": phone
            }

            response = await client.put(
                "/api/user/profile",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["phone"] == phone

    @pytest.mark.asyncio
    async def test_profile_fields_separation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that profile update correctly separates user and settings fields."""
        update_data = {
            "first_name": "NewFirst",  # User field
            "last_name": "NewLast",    # User field
            "phone": "+1234567890",    # User field
            "job_title": "New Title",  # Settings field
            "bio": "New bio",          # Settings field
            "avatar_url": "https://test.com/avatar.jpg"  # Settings field
        }

        response = await client.put(
            "/api/user/profile",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all fields are updated correctly
        assert data["first_name"] == "NewFirst"
        assert data["last_name"] == "NewLast"
        assert data["phone"] == "+1234567890"
        assert data["job_title"] == "New Title"
        assert data["bio"] == "New bio"
        assert data["avatar_url"] == "https://test.com/avatar.jpg"