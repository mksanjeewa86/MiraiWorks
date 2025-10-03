"""Company Connection model for company-to-company relationships."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class CompanyConnection(Base):
    """Company-to-company connections requiring approval."""

    __tablename__ = "company_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Requesting company
    requesting_company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Target company
    target_company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Connection status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Status: pending, approved, rejected, blocked"
    )

    # Connection details
    connection_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="partnership",
        comment="Type: partnership, client, vendor, referral"
    )
    
    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional message from requesting company"
    )
    
    response_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional response message from target company"
    )

    # User tracking
    requested_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who initiated the connection request"
    )
    
    responded_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who approved/rejected the request"
    )

    # Permission settings (what the connection allows)
    allow_messaging: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_candidate_sharing: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_position_sharing: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_interview_coordination: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    requested_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Optional expiration date for the connection"
    )

    # Relationships
    requesting_company: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[requesting_company_id],
        back_populates="sent_connection_requests"
    )
    
    target_company: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[target_company_id],
        back_populates="received_connection_requests"
    )
    
    requester: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[requested_by],
        post_update=True
    )
    
    responder: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[responded_by],
        post_update=True
    )

    # Ensure no duplicate connection requests
    __table_args__ = (
        UniqueConstraint(
            'requesting_company_id', 
            'target_company_id', 
            name='unique_company_connection'
        ),
    )

    def __repr__(self) -> str:
        return f"<CompanyConnection(requesting={self.requesting_company_id}, target={self.target_company_id}, status={self.status})>"

    def approve(self, responding_user_id: int, response_message: str = None):
        """Approve the connection request."""
        self.status = "approved"
        self.responded_by = responding_user_id
        self.responded_at = datetime.utcnow()
        if response_message:
            self.response_message = response_message

    def reject(self, responding_user_id: int, response_message: str = None):
        """Reject the connection request."""
        self.status = "rejected"
        self.responded_by = responding_user_id
        self.responded_at = datetime.utcnow()
        if response_message:
            self.response_message = response_message

    def block(self, responding_user_id: int, response_message: str = None):
        """Block future connection requests from this company."""
        self.status = "blocked"
        self.responded_by = responding_user_id
        self.responded_at = datetime.utcnow()
        if response_message:
            self.response_message = response_message

    @property
    def is_active(self) -> bool:
        """Check if the connection is active."""
        return self.status == "approved"

    @property
    def is_pending(self) -> bool:
        """Check if the connection is pending approval."""
        return self.status == "pending"

    @property
    def is_expired(self) -> bool:
        """Check if the connection has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at