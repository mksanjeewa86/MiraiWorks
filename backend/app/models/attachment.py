from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import VirusStatus


class Attachment(BaseModel):
    __tablename__ = "attachments"
    message_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(
        String(500), nullable=False, unique=True, index=True
    )  # S3 object key
    s3_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # File hash for deduplication

    # Virus scanning
    virus_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=VirusStatus.PENDING.value, index=True
    )
    virus_scan_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadata
    is_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )  # Only true after clean scan
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    upload_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    message = relationship("Message", back_populates="attachments")
    owner = relationship("User")

    @property
    def file_size_mb(self):
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_image(self):
        """Check if attachment is an image."""
        return self.mime_type.startswith("image/") if self.mime_type else False

    @property
    def is_document(self):
        """Check if attachment is a document."""
        document_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/csv",
        ]
        return self.mime_type in document_types if self.mime_type else False

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.original_filename}', virus_status='{self.virus_status}', available={self.is_available})>"
