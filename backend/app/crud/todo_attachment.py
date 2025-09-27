from typing import Any

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.todo_attachment import TodoAttachment
from app.schemas.todo_attachment import TodoAttachmentCreate, TodoAttachmentUpdate
from app.services.file_storage_service import file_storage_service


class CRUDTodoAttachment(CRUDBase[TodoAttachment, TodoAttachmentCreate, TodoAttachmentUpdate]):
    """CRUD operations for todo attachments."""

    async def create_attachment(
        self,
        db: AsyncSession,
        *,
        attachment_data: TodoAttachmentCreate,
        uploader_id: int | None = None
    ) -> TodoAttachment:
        """Create a new todo attachment."""
        db_obj = TodoAttachment(
            todo_id=attachment_data.todo_id,
            uploaded_by=uploader_id or attachment_data.uploaded_by,
            original_filename=attachment_data.original_filename,
            stored_filename=attachment_data.stored_filename,
            file_path=attachment_data.file_path,
            file_size=attachment_data.file_size,
            mime_type=attachment_data.mime_type,
            file_extension=attachment_data.file_extension,
            description=attachment_data.description,
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_todo_attachments(
        self,
        db: AsyncSession,
        *,
        todo_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[TodoAttachment]:
        """Get all attachments for a specific todo."""
        query = (
            select(TodoAttachment)
            .where(TodoAttachment.todo_id == todo_id)
            .order_by(desc(TodoAttachment.uploaded_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_attachment_by_id(
        self,
        db: AsyncSession,
        *,
        attachment_id: int,
        todo_id: int | None = None
    ) -> TodoAttachment | None:
        """Get attachment by ID, optionally filtered by todo_id."""
        conditions = [TodoAttachment.id == attachment_id]
        if todo_id is not None:
            conditions.append(TodoAttachment.todo_id == todo_id)

        query = select(TodoAttachment).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_attachments_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[TodoAttachment]:
        """Get all attachments uploaded by a specific user."""
        query = (
            select(TodoAttachment)
            .where(TodoAttachment.uploaded_by == user_id)
            .order_by(desc(TodoAttachment.uploaded_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_attachments_by_file_type(
        self,
        db: AsyncSession,
        *,
        mime_type_pattern: str,
        todo_id: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[TodoAttachment]:
        """Get attachments by MIME type pattern (e.g., 'image/%', 'application/pdf')."""
        conditions = [TodoAttachment.mime_type.like(mime_type_pattern)]
        if todo_id is not None:
            conditions.append(TodoAttachment.todo_id == todo_id)

        query = (
            select(TodoAttachment)
            .where(and_(*conditions))
            .order_by(desc(TodoAttachment.uploaded_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def update_attachment_description(
        self,
        db: AsyncSession,
        *,
        attachment_id: int,
        description: str | None,
        user_id: int | None = None
    ) -> TodoAttachment | None:
        """Update attachment description."""
        conditions = [TodoAttachment.id == attachment_id]
        if user_id is not None:
            conditions.append(TodoAttachment.uploaded_by == user_id)

        query = select(TodoAttachment).where(and_(*conditions))
        result = await db.execute(query)
        attachment = result.scalar_one_or_none()

        if attachment:
            attachment.description = description
            await db.commit()
            await db.refresh(attachment)

        return attachment

    async def delete_attachment(
        self,
        db: AsyncSession,
        *,
        attachment_id: int,
        todo_id: int | None = None,
        cleanup_file: bool = True
    ) -> bool:
        """Delete an attachment and optionally its file."""
        conditions = [TodoAttachment.id == attachment_id]
        if todo_id is not None:
            conditions.append(TodoAttachment.todo_id == todo_id)

        query = select(TodoAttachment).where(and_(*conditions))
        result = await db.execute(query)
        attachment = result.scalar_one_or_none()

        if not attachment:
            return False

        # Store file path before deleting from DB
        file_path = attachment.file_path

        # Delete from database
        await db.delete(attachment)
        await db.commit()

        # Delete physical file if requested
        if cleanup_file:
            file_storage_service.delete_file(file_path)

        return True

    async def delete_attachments_bulk(
        self,
        db: AsyncSession,
        *,
        attachment_ids: list[int],
        todo_id: int | None = None,
        cleanup_files: bool = True
    ) -> dict[str, Any]:
        """Delete multiple attachments in bulk."""
        conditions = [TodoAttachment.id.in_(attachment_ids)]
        if todo_id is not None:
            conditions.append(TodoAttachment.todo_id == todo_id)

        query = select(TodoAttachment).where(and_(*conditions))
        result = await db.execute(query)
        attachments = result.scalars().all()

        deleted_count = 0
        failed_deletions = []
        file_paths = []

        for attachment in attachments:
            try:
                file_paths.append(attachment.file_path)
                await db.delete(attachment)
                deleted_count += 1
            except Exception as e:
                failed_deletions.append({
                    "attachment_id": attachment.id,
                    "filename": attachment.original_filename,
                    "error": str(e)
                })

        await db.commit()

        # Delete physical files if requested
        if cleanup_files:
            for file_path in file_paths:
                file_storage_service.delete_file(file_path)

        return {
            "deleted_count": deleted_count,
            "failed_deletions": failed_deletions,
            "cleaned_files": len(file_paths) if cleanup_files else 0
        }

    async def get_attachment_stats(
        self,
        db: AsyncSession,
        *,
        todo_id: int | None = None,
        user_id: int | None = None
    ) -> dict[str, Any]:
        """Get statistics about attachments."""
        conditions = []
        if todo_id is not None:
            conditions.append(TodoAttachment.todo_id == todo_id)
        if user_id is not None:
            conditions.append(TodoAttachment.uploaded_by == user_id)

        base_query = select(TodoAttachment)
        if conditions:
            base_query = base_query.where(and_(*conditions))

        # Get total count and size
        count_query = select(func.count(TodoAttachment.id), func.sum(TodoAttachment.file_size))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total_count, total_size = count_result.first()

        total_size = total_size or 0

        # Get file type distribution
        type_query = select(
            TodoAttachment.mime_type,
            func.count(TodoAttachment.id).label('count'),
            func.sum(TodoAttachment.file_size).label('size')
        )
        if conditions:
            type_query = type_query.where(and_(*conditions))
        type_query = type_query.group_by(TodoAttachment.mime_type)

        type_result = await db.execute(type_query)
        file_type_stats = {}
        for mime_type, count, size in type_result:
            category = self._get_file_category_from_mime(mime_type)
            if category not in file_type_stats:
                file_type_stats[category] = {"count": 0, "size": 0}
            file_type_stats[category]["count"] += count
            file_type_stats[category]["size"] += size or 0

        # Get largest file
        largest_query = base_query.order_by(desc(TodoAttachment.file_size)).limit(1)
        largest_result = await db.execute(largest_query)
        largest_file = largest_result.scalar_one_or_none()

        # Get recent attachments
        recent_query = base_query.order_by(desc(TodoAttachment.uploaded_at)).limit(5)
        recent_result = await db.execute(recent_query)
        recent_attachments = recent_result.scalars().all()

        return {
            "total_count": total_count or 0,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024) if total_size else 0,
            "file_type_stats": file_type_stats,
            "largest_file": largest_file,
            "recent_attachments": recent_attachments
        }

    def _get_file_category_from_mime(self, mime_type: str) -> str:
        """Get file category from MIME type."""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type in {
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain', 'text/csv'
        }:
            return 'document'
        else:
            return 'other'

    async def get_todo_attachment_summary(
        self,
        db: AsyncSession,
        *,
        todo_id: int
    ) -> dict[str, Any]:
        """Get a summary of attachments for a todo."""
        attachments = await self.get_todo_attachments(db, todo_id=todo_id)

        total_size = sum(att.file_size for att in attachments)
        file_type_counts = {}

        for attachment in attachments:
            category = attachment.file_category
            file_type_counts[category] = file_type_counts.get(category, 0) + 1

        return {
            "total_count": len(attachments),
            "total_size_mb": total_size / (1024 * 1024),
            "file_type_counts": file_type_counts,
            "attachments": attachments
        }

    async def cleanup_orphaned_attachments(
        self,
        db: AsyncSession
    ) -> dict[str, Any]:
        """Clean up attachment records for which the physical file no longer exists."""
        query = select(TodoAttachment)
        result = await db.execute(query)
        all_attachments = result.scalars().all()

        orphaned_records = []
        valid_file_paths = []

        for attachment in all_attachments:
            if not attachment.is_file_exists():
                orphaned_records.append(attachment)
            else:
                valid_file_paths.append(attachment.file_path)

        # Delete orphaned records from database
        deleted_count = 0
        for attachment in orphaned_records:
            await db.delete(attachment)
            deleted_count += 1

        await db.commit()

        # Clean up orphaned files on disk
        cleanup_result = file_storage_service.cleanup_orphaned_files(valid_file_paths)

        return {
            "deleted_db_records": deleted_count,
            "orphaned_records": [att.id for att in orphaned_records],
            "file_cleanup": cleanup_result
        }


# Global CRUD instance
todo_attachment = CRUDTodoAttachment(TodoAttachment)
