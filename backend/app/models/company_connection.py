"""Company connection model for company-based interactions."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.utils.datetime_utils import get_utc_now

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class CompanyConnection(Base):
    """
    Company-based connections for messaging and interactions.

    Supports two types of connections:
    1. User-to-Company: Individual user connects to a company
    2. Company-to-Company: Two companies connect together
    """

    __tablename__ = "company_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Source entity (user or company)
    source_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type of source entity: user or company",
    )
    source_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="User ID if source is a user",
    )
    source_company_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Company ID if source is a company",
    )

    # Target entity (always a company)
    target_company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Target company ID",
    )

    # Connection metadata
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True, comment="Whether connection is active"
    )
    connection_type: Mapped[str] = mapped_column(
        String(50),
        default="standard",
        nullable=False,
        comment="Type of connection: standard, partnership, etc",
    )

    # Permissions (for future expansion)
    can_message: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Can send messages"
    )
    can_view_profile: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Can view profiles"
    )
    can_assign_tasks: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Can assign tasks"
    )

    # Creation tracking
    creation_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="manual",
        comment="How connection was created: manual, automatic, api",
    )
    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created this connection",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=get_utc_now, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    source_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[source_user_id],
        back_populates="company_connections_as_user",
    )
    source_company: Mapped["Company | None"] = relationship(
        "Company",
        foreign_keys=[source_company_id],
        back_populates="company_connections_as_source",
    )
    target_company: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[target_company_id],
        back_populates="company_connections_as_target",
    )
    creator: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[created_by],
        post_update=True,
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("source_user_id", "target_company_id", name="unique_user_company_connection"),
        UniqueConstraint("source_company_id", "target_company_id", name="unique_company_connection"),
    )

    def __repr__(self) -> str:
        if self.source_type == "user":
            return f"<CompanyConnection(user={self.source_user_id} → company={self.target_company_id}, active={self.is_active})>"
        return f"<CompanyConnection(company={self.source_company_id} → company={self.target_company_id}, active={self.is_active})>"

    @property
    def source_display_name(self) -> str:
        """Get display name for source entity."""
        if self.source_type == "user" and self.source_user:
            return self.source_user.full_name
        if self.source_type == "company" and self.source_company:
            return self.source_company.name
        return "Unknown"

    @property
    def is_user_to_company(self) -> bool:
        """Check if this is a user-to-company connection."""
        return self.source_type == "user"

    @property
    def is_company_to_company(self) -> bool:
        """Check if this is a company-to-company connection."""
        return self.source_type == "company"
