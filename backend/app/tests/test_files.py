import io
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestFiles:
    """Comprehensive tests for file management functionality."""

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    async def test_upload_file_success(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Test successful file upload."""
        # Create test file first to get correct size
        file_content = b"Test file content"

        # Don't mock storage service - let it use the actual local storage for this test
        # This will test the real upload flow

        # Create test file data
        file_data = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        response = await client.post(
            "/api/files/upload", files=file_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "file_url" in data
        assert "file_name" in data
        assert "file_size" in data
        assert "file_type" in data
        assert "s3_key" in data
        assert "success" in data

        # Verify response values
        assert data["file_name"] == "test.txt"
        assert data["file_size"] == len(file_content)
        assert data["file_type"] == "text/plain"
        assert data["success"] is True
        # Verify that the s3_key contains the expected pattern with UUID
        assert "message-attachments" in data["s3_key"]
        assert "test.txt" in data["s3_key"]
        # Verify UUID pattern is present (UUID format: 8-4-4-4-12 characters)
        import re

        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        assert re.search(
            uuid_pattern, data["s3_key"]
        ), f"UUID pattern not found in {data['s3_key']}"

    @pytest.mark.asyncio
    async def test_upload_file_unauthorized(self, client: AsyncClient):
        """Test file upload without authentication fails."""
        file_data = {"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}

        response = await client.post("/api/files/upload", files=file_data)

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_upload_file_no_filename(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test file upload without filename fails."""
        file_data = {"file": ("", io.BytesIO(b"content"), "text/plain")}

        response = await client.post(
            "/api/files/upload", files=file_data, headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        # Check for Pydantic validation error about UploadFile
        assert any("UploadFile" in str(error) for error in error_detail)

    @pytest.mark.asyncio
    async def test_upload_file_invalid_extension(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test file upload with invalid extension fails."""
        file_data = {"file": ("test.exe", io.BytesIO(b"content"), "application/exe")}

        response = await client.post(
            "/api/files/upload", files=file_data, headers=auth_headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "File type not allowed" in error_detail

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, client: AsyncClient, auth_headers: dict):
        """Test file upload with file size exceeding limit fails."""
        # Create a file larger than 10MB (MAX_FILE_SIZE)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file_data = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}

        response = await client.post(
            "/api/files/upload", files=file_data, headers=auth_headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "File too large" in error_detail

    @pytest.mark.asyncio
    async def test_upload_file_valid_extensions(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test file upload with various valid extensions."""
        valid_extensions = [
            ("test.txt", "text/plain"),
            ("test.pdf", "application/pdf"),
            ("test.png", "image/png"),
            ("test.jpg", "image/jpeg"),
            (
                "test.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        ]

        with patch(
            "app.services.storage_service.get_storage_service"
        ) as mock_get_storage_service:
            mock_storage = Mock()
            mock_storage.upload_file_data = AsyncMock(
                return_value=("test_key", "test_hash", 1024)
            )
            mock_storage.get_presigned_url = Mock(
                return_value="https://test.com/download/test"
            )
            mock_get_storage_service.return_value = mock_storage

            for filename, content_type in valid_extensions:
                file_data = {"file": (filename, io.BytesIO(b"content"), content_type)}

                response = await client.post(
                    "/api/files/upload", files=file_data, headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert data["file_name"] == filename
                assert data["success"] is True

    @pytest.mark.asyncio
    @patch("app.services.local_storage_service.get_local_storage_service")
    async def test_upload_file_storage_error(
        self, mock_get_local_storage_service, client: AsyncClient, auth_headers: dict
    ):
        """Test file upload with storage service error."""
        # Mock local storage service to raise exception
        mock_storage = Mock()
        mock_storage.upload_file_data = AsyncMock(
            side_effect=Exception("Storage error")
        )
        mock_get_local_storage_service.return_value = mock_storage

        file_data = {"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}

        response = await client.post(
            "/api/files/upload", files=file_data, headers=auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Error saving file" in error_detail

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    @patch("app.endpoints.files.check_file_access_permission")
    async def test_download_file_success(
        self,
        mock_check_permission,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test successful file download URL generation."""
        # Mock permission check to return True
        mock_check_permission.return_value = True

        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.get_presigned_url = Mock(
            return_value="https://test.com/download/test_key"
        )
        mock_get_storage_service.return_value = mock_storage

        test_s3_key = "attachments/1/2024/01/uuid_test.txt"

        response = await client.get(
            f"/api/files/download/{test_s3_key}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "download_url" in data
        assert "s3_key" in data
        assert "expires_in" in data

        # Verify response values
        assert data["download_url"] == "https://test.com/download/test_key"
        assert data["s3_key"] == test_s3_key
        assert data["expires_in"] == "1 hour"

        # Verify storage service was called correctly
        mock_storage.file_exists.assert_called_once_with(test_s3_key)
        mock_storage.get_presigned_url.assert_called_once_with(test_s3_key)

    @pytest.mark.asyncio
    async def test_download_file_unauthorized(self, client: AsyncClient):
        """Test file download without authentication fails."""
        response = await client.get("/api/files/download/test_key")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    @patch("app.endpoints.files.check_file_access_permission")
    async def test_download_file_not_found(
        self,
        mock_check_permission,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test file download with non-existent file fails."""
        # Mock permission check to return True (user has permission but file doesn't exist)
        mock_check_permission.return_value = True

        # Mock storage service to return file not found
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=False)
        mock_get_storage_service.return_value = mock_storage

        response = await client.get(
            "/api/files/download/nonexistent_key", headers=auth_headers
        )

        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "File not found" in error_detail

    @pytest.mark.asyncio
    @patch("app.services.local_storage_service.get_local_storage_service")
    @patch("app.services.storage_service.get_storage_service")
    @patch("app.endpoints.files.check_file_access_permission")
    async def test_download_file_storage_error(
        self,
        mock_check_permission,
        mock_get_storage_service,
        mock_get_local_storage_service,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test file download with storage service error."""
        # Mock permission check to return True
        mock_check_permission.return_value = True

        # Mock MinIO storage service to raise exception
        mock_storage = Mock()
        mock_storage.file_exists = Mock(side_effect=Exception("Storage error"))
        mock_get_storage_service.return_value = mock_storage

        # Mock local storage service to also raise exception
        mock_local_storage = Mock()
        mock_local_storage.file_exists = Mock(
            side_effect=Exception("Local storage error")
        )
        mock_get_local_storage_service.return_value = mock_local_storage

        response = await client.get(
            "/api/files/download/test_key", headers=auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Error downloading file" in error_detail

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    async def test_delete_file_success(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        super_admin_auth_headers: dict,
    ):
        """Test successful file deletion."""
        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.delete_file = Mock(return_value=True)
        mock_get_storage_service.return_value = mock_storage

        test_s3_key = "attachments/1/2024/01/uuid_test.txt"

        response = await client.delete(
            f"/api/files/{test_s3_key}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "File deleted successfully"

        # Verify storage service was called correctly
        mock_storage.file_exists.assert_called_once_with(test_s3_key)
        mock_storage.delete_file.assert_called_once_with(test_s3_key)

    @pytest.mark.asyncio
    async def test_delete_file_unauthorized(self, client: AsyncClient):
        """Test file deletion without authentication fails."""
        response = await client.delete("/api/files/test_key")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    async def test_delete_file_not_found(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        super_admin_auth_headers: dict,
    ):
        """Test file deletion with non-existent file fails."""
        # Mock storage service to return file not found
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=False)
        mock_get_storage_service.return_value = mock_storage

        response = await client.delete(
            "/api/files/nonexistent_key", headers=super_admin_auth_headers
        )

        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "File not found" in error_detail

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    async def test_delete_file_deletion_failed(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        super_admin_auth_headers: dict,
    ):
        """Test file deletion when storage service deletion fails."""
        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.delete_file = Mock(return_value=False)  # Deletion failed
        mock_get_storage_service.return_value = mock_storage

        response = await client.delete(
            "/api/files/test_key", headers=super_admin_auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Failed to delete file" in error_detail

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    async def test_delete_file_storage_error(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        super_admin_auth_headers: dict,
    ):
        """Test file deletion with storage service error."""
        # Mock storage service to raise exception
        mock_storage = Mock()
        mock_storage.file_exists = Mock(side_effect=Exception("Storage error"))
        mock_get_storage_service.return_value = mock_storage

        response = await client.delete(
            "/api/files/test_key", headers=super_admin_auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Error deleting file" in error_detail

    @pytest.mark.asyncio
    async def test_file_extension_validation(self):
        """Test file extension validation function."""
        from app.endpoints.files import is_allowed_file

        # Test valid extensions
        valid_files = [
            "document.pdf",
            "image.png",
            "image.jpg",
            "image.jpeg",
            "document.doc",
            "document.docx",
            "spreadsheet.xls",
            "spreadsheet.xlsx",
            "presentation.ppt",
            "presentation.pptx",
            "text.txt",
            "archive.zip",
            "archive.rar",
            "archive.7z",
            "image.gif",
        ]

        for filename in valid_files:
            assert is_allowed_file(filename), f"File {filename} should be allowed"

        # Test invalid extensions
        invalid_files = [
            "executable.exe",
            "script.sh",
            "binary.bin",
            "no_extension",
            ".hidden",
            "file.invalid",
        ]

        for filename in invalid_files:
            assert not is_allowed_file(
                filename
            ), f"File {filename} should not be allowed"

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    async def test_upload_with_special_characters_in_filename(
        self, mock_get_storage_service, client: AsyncClient, auth_headers: dict
    ):
        """Test file upload with special characters in filename."""
        # Mock storage service
        mock_storage = Mock()
        mock_storage.upload_file_data = AsyncMock(
            return_value=("test_key", "test_hash", 1024)
        )
        mock_storage.get_presigned_url = Mock(
            return_value="https://test.com/download/test"
        )
        mock_get_storage_service.return_value = mock_storage

        # Test filename with special characters
        special_filename = "test file (copy) [2024].txt"
        file_data = {"file": (special_filename, io.BytesIO(b"content"), "text/plain")}

        response = await client.post(
            "/api/files/upload", files=file_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == special_filename
        assert data["success"] is True

    @pytest.mark.asyncio
    @patch("app.services.storage_service.get_storage_service")
    @patch("app.endpoints.files.check_file_access_permission")
    async def test_download_with_nested_path(
        self,
        mock_check_permission,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test file download with nested S3 key path."""
        # Mock permission check to return True
        mock_check_permission.return_value = True

        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.get_presigned_url = Mock(
            return_value="https://test.com/download/nested/path"
        )
        mock_get_storage_service.return_value = mock_storage

        # Test nested path
        nested_s3_key = "attachments/user/123/2024/01/uuid_test.txt"

        response = await client.get(
            f"/api/files/download/{nested_s3_key}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["s3_key"] == nested_s3_key

    @pytest.mark.asyncio
    async def test_file_size_limits(self):
        """Test file size constants."""
        from app.endpoints.files import MAX_FILE_SIZE

        # Verify the file size limit is reasonable
        assert 10 * 1024 * 1024 == MAX_FILE_SIZE  # 10MB
        assert 0 < MAX_FILE_SIZE

    @pytest.mark.asyncio
    async def test_allowed_extensions_coverage(self):
        """Test that all expected file extensions are allowed."""
        from app.endpoints.files import ALLOWED_EXTENSIONS

        expected_extensions = {
            "txt",
            "pdf",
            "png",
            "jpg",
            "jpeg",
            "gif",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "zip",
            "rar",
            "7z",
        }

        # Verify all expected extensions are present
        for ext in expected_extensions:
            assert ext in ALLOWED_EXTENSIONS, f"Extension {ext} should be allowed"

        # Verify extensions are lowercase
        for ext in ALLOWED_EXTENSIONS:
            assert ext.islower(), f"Extension {ext} should be lowercase"

    @pytest.mark.asyncio
    async def test_file_download_permission_sender_access(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_admin_user: User,
    ):
        """Test that message sender can download their uploaded file."""
        from pathlib import Path

        from app.schemas.message import MessageCreate
        from app.services.message_service import message_service

        sender = test_user
        recipient = test_admin_user

        # Create auth headers for sender
        sender_token = self._create_test_token(sender.id)
        sender_headers = {"Authorization": f"Bearer {sender_token}"}

        # Create a message with file attachment
        file_url = "/api/files/download/message-attachments/1/2024/test-file.txt"
        message_data = MessageCreate(
            recipient_id=recipient.id,
            content="📎 test-file.txt",
            type="file",
            file_url=file_url,
            file_name="test-file.txt",
            file_size=1024,
            file_type="text/plain",
        )

        # Send the message
        await message_service.send_message(db_session, sender.id, message_data)

        # Test that sender can download the file
        with patch(
            "app.services.storage_service.get_storage_service"
        ) as mock_storage_service, patch(
            "app.services.local_storage_service.get_local_storage_service"
        ) as mock_local_storage:
            # Mock MinIO storage service to fail (no connection)
            mock_minio = Mock()
            mock_minio.file_exists = Mock(side_effect=Exception("MinIO not available"))
            mock_storage_service.return_value = mock_minio

            # Mock local storage service with proper base_path
            mock_storage = Mock()
            mock_storage.base_path = Path("/tmp/uploads")  # Proper path object
            mock_storage.file_exists = Mock(
                return_value=False
            )  # File doesn't exist locally
            mock_local_storage.return_value = mock_storage

            # Since file doesn't exist, it should return 404
            response = await client.get(
                "/api/files/download/message-attachments/1/2024/test-file.txt",
                headers=sender_headers,
            )

            # Permission check passes (user has access), but file doesn't exist on disk
            # This confirms the permission system is working correctly
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_file_download_permission_check(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_admin_user: User,
    ):
        """Test file download permission system works correctly."""
        from pathlib import Path

        from app.schemas.message import MessageCreate
        from app.services.message_service import message_service

        sender = test_user
        recipient = test_admin_user

        # Create auth headers for recipient (should be able to download)
        recipient_token = self._create_test_token(recipient.id)
        recipient_headers = {"Authorization": f"Bearer {recipient_token}"}

        # Create a message with file attachment
        file_url = "/api/files/download/message-attachments/1/2024/test-file.txt"
        message_data = MessageCreate(
            recipient_id=recipient.id,
            content="📎 test-file.txt",
            type="file",
            file_url=file_url,
            file_name="test-file.txt",
            file_size=1024,
            file_type="text/plain",
        )

        # Send the message
        await message_service.send_message(db_session, sender.id, message_data)

        # Test that recipient can download the file
        with patch(
            "app.services.storage_service.get_storage_service"
        ) as mock_storage_service, patch(
            "app.services.local_storage_service.get_local_storage_service"
        ) as mock_local_storage:
            # Mock MinIO storage service to fail (no connection)
            mock_minio = Mock()
            mock_minio.file_exists = Mock(side_effect=Exception("MinIO not available"))
            mock_storage_service.return_value = mock_minio

            # Mock local storage service with proper base_path
            mock_storage = Mock()
            mock_storage.base_path = Path("/tmp/uploads")  # Proper path object
            mock_storage.file_exists = Mock(
                return_value=False
            )  # File doesn't exist locally
            mock_local_storage.return_value = mock_storage

            # Since file doesn't exist, it should return 404
            response = await client.get(
                "/api/files/download/message-attachments/1/2024/test-file.txt",
                headers=recipient_headers,
            )

            # Permission check passes (user has access), but file doesn't exist on disk
            # This confirms the permission system is working correctly
            assert response.status_code == 404

    def _create_test_token(self, user_id: int) -> str:
        """Helper method to create test JWT token."""
        from app.services.auth_service import auth_service

        return auth_service.create_access_token(data={"sub": str(user_id)})

    @pytest.mark.asyncio
    async def test_file_download_permission_between_different_users(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_admin_user: User,
    ):
        """Test file download permissions work correctly between different users."""
        from pathlib import Path

        from app.schemas.message import MessageCreate
        from app.services.message_service import message_service

        # Use token-based auth instead of login to avoid 2FA issues
        sender_token = self._create_test_token(test_user.id)
        sender_headers = {"Authorization": f"Bearer {sender_token}"}

        recipient_token = self._create_test_token(test_admin_user.id)
        recipient_headers = {"Authorization": f"Bearer {recipient_token}"}

        # Create a message with file attachment (simulating file upload + message)
        file_url = "/api/files/download/message-attachments/1/2025/test-permission.txt"
        message_data = MessageCreate(
            recipient_id=test_admin_user.id,
            content="📎 test-permission.txt",
            type="file",
            file_url=file_url,
            file_name="test-permission.txt",
            file_size=1024,
            file_type="text/plain",
        )

        # Send the message from sender to recipient
        await message_service.send_message(db_session, test_user.id, message_data)

        # Mock storage services to simulate file system behavior
        with patch(
            "app.services.storage_service.get_storage_service"
        ) as mock_storage_service, patch(
            "app.services.local_storage_service.get_local_storage_service"
        ) as mock_local_storage:
            # Mock MinIO storage service to fail (no connection)
            mock_minio = Mock()
            mock_minio.file_exists = Mock(side_effect=Exception("MinIO not available"))
            mock_storage_service.return_value = mock_minio

            # Mock local storage service with proper base_path
            mock_storage = Mock()
            mock_storage.base_path = Path("/tmp/uploads")  # Proper path object
            mock_storage.file_exists = Mock(return_value=True)  # File exists locally
            mock_local_storage.return_value = mock_storage

            # Create the mock file path for FileResponse
            download_path = "message-attachments/1/2025/test-permission.txt"
            _mock_full_path = Path("/tmp/uploads") / download_path

            # Mock path.exists() to return True and patch the FileResponse import
            with patch.object(Path, "exists", return_value=True), patch(
                "fastapi.responses.FileResponse"
            ) as mock_file_response:
                # Mock FileResponse to return a proper response
                from fastapi.responses import Response

                mock_response = Response(
                    content="test file content", media_type="text/plain"
                )
                mock_file_response.return_value = mock_response

                # Test 1: Sender should be able to download
                sender_download = await client.get(
                    f"/api/files/download/{download_path}", headers=sender_headers
                )

                # Test 2: Recipient should be able to download
                recipient_download = await client.get(
                    f"/api/files/download/{download_path}", headers=recipient_headers
                )

                # Both users should have permission (either 200 for successful download or other non-403 status)
                # The key is that neither should get 403 (Forbidden)
                assert (
                    sender_download.status_code != 403
                ), f"Sender should have access, got {sender_download.status_code}"
                assert (
                    recipient_download.status_code != 403
                ), f"Recipient should have access, got {recipient_download.status_code}"

                # Since permission checks passed, the downloads should succeed
