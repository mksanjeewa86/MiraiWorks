from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TodoAttachmentBase(BaseModel):
    """Base schema for todo attachments."""

    description: Optional[str] = Field(
        None, max_length=1000, description="Optional description for the attachment"
    )


class TodoAttachmentCreate(TodoAttachmentBase):
    """Schema for creating a new todo attachment (used internally)."""

    todo_id: int = Field(..., description="ID of the todo this attachment belongs to")
    original_filename: str = Field(..., max_length=255, description="Original filename")
    stored_filename: str = Field(
        ..., max_length=255, description="Stored filename on disk"
    )
    file_path: str = Field(
        ..., max_length=500, description="Full path to the stored file"
    )
    file_size: int = Field(
        ..., ge=1, le=26214400, description="File size in bytes (max 25MB)"
    )
    mime_type: str = Field(..., max_length=100, description="MIME type of the file")
    file_extension: Optional[str] = Field(
        None, max_length=10, description="File extension"
    )
    uploaded_by: Optional[int] = Field(
        None, description="ID of the user who uploaded the file"
    )

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v):
        """Validate file size is within 25MB limit."""
        max_size = 25 * 1024 * 1024  # 25MB in bytes
        if v > max_size:
            raise ValueError(
                f"File size must be less than 25MB (got {v / (1024*1024):.2f}MB)"
            )
        return v

    @field_validator("original_filename", "stored_filename")
    @classmethod
    def validate_filename(cls, v):
        """Validate filename is not empty and contains valid characters."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")

        # Check for invalid characters (basic validation)
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            if char in v:
                raise ValueError(f"Filename contains invalid character: {char}")

        return v.strip()


class TodoAttachmentUpdate(TodoAttachmentBase):
    """Schema for updating a todo attachment."""

    description: Optional[str] = Field(None, max_length=1000)


class TodoAttachmentInfo(TodoAttachmentBase):
    """Schema for returning todo attachment information."""

    id: int
    todo_id: int
    original_filename: str
    file_size: int
    mime_type: str
    file_extension: Optional[str]
    uploaded_by: Optional[int]
    uploaded_at: datetime
    updated_at: datetime

    # Computed properties
    file_size_mb: float = Field(..., description="File size in megabytes")
    file_category: str = Field(
        ..., description="File category (image, document, video, audio, other)"
    )
    file_icon: str = Field(..., description="Icon name for the file type")
    download_url: str = Field(..., description="URL to download the file")
    preview_url: Optional[str] = Field(
        None, description="URL to preview the file (if supported)"
    )
    is_image: bool = Field(..., description="Whether the file is an image")
    is_document: bool = Field(..., description="Whether the file is a document")
    is_video: bool = Field(..., description="Whether the file is a video")
    is_audio: bool = Field(..., description="Whether the file is an audio file")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_with_computed(cls, attachment_orm):
        """Create schema with computed properties from ORM object."""
        return cls(
            id=attachment_orm.id,
            todo_id=attachment_orm.todo_id,
            original_filename=attachment_orm.original_filename,
            file_size=attachment_orm.file_size,
            mime_type=attachment_orm.mime_type,
            file_extension=attachment_orm.file_extension,
            description=attachment_orm.description,
            uploaded_by=attachment_orm.uploaded_by,
            uploaded_at=attachment_orm.uploaded_at,
            updated_at=attachment_orm.updated_at,
            # Computed properties
            file_size_mb=attachment_orm.file_size_mb,
            file_category=attachment_orm.file_category,
            file_icon=attachment_orm.get_file_icon(),
            download_url=attachment_orm.get_download_url(),
            preview_url=attachment_orm.get_preview_url(),
            is_image=attachment_orm.is_image,
            is_document=attachment_orm.is_document,
            is_video=attachment_orm.is_video,
            is_audio=attachment_orm.is_audio,
        )


class TodoAttachmentList(BaseModel):
    """Schema for listing todo attachments."""

    attachments: list[TodoAttachmentInfo] = Field(
        ..., description="List of attachments"
    )
    total_count: int = Field(..., description="Total number of attachments")
    total_size_mb: float = Field(..., description="Total size of all attachments in MB")


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""

    message: str = Field(..., description="Success message")
    attachment: TodoAttachmentInfo = Field(
        ..., description="Information about the uploaded file"
    )


class FileUploadRequest(BaseModel):
    """Schema for file upload request metadata."""

    description: Optional[str] = Field(
        None, max_length=1000, description="Optional description for the file"
    )


class AttachmentStats(BaseModel):
    """Schema for attachment statistics."""

    total_attachments: int = Field(..., description="Total number of attachments")
    total_size_mb: float = Field(..., description="Total size in megabytes")
    file_type_counts: dict[str, int] = Field(
        ..., description="Count of files by category"
    )
    largest_file: Optional[TodoAttachmentInfo] = Field(
        None, description="Information about the largest file"
    )
    recent_attachments: list[TodoAttachmentInfo] = Field(
        ..., description="Most recently uploaded attachments"
    )


class BulkDeleteRequest(BaseModel):
    """Schema for bulk deleting attachments."""

    attachment_ids: list[int] = Field(
        ..., min_length=1, description="List of attachment IDs to delete"
    )


class BulkDeleteResponse(BaseModel):
    """Schema for bulk delete response."""

    message: str = Field(..., description="Success message")
    deleted_count: int = Field(..., description="Number of attachments deleted")
    failed_deletions: list[dict] = Field(
        default_factory=list, description="List of failed deletions with reasons"
    )
