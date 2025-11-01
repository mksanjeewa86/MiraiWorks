"""Certification model for user profiles."""

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ProfileCertification(BaseModel):
    """Certification entries for user profiles."""

    __tablename__ = "profile_certifications"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Certification Information
    certification_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_organization: Mapped[str] = mapped_column(String(255), nullable=False)

    # Dates
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    does_not_expire: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Credential Information
    credential_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Badge/Certificate Image
    certificate_image_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Display Order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="certifications")

    def __repr__(self):
        return f"<Certification(id={self.id}, user_id={self.user_id}, name='{self.certification_name}', issuer='{self.issuing_organization}')>"
