"""Certification model for user profiles."""

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import TimestampMixin
from app.database import Base


class ProfileCertification(Base, TimestampMixin):
    """Certification entries for user profiles."""

    __tablename__ = "profile_certifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Certification Information
    certification_name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=False)

    # Dates
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)  # NULL if no expiry
    does_not_expire = Column(Boolean, default=False, nullable=False)

    # Credential Information
    credential_id = Column(String(255), nullable=True)
    credential_url = Column(String(500), nullable=True)

    # Badge/Certificate Image
    certificate_image_url = Column(String(500), nullable=True)

    # Description
    description = Column(Text, nullable=True)

    # Display Order
    display_order = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="certifications")

    def __repr__(self):
        return f"<Certification(id={self.id}, user_id={self.user_id}, name='{self.certification_name}', issuer='{self.issuing_organization}')>"
