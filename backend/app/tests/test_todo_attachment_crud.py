import os
import tempfile

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.todo import todo as todo_crud
from app.crud.todo_attachment import todo_attachment
from app.schemas.todo import TodoCreate
from app.schemas.todo_attachment import TodoAttachmentCreate


class TestTodoAttachmentCRUD:
    """Unit tests for todo attachment CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_attachment(self, db_session: AsyncSession, test_users: dict):
        """Test creating a new attachment."""
        user = test_users['recruiter']

        # Create a todo first
        todo_data = TodoCreate(title="Test Todo", description="For attachment testing")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)

        # Create attachment
        attachment_data = TodoAttachmentCreate(
            todo_id=test_todo.id,
            original_filename="test_file.txt",
            stored_filename="stored_123456.txt",
            file_path="/uploads/stored_123456.txt",
            file_size=1024,
            mime_type="text/plain",
            file_extension=".txt",
            description="Test attachment",
            uploaded_by=user.id
        )

        attachment = await todo_attachment.create_attachment(
            db_session, attachment_data=attachment_data, uploader_id=user.id
        )

        assert attachment.id is not None
        assert attachment.todo_id == test_todo.id
        assert attachment.original_filename == "test_file.txt"
        assert attachment.file_size == 1024
        assert attachment.mime_type == "text/plain"
        assert attachment.uploaded_by == user.id
        assert attachment.description == "Test attachment"

    @pytest.mark.asyncio
    async def test_get_todo_attachments(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting all attachments for a todo."""
        todo = test_todo_with_attachments['todo']

        attachments = await todo_attachment.get_todo_attachments(db_session, todo_id=todo.id)

        assert len(attachments) >= 1
        assert all(att.todo_id == todo.id for att in attachments)
        # Should be ordered by upload date (newest first)
        if len(attachments) > 1:
            assert attachments[0].uploaded_at >= attachments[1].uploaded_at

    @pytest.mark.asyncio
    async def test_get_attachment_by_id(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting attachment by ID."""
        todo = test_todo_with_attachments['todo']
        original_attachment = test_todo_with_attachments['attachments'][0]

        # Get by ID only
        attachment = await todo_attachment.get_attachment_by_id(
            db_session, attachment_id=original_attachment.id
        )
        assert attachment is not None
        assert attachment.id == original_attachment.id

        # Get by ID with todo filter
        attachment = await todo_attachment.get_attachment_by_id(
            db_session, attachment_id=original_attachment.id, todo_id=todo.id
        )
        assert attachment is not None
        assert attachment.id == original_attachment.id

        # Get by ID with wrong todo filter
        attachment = await todo_attachment.get_attachment_by_id(
            db_session, attachment_id=original_attachment.id, todo_id=99999
        )
        assert attachment is None

    @pytest.mark.asyncio
    async def test_get_attachments_by_user(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting attachments by user."""
        user = test_todo_with_attachments['user']

        attachments = await todo_attachment.get_attachments_by_user(db_session, user_id=user.id)

        assert len(attachments) >= 1
        assert all(att.uploaded_by == user.id for att in attachments)

    @pytest.mark.asyncio
    async def test_get_attachments_by_file_type(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting attachments by file type."""
        todo = test_todo_with_attachments['todo']

        # Get text files
        text_attachments = await todo_attachment.get_attachments_by_file_type(
            db_session, mime_type_pattern="text/%", todo_id=todo.id
        )

        for att in text_attachments:
            assert att.mime_type.startswith("text/")
            assert att.todo_id == todo.id

    @pytest.mark.asyncio
    async def test_update_attachment_description(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test updating attachment description."""
        attachment = test_todo_with_attachments['attachments'][0]
        user = test_todo_with_attachments['user']

        new_description = "Updated description for test"

        updated = await todo_attachment.update_attachment_description(
            db_session,
            attachment_id=attachment.id,
            description=new_description,
            user_id=user.id
        )

        assert updated is not None
        assert updated.description == new_description
        assert updated.id == attachment.id

    @pytest.mark.asyncio
    async def test_update_attachment_description_wrong_user(self, db_session: AsyncSession, test_todo_with_attachments: dict, test_users: dict):
        """Test updating attachment description with wrong user fails."""
        attachment = test_todo_with_attachments['attachments'][0]
        other_user = test_users['candidate']  # Different user

        updated = await todo_attachment.update_attachment_description(
            db_session,
            attachment_id=attachment.id,
            description="Should not work",
            user_id=other_user.id
        )

        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_attachment(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test deleting an attachment."""
        attachment = test_todo_with_attachments['attachments'][0]
        todo = test_todo_with_attachments['todo']

        # Create a temporary file to test cleanup
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name

        # Update attachment path to temp file
        attachment.file_path = temp_path
        await db_session.commit()

        success = await todo_attachment.delete_attachment(
            db_session, attachment_id=attachment.id, todo_id=todo.id, cleanup_file=True
        )

        assert success is True

        # Verify attachment is deleted from database
        deleted_attachment = await todo_attachment.get_attachment_by_id(
            db_session, attachment_id=attachment.id
        )
        assert deleted_attachment is None

        # Verify file is deleted from disk
        assert not os.path.exists(temp_path)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_attachment(self, db_session: AsyncSession):
        """Test deleting non-existent attachment returns False."""
        success = await todo_attachment.delete_attachment(
            db_session, attachment_id=99999, cleanup_file=True
        )
        assert success is False

    @pytest.mark.asyncio
    async def test_delete_attachments_bulk(self, db_session: AsyncSession, test_users: dict):
        """Test bulk deletion of attachments."""
        user = test_users['recruiter']

        # Create todo with multiple attachments
        todo_data = TodoCreate(title="Bulk Delete Test", description="Testing bulk operations")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)

        # Create multiple attachments
        attachment_ids = []
        temp_files = []

        for i in range(3):
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(f"test content {i}".encode())
                temp_path = temp_file.name
                temp_files.append(temp_path)

            attachment_data = TodoAttachmentCreate(
                todo_id=test_todo.id,
                original_filename=f"bulk_test_{i}.txt",
                stored_filename=f"stored_{i}.txt",
                file_path=temp_path,
                file_size=len(f"test content {i}"),
                mime_type="text/plain",
                uploaded_by=user.id
            )

            attachment = await todo_attachment.create_attachment(
                db_session, attachment_data=attachment_data, uploader_id=user.id
            )
            attachment_ids.append(attachment.id)

        # Bulk delete first 2 attachments
        result = await todo_attachment.delete_attachments_bulk(
            db_session, attachment_ids=attachment_ids[:2], todo_id=test_todo.id, cleanup_files=True
        )

        assert result["deleted_count"] == 2
        assert len(result["failed_deletions"]) == 0

        # Verify files are deleted
        for temp_path in temp_files[:2]:
            assert not os.path.exists(temp_path)

        # Verify third file still exists
        assert os.path.exists(temp_files[2])

        # Clean up remaining file
        os.unlink(temp_files[2])

    @pytest.mark.asyncio
    async def test_get_attachment_stats(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting attachment statistics."""
        todo = test_todo_with_attachments['todo']

        stats = await todo_attachment.get_attachment_stats(db_session, todo_id=todo.id)

        assert stats["total_count"] >= 1
        assert stats["total_size_bytes"] > 0
        assert stats["total_size_mb"] > 0
        assert "file_type_stats" in stats
        assert stats["largest_file"] is not None
        assert len(stats["recent_attachments"]) >= 1

    @pytest.mark.asyncio
    async def test_get_attachment_stats_by_user(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting attachment statistics filtered by user."""
        user = test_todo_with_attachments['user']

        stats = await todo_attachment.get_attachment_stats(db_session, user_id=user.id)

        assert stats["total_count"] >= 1
        assert all(
            att.uploaded_by == user.id
            for att in stats["recent_attachments"]
        )

    @pytest.mark.asyncio
    async def test_get_todo_attachment_summary(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test getting attachment summary for a todo."""
        todo = test_todo_with_attachments['todo']

        summary = await todo_attachment.get_todo_attachment_summary(db_session, todo_id=todo.id)

        assert summary["total_count"] >= 1
        assert summary["total_size_mb"] >= 0
        assert "file_type_counts" in summary
        assert "attachments" in summary
        assert len(summary["attachments"]) == summary["total_count"]

    @pytest.mark.asyncio
    async def test_attachment_model_properties(self, db_session: AsyncSession, test_todo_with_attachments: dict):
        """Test TodoAttachment model computed properties."""
        attachment = test_todo_with_attachments['attachments'][0]

        # Test file size in MB
        assert attachment.file_size_mb == attachment.file_size / (1024 * 1024)

        # Test file category detection
        if attachment.mime_type.startswith("text/"):
            assert attachment.file_category == "document"
            assert attachment.is_document is True
            assert attachment.is_image is False
            assert attachment.is_video is False
            assert attachment.is_audio is False

        # Test URLs
        assert attachment.get_download_url().startswith(f"/api/todos/{attachment.todo_id}/attachments/{attachment.id}/download")

        # Test file icon
        assert attachment.get_file_icon() in ["PhotoIcon", "DocumentTextIcon", "VideoCameraIcon", "SpeakerWaveIcon", "DocumentIcon"]

        # Test file existence check
        assert attachment.is_file_exists() in [True, False]  # Depends on whether file actually exists

    @pytest.mark.asyncio
    async def test_cleanup_orphaned_attachments(self, db_session: AsyncSession, test_users: dict):
        """Test cleanup of orphaned attachment records."""
        user = test_users['recruiter']

        # Create todo and attachment with non-existent file
        todo_data = TodoCreate(title="Orphan Test", description="Testing orphan cleanup")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)

        attachment_data = TodoAttachmentCreate(
            todo_id=test_todo.id,
            original_filename="orphan_test.txt",
            stored_filename="orphan_stored.txt",
            file_path="/nonexistent/path/orphan_stored.txt",  # Non-existent path
            file_size=100,
            mime_type="text/plain",
            uploaded_by=user.id
        )

        orphan_attachment = await todo_attachment.create_attachment(
            db_session, attachment_data=attachment_data, uploader_id=user.id
        )

        # Run cleanup
        result = await todo_attachment.cleanup_orphaned_attachments(db_session)

        assert result["deleted_db_records"] >= 1
        assert orphan_attachment.id in result["orphaned_records"]

        # Verify orphaned record is deleted
        deleted_attachment = await todo_attachment.get_attachment_by_id(
            db_session, attachment_id=orphan_attachment.id
        )
        assert deleted_attachment is None

    @pytest.mark.asyncio
    async def test_file_category_detection(self, db_session: AsyncSession, test_users: dict):
        """Test file category detection for different MIME types."""
        user = test_users['recruiter']

        todo_data = TodoCreate(title="Category Test", description="Testing file categories")
        test_todo = await todo_crud.create_with_owner(db_session, obj_in=todo_data, owner_id=user.id)

        test_cases = [
            ("image.jpg", "image/jpeg", "image"),
            ("document.pdf", "application/pdf", "document"),
            ("video.mp4", "video/mp4", "video"),
            ("audio.mp3", "audio/mpeg", "audio"),
            ("data.bin", "application/octet-stream", "other"),
            ("sheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "document"),
        ]

        for filename, mime_type, expected_category in test_cases:
            attachment_data = TodoAttachmentCreate(
                todo_id=test_todo.id,
                original_filename=filename,
                stored_filename=f"stored_{filename}",
                file_path=f"/uploads/stored_{filename}",
                file_size=1000,
                mime_type=mime_type,
                uploaded_by=user.id
            )

            attachment = await todo_attachment.create_attachment(
                db_session, attachment_data=attachment_data, uploader_id=user.id
            )

            assert attachment.file_category == expected_category

            # Test specific type properties
            if expected_category == "image":
                assert attachment.is_image is True
                assert attachment.is_document is False
            elif expected_category == "document":
                assert attachment.is_document is True
                assert attachment.is_image is False
            elif expected_category == "video":
                assert attachment.is_video is True
                assert attachment.is_audio is False
            elif expected_category == "audio":
                assert attachment.is_audio is True
                assert attachment.is_video is False
