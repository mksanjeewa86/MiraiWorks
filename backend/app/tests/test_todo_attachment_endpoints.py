from io import BytesIO

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.todo import todo as todo_crud
from app.schemas.todo import TodoCreate
from app.tests.conftest import get_auth_headers_for_user


class TestTodoAttachmentEndpoints:
    """Comprehensive tests for todo attachment functionality."""

    @pytest.mark.asyncio
    async def test_upload_file_success(
        self, client: AsyncClient, db_session: AsyncSession, test_user
    ):
        """Test successful file upload to todo."""
        user = test_user
        
        # Create a test todo
        todo_data = TodoCreate(
            title="Test Todo with Attachments",
            description="Testing file attachments"
        )
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        # Create test file content
        file_content = b"This is test file content for attachment testing."
        
        # Upload file
        files = {
            "file": ("test_document.txt", BytesIO(file_content), "text/plain")
        }
        data = {
            "description": "Test file attachment"
        }
        
        response = await client.post(
            f"/api/todos/{test_todo.id}/attachments/upload",
            files=files,
            data=data,
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["message"] == "File 'test_document.txt' uploaded successfully"
        assert result["attachment"]["original_filename"] == "test_document.txt"
        assert result["attachment"]["file_size"] == len(file_content)
        assert result["attachment"]["mime_type"] == "text/plain"
        assert result["attachment"]["description"] == "Test file attachment"
        assert result["attachment"]["is_document"] is True

    @pytest.mark.asyncio
    async def test_upload_file_size_limit(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test file upload size limit enforcement (25MB)."""
        user = test_users['recruiter']
        
        # Create a test todo
        todo_data = TodoCreate(title="Test Todo", description="Testing size limits")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        # Create file larger than 25MB
        large_content = b"x" * (26 * 1024 * 1024)  # 26MB
        
        files = {
            "file": ("large_file.txt", BytesIO(large_content), "text/plain")
        }
        
        response = await client.post(
            f"/api/todos/{test_todo.id}/attachments/upload",
            files=files,
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 400
        assert "exceeds 25MB limit" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_empty_file(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test upload of empty file fails."""
        user = test_users['recruiter']
        
        # Create a test todo
        todo_data = TodoCreate(title="Test Todo", description="Testing empty file")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        # Upload empty file
        files = {
            "file": ("empty.txt", BytesIO(b""), "text/plain")
        }
        
        response = await client.post(
            f"/api/todos/{test_todo.id}/attachments/upload",
            files=files,
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 400
        assert "File is empty" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_to_nonexistent_todo(
        self, client: AsyncClient, test_users: dict
    ):
        """Test file upload to non-existent todo fails."""
        user = test_users['recruiter']
        
        files = {
            "file": ("test.txt", BytesIO(b"test content"), "text/plain")
        }
        
        response = await client.post(
            f"/api/todos/99999/attachments/upload",
            files=files,
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 404
        assert "Todo not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_unauthorized(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test file upload without proper permissions fails."""
        owner = test_users['recruiter']
        other_user = test_users['candidate']
        
        # Create todo owned by someone else
        todo_data = TodoCreate(title="Other's Todo", description="Not accessible")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=owner.id)
        
        files = {
            "file": ("test.txt", BytesIO(b"test content"), "text/plain")
        }
        
        response = await client.post(
            f"/api/todos/{test_todo.id}/attachments/upload",
            files=files,
            headers=await get_auth_headers_for_user(client, other_user)
        )
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_todo_attachments(
        self, client: AsyncClient, db_session: AsyncSession, test_todo_with_attachments: dict
    ):
        """Test getting all attachments for a todo."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        
        response = await client.get(
            f"/api/todos/{todo.id}/attachments",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "attachments" in result
        assert "total_count" in result
        assert "total_size_mb" in result
        assert result["total_count"] >= 1

    @pytest.mark.asyncio
    async def test_get_attachment_details(
        self, client: AsyncClient, test_todo_with_attachments: dict
    ):
        """Test getting specific attachment details."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        attachment = test_todo_with_attachments['attachments'][0]
        
        response = await client.get(
            f"/api/todos/{todo.id}/attachments/{attachment.id}",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == attachment.id
        assert result["original_filename"] == attachment.original_filename
        assert result["file_size"] == attachment.file_size

    @pytest.mark.asyncio
    async def test_download_attachment(
        self, client: AsyncClient, test_todo_with_attachments: dict
    ):
        """Test downloading an attachment."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        attachment = test_todo_with_attachments['attachments'][0]
        
        response = await client.get(
            f"/api/todos/{todo.id}/attachments/{attachment.id}/download",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        # Check that we got file content
        assert len(response.content) > 0
        # Check Content-Disposition header
        assert "attachment" in response.headers.get("content-disposition", "")

    @pytest.mark.asyncio
    async def test_preview_image_attachment(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test previewing an image attachment."""
        user = test_users['recruiter']
        
        # Create todo and image attachment
        todo_data = TodoCreate(title="Image Test", description="Testing image preview")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        # Create fake image content (minimal PNG header)
        image_content = b"\x89PNG\r\n\x1a\n" + b"fake image data"
        
        files = {
            "file": ("test_image.png", BytesIO(image_content), "image/png")
        }
        
        upload_response = await client.post(
            f"/api/todos/{test_todo.id}/attachments/upload",
            files=files,
            headers=await get_auth_headers_for_user(client, user)
        )
        
        attachment_id = upload_response.json()["attachment"]["id"]
        
        # Test preview
        response = await client.get(
            f"/api/todos/{test_todo.id}/attachments/{attachment_id}/preview",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/png"

    @pytest.mark.asyncio
    async def test_preview_unsupported_file_type(
        self, client: AsyncClient, test_todo_with_attachments: dict
    ):
        """Test preview fails for unsupported file types."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        attachment = test_todo_with_attachments['attachments'][0]  # Should be text file
        
        response = await client.get(
            f"/api/todos/{todo.id}/attachments/{attachment.id}/preview",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 400
        assert "Preview not supported" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_attachment_description(
        self, client: AsyncClient, test_todo_with_attachments: dict
    ):
        """Test updating attachment description."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        attachment = test_todo_with_attachments['attachments'][0]
        
        new_description = "Updated description for test file"
        
        response = await client.put(
            f"/api/todos/{todo.id}/attachments/{attachment.id}",
            data={"description": new_description},
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["description"] == new_description

    @pytest.mark.asyncio
    async def test_delete_attachment(
        self, client: AsyncClient, test_todo_with_attachments: dict
    ):
        """Test deleting an attachment."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        attachment = test_todo_with_attachments['attachments'][0]
        
        response = await client.delete(
            f"/api/todos/{todo.id}/attachments/{attachment.id}",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 204
        
        # Verify attachment is deleted
        get_response = await client.get(
            f"/api/todos/{todo.id}/attachments/{attachment.id}",
            headers=await get_auth_headers_for_user(client, user)
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_bulk_delete_attachments(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test bulk deletion of multiple attachments."""
        user = test_users['recruiter']
        
        # Create todo with multiple attachments
        todo_data = TodoCreate(title="Bulk Delete Test", description="Testing bulk operations")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        attachment_ids = []
        
        # Upload multiple files
        for i in range(3):
            files = {
                "file": (f"test_file_{i}.txt", BytesIO(f"Content {i}".encode()), "text/plain")
            }
            
            response = await client.post(
                f"/api/todos/{test_todo.id}/attachments/upload",
                files=files,
                headers=await get_auth_headers_for_user(client, user)
            )
            
            attachment_ids.append(response.json()["attachment"]["id"])
        
        # Bulk delete
        delete_data = {"attachment_ids": attachment_ids[:2]}  # Delete first 2
        
        response = await client.post(
            f"/api/todos/{test_todo.id}/attachments/bulk-delete",
            json=delete_data,
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 2
        assert len(result["failed_deletions"]) == 0

    @pytest.mark.asyncio
    async def test_get_attachment_stats(
        self, client: AsyncClient, test_todo_with_attachments: dict
    ):
        """Test getting attachment statistics for a todo."""
        todo = test_todo_with_attachments['todo']
        user = test_todo_with_attachments['user']
        
        response = await client.get(
            f"/api/todos/{todo.id}/attachments/stats",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "total_attachments" in result
        assert "total_size_mb" in result
        assert "file_type_counts" in result
        assert result["total_attachments"] >= 1

    @pytest.mark.asyncio
    async def test_get_my_uploads(
        self, client: AsyncClient, test_users: dict
    ):
        """Test getting user's uploaded attachments."""
        user = test_users['recruiter']
        
        response = await client.get(
            "/api/attachments/my-uploads",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_file_type_detection(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test file type detection for different file formats."""
        user = test_users['recruiter']
        
        todo_data = TodoCreate(title="File Type Test", description="Testing file types")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        # Test different file types
        test_files = [
            ("image.jpg", b"\xff\xd8\xff\xe0fake jpeg", "image/jpeg"),
            ("document.pdf", b"%PDF-1.4fake pdf", "application/pdf"),
            ("video.mp4", b"fake mp4 content", "video/mp4"),
            ("audio.mp3", b"fake mp3 content", "audio/mpeg"),
        ]
        
        for filename, content, mime_type in test_files:
            files = {
                "file": (filename, BytesIO(content), mime_type)
            }
            
            response = await client.post(
                f"/api/todos/{test_todo.id}/attachments/upload",
                files=files,
                headers=await get_auth_headers_for_user(client, user)
            )
            
            assert response.status_code == 201
            result = response.json()
            attachment = result["attachment"]
            
            # Verify file category is correctly detected
            if mime_type.startswith("image/"):
                assert attachment["file_category"] == "image"
                assert attachment["is_image"] is True
            elif mime_type == "application/pdf":
                assert attachment["file_category"] == "document"
                assert attachment["is_document"] is True
            elif mime_type.startswith("video/"):
                assert attachment["file_category"] == "video"
                assert attachment["is_video"] is True
            elif mime_type.startswith("audio/"):
                assert attachment["file_category"] == "audio"
                assert attachment["is_audio"] is True

    @pytest.mark.asyncio
    async def test_concurrent_uploads(
        self, client: AsyncClient, db_session: AsyncSession, test_users: dict
    ):
        """Test handling multiple concurrent file uploads."""
        user = test_users['recruiter']
        
        todo_data = TodoCreate(title="Concurrent Test", description="Testing concurrent uploads")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)
        
        # Create multiple upload tasks
        import asyncio
        
        async def upload_file(filename: str, content: bytes):
            files = {"file": (filename, BytesIO(content), "text/plain")}
            return await client.post(
                f"/api/todos/{test_todo.id}/attachments/upload",
                files=files,
                headers=await get_auth_headers_for_user(client, user)
            )
        
        # Upload 5 files concurrently
        tasks = [
            upload_file(f"concurrent_{i}.txt", f"Content {i}".encode())
            for i in range(5)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All uploads should succeed
        for response in responses:
            assert response.status_code == 201
        
        # Verify all files are stored
        get_response = await client.get(
            f"/api/todos/{test_todo.id}/attachments",
            headers=await get_auth_headers_for_user(client, user)
        )
        
        assert get_response.status_code == 200
        result = get_response.json()
        assert result["total_count"] == 5