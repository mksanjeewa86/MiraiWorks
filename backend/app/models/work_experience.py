"""Work Experience model for user profiles."""

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProfileWorkExperience(BaseModel):
    """Work experience entries for user profiles."""

    __tablename__ = "profile_work_experiences"
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Company Information
    company_name = Column(String(255), nullable=False)
    company_logo_url = Column(String(500), nullable=True)

    # Position Information
    position_title = Column(String(255), nullable=False)
    employment_type = Column(String(50), nullable=True)  # Full-time, Part-time, Contract, etc.
    location = Column(String(255), nullable=True)

    # Duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL if current position
    is_current = Column(Boolean, default=False, nullable=False)

    # Description
    description = Column(Text, nullable=True)

    # Skills used (stored as comma-separated values for now, could be normalized later)
    skills = Column(Text, nullable=True)

    # Display Order
    display_order = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="work_experiences")

    def __repr__(self):
        return f"<WorkExperience(id={self.id}, user_id={self.user_id}, company='{self.company_name}', position='{self.position_title}')>"
