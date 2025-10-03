"""Company Follow model for candidate-to-company connections."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company import Company


class CompanyFollow(Base):
    """Instant candidate following of companies (no approval needed)."""

    __tablename__ = "company_follows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Candidate following the company
    candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Company being followed
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Follow status - instant, no approval needed
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Optional notification preferences
    notify_new_positions: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_company_updates: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_events: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    followed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    unfollowed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Relationships
    candidate: Mapped["User"] = relationship(
        "User",
        foreign_keys=[candidate_id],
        back_populates="followed_companies"
    )
    company: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[company_id],
        back_populates="followers"
    )

    # Ensure no duplicate follows
    __table_args__ = (
        UniqueConstraint('candidate_id', 'company_id', name='unique_candidate_company_follow'),
    )

    def __repr__(self) -> str:
        return f"<CompanyFollow(candidate_id={self.candidate_id}, company_id={self.company_id}, active={self.is_active})>"

    def unfollow(self):
        """Mark this follow relationship as inactive."""
        self.is_active = False
        self.unfollowed_at = datetime.utcnow()

    def refollow(self):
        """Reactivate this follow relationship."""
        self.is_active = True
        self.unfollowed_at = None