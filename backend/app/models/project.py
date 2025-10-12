"""Project model for user profiles."""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import TimestampMixin
from app.database import Base


class ProfileProject(Base, TimestampMixin):
    """Project entries for user profiles."""

    __tablename__ = "profile_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Project Information
    project_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Role Information
    role = Column(String(100), nullable=True)  # Developer, Designer, Project Manager, etc.

    # Technologies Used (stored as comma-separated values for now)
    technologies = Column(Text, nullable=True)

    # Links
    project_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)

    # Project Images (stored as comma-separated URLs for now)
    image_urls = Column(Text, nullable=True)

    # Duration
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # NULL if ongoing

    # Display Order
    display_order = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, user_id={self.user_id}, name='{self.project_name}', role='{self.role}')>"
