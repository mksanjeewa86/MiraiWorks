from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.user import User


class TodoAttachment(Base):
    """Model for todo file attachments with no file count limit and 25MB size limit."""

    __tablename__ = "todo_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    todo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Size in bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_extension: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Optional metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    todo: Mapped[Todo] = relationship("Todo", backref="attachments")
    uploader: Mapped[User | None] = relationship(
        "User", foreign_keys=[uploaded_by], backref="uploaded_attachments"
    )

    @property
    def file_size_mb(self) -> float:
        """Return file size in megabytes."""
        return self.file_size / (1024 * 1024)

    @property
    def is_image(self) -> bool:
        """Check if the file is an image."""
        image_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'}
        return self.mime_type in image_types

    @property
    def is_document(self) -> bool:
        """Check if the file is a document."""
        doc_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'text/csv'
        }
        return self.mime_type in doc_types

    @property
    def is_video(self) -> bool:
        """Check if the file is a video."""
        return self.mime_type.startswith('video/')

    @property
    def is_audio(self) -> bool:
        """Check if the file is audio."""
        return self.mime_type.startswith('audio/')

    @property
    def file_category(self) -> str:
        """Get the file category for UI display."""
        if self.is_image:
            return "image"
        elif self.is_document:
            return "document"
        elif self.is_video:
            return "video"
        elif self.is_audio:
            return "audio"
        else:
            return "other"

    def get_file_icon(self) -> str:
        """Get appropriate icon name for the file type."""
        category = self.file_category
        icon_map = {
            "image": "PhotoIcon",
            "document": "DocumentTextIcon",
            "video": "VideoCameraIcon",
            "audio": "SpeakerWaveIcon",
            "other": "DocumentIcon"
        }
        return icon_map.get(category, "DocumentIcon")

    def get_download_url(self) -> str:
        """Generate download URL for the attachment."""
        return f"/api/todos/{self.todo_id}/attachments/{self.id}/download"

    def get_preview_url(self) -> str | None:
        """Generate preview URL for supported file types."""
        if self.is_image or self.mime_type == 'application/pdf':
            return f"/api/todos/{self.todo_id}/attachments/{self.id}/preview"
        return None

    def is_file_exists(self) -> bool:
        """Check if the physical file exists on disk."""
        return os.path.exists(self.file_path)

    def __repr__(self) -> str:
        return f"<TodoAttachment(id={self.id}, filename='{self.original_filename}', size={self.file_size_mb:.2f}MB)>"
