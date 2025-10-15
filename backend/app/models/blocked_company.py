"""
Blocked Company Model

Allows candidates to block specific companies from:
- Searching/viewing their profile
- Receiving recommendations for these companies
- Being contacted by recruiters from these companies
"""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company import Company


class BlockedCompany(BaseModel):
    """
    Model for companies blocked by candidates.

    Candidates can block companies to prevent:
    - Company recruiters from viewing their profile
    - Receiving job recommendations from these companies
    - Being matched with positions from these companies
    """
    __tablename__ = "blocked_companies"

    # Foreign key to user (candidate)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Company identifier - can be either company_id (if exists in system) or company_name (free text)
    company_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Optional reason for blocking (for user's reference)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="blocked_companies")
    company: Mapped["Company"] = relationship("Company", foreign_keys=[company_id])

    # Indexes for performance
    __table_args__ = (
        Index("ix_blocked_companies_user_id", "user_id"),
        Index("ix_blocked_companies_company_id", "company_id"),
        Index("ix_blocked_companies_company_name", "company_name"),
        # Unique constraint to prevent duplicate blocks
        Index("ix_blocked_companies_user_company", "user_id", "company_id", unique=True),
    )

    def __repr__(self):
        company_identifier = f"company_id={self.company_id}" if self.company_id else f"company_name={self.company_name}"
        return f"<BlockedCompany(user_id={self.user_id}, {company_identifier})>"
