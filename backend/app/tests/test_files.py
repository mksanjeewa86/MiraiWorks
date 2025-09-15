import io
import pytest
from unittest.mock import AsyncMock, Mock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestFiles:
    """Comprehensive tests for file management functionality."""

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_upload_file_success(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test successful file upload."""
        # Create test file first to get correct size
        file_content = b"Test file content"

        # Mock storage service
        mock_storage = Mock()
        mock_storage.upload_file_data = AsyncMock(
            return_value=("attachments/1/2024/01/uuid_test.txt", "file_hash", len(file_content))
        )
        mock_storage.get_presigned_url = Mock(
            return_value="https://test.com/download/uuid_test.txt"
        )
        mock_get_storage_service.return_value = mock_storage

        # Create test file data
        file_data = {
            "file": ("test.txt", io.BytesIO(file_content), "text/plain")
        }

        response = await client.post(
            "/api/files/upload",
            files=file_data,
            headers=auth_headers
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
        assert "uuid_test.txt" in data["s3_key"]

        # Verify storage service was called correctly
        mock_storage.upload_file_data.assert_called_once()
        mock_storage.get_presigned_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_unauthorized(self, client: AsyncClient):
        """Test file upload without authentication fails."""
        file_data = {
            "file": ("test.txt", io.BytesIO(b"content"), "text/plain")
        }

        response = await client.post("/api/files/upload", files=file_data)

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_upload_file_no_filename(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file upload without filename fails."""
        file_data = {
            "file": ("", io.BytesIO(b"content"), "text/plain")
        }

        response = await client.post(
            "/api/files/upload",
            files=file_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        # Check for Pydantic validation error about UploadFile
        assert any("UploadFile" in str(error) for error in error_detail)

    @pytest.mark.asyncio
    async def test_upload_file_invalid_extension(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file upload with invalid extension fails."""
        file_data = {
            "file": ("test.exe", io.BytesIO(b"content"), "application/exe")
        }

        response = await client.post(
            "/api/files/upload",
            files=file_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "File type not allowed" in error_detail

    @pytest.mark.asyncio
    async def test_upload_file_too_large(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file upload with file size exceeding limit fails."""
        # Create a file larger than 10MB (MAX_FILE_SIZE)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file_data = {
            "file": ("large.txt", io.BytesIO(large_content), "text/plain")
        }

        response = await client.post(
            "/api/files/upload",
            files=file_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "File too large" in error_detail

    @pytest.mark.asyncio
    async def test_upload_file_valid_extensions(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file upload with various valid extensions."""
        valid_extensions = [
            ("test.txt", "text/plain"),
            ("test.pdf", "application/pdf"),
            ("test.png", "image/png"),
            ("test.jpg", "image/jpeg"),
            ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ]

        with patch('app.services.storage_service.get_storage_service') as mock_get_storage_service:
            mock_storage = Mock()
            mock_storage.upload_file_data = AsyncMock(
                return_value=("test_key", "test_hash", 1024)
            )
            mock_storage.get_presigned_url = Mock(
                return_value="https://test.com/download/test"
            )
            mock_get_storage_service.return_value = mock_storage

            for filename, content_type in valid_extensions:
                file_data = {
                    "file": (filename, io.BytesIO(b"content"), content_type)
                }

                response = await client.post(
                    "/api/files/upload",
                    files=file_data,
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.json()
                assert data["file_name"] == filename
                assert data["success"] is True

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_upload_file_storage_error(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file upload with storage service error."""
        # Mock storage service to raise exception
        mock_storage = Mock()
        mock_storage.upload_file_data = AsyncMock(
            side_effect=Exception("Storage error")
        )
        mock_get_storage_service.return_value = mock_storage

        file_data = {
            "file": ("test.txt", io.BytesIO(b"content"), "text/plain")
        }

        response = await client.post(
            "/api/files/upload",
            files=file_data,
            headers=auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Error saving file" in error_detail

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_download_file_success(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test successful file download URL generation."""
        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.get_presigned_url = Mock(
            return_value="https://test.com/download/test_key"
        )
        mock_get_storage_service.return_value = mock_storage

        test_s3_key = "attachments/1/2024/01/uuid_test.txt"

        response = await client.get(
            f"/api/files/download/{test_s3_key}",
            headers=auth_headers
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
    @patch('app.services.storage_service.get_storage_service')
    async def test_download_file_not_found(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file download with non-existent file fails."""
        # Mock storage service to return file not found
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=False)
        mock_get_storage_service.return_value = mock_storage

        response = await client.get(
            "/api/files/download/nonexistent_key",
            headers=auth_headers
        )

        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "File not found" in error_detail

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_download_file_storage_error(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file download with storage service error."""
        # Mock storage service to raise exception
        mock_storage = Mock()
        mock_storage.file_exists = Mock(side_effect=Exception("Storage error"))
        mock_get_storage_service.return_value = mock_storage

        response = await client.get(
            "/api/files/download/test_key",
            headers=auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Error generating download URL" in error_detail

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_delete_file_success(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test successful file deletion."""
        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.delete_file = Mock(return_value=True)
        mock_get_storage_service.return_value = mock_storage

        test_s3_key = "attachments/1/2024/01/uuid_test.txt"

        response = await client.delete(
            f"/api/files/{test_s3_key}",
            headers=auth_headers
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
    @patch('app.services.storage_service.get_storage_service')
    async def test_delete_file_not_found(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file deletion with non-existent file fails."""
        # Mock storage service to return file not found
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=False)
        mock_get_storage_service.return_value = mock_storage

        response = await client.delete(
            "/api/files/nonexistent_key",
            headers=auth_headers
        )

        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "File not found" in error_detail

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_delete_file_deletion_failed(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file deletion when storage service deletion fails."""
        # Mock storage service
        mock_storage = Mock()
        mock_storage.file_exists = Mock(return_value=True)
        mock_storage.delete_file = Mock(return_value=False)  # Deletion failed
        mock_get_storage_service.return_value = mock_storage

        response = await client.delete(
            "/api/files/test_key",
            headers=auth_headers
        )

        assert response.status_code == 500
        error_detail = response.json()["detail"]
        assert "Failed to delete file" in error_detail

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_delete_file_storage_error(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file deletion with storage service error."""
        # Mock storage service to raise exception
        mock_storage = Mock()
        mock_storage.file_exists = Mock(side_effect=Exception("Storage error"))
        mock_get_storage_service.return_value = mock_storage

        response = await client.delete(
            "/api/files/test_key",
            headers=auth_headers
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
            assert not is_allowed_file(filename), f"File {filename} should not be allowed"

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_upload_with_special_characters_in_filename(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
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
        file_data = {
            "file": (special_filename, io.BytesIO(b"content"), "text/plain")
        }

        response = await client.post(
            "/api/files/upload",
            files=file_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == special_filename
        assert data["success"] is True

    @pytest.mark.asyncio
    @patch('app.services.storage_service.get_storage_service')
    async def test_download_with_nested_path(
        self,
        mock_get_storage_service,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test file download with nested S3 key path."""
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
            f"/api/files/download/{nested_s3_key}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["s3_key"] == nested_s3_key

    @pytest.mark.asyncio
    async def test_file_size_limits(self):
        """Test file size constants."""
        from app.endpoints.files import MAX_FILE_SIZE

        # Verify the file size limit is reasonable
        assert MAX_FILE_SIZE == 10 * 1024 * 1024  # 10MB
        assert MAX_FILE_SIZE > 0

    @pytest.mark.asyncio
    async def test_allowed_extensions_coverage(self):
        """Test that all expected file extensions are allowed."""
        from app.endpoints.files import ALLOWED_EXTENSIONS

        expected_extensions = {
            "txt", "pdf", "png", "jpg", "jpeg", "gif",
            "doc", "docx", "xls", "xlsx", "ppt", "pptx",
            "zip", "rar", "7z"
        }

        # Verify all expected extensions are present
        for ext in expected_extensions:
            assert ext in ALLOWED_EXTENSIONS, f"Extension {ext} should be allowed"

        # Verify extensions are lowercase
        for ext in ALLOWED_EXTENSIONS:
            assert ext.islower(), f"Extension {ext} should be lowercase"