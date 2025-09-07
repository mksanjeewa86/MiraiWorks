from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.utils.constants import VirusStatus


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename = Column(String(255), nullable=False)
    s3_key = Column(
        String(500), nullable=False, unique=True, index=True
    )  # S3 object key
    s3_bucket = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False, index=True)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    sha256_hash = Column(
        String(64), nullable=False, index=True
    )  # File hash for deduplication

    # Virus scanning
    virus_status = Column(
        String(20), nullable=False, default=VirusStatus.PENDING.value, index=True
    )
    virus_scan_result = Column(Text, nullable=True)  # Detailed scan result
    scanned_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    is_available = Column(
        Boolean, nullable=False, default=False, index=True
    )  # Only true after clean scan
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    upload_ip = Column(String(45), nullable=True)  # IP address of uploader

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

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
