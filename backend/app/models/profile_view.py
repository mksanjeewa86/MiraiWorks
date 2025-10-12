"""Profile View model for tracking who viewed profiles."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ProfileView(Base):
    """Track profile views for analytics."""

    __tablename__ = "profile_views"

    id = Column(Integer, primary_key=True, index=True)
    profile_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User whose profile was viewed",
    )
    viewer_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who viewed the profile (null for anonymous views)",
    )
    viewer_company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        comment="Company of the viewer",
    )
    viewer_ip = Column(String(45), nullable=True, comment="IP address of viewer")
    viewer_user_agent = Column(Text, nullable=True, comment="Browser/device info")
    view_duration = Column(Integer, nullable=True, comment="Duration of view in seconds")
    referrer = Column(String(500), nullable=True, comment="How they found the profile")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    profile_user = relationship(
        "User", foreign_keys=[profile_user_id], back_populates="profile_views_received"
    )
    viewer_user = relationship(
        "User", foreign_keys=[viewer_user_id], back_populates="profile_views_made"
    )

    def __repr__(self):
        return f"<ProfileView(id={self.id}, profile_user_id={self.profile_user_id}, viewer_user_id={self.viewer_user_id})>"
