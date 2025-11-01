"""Project model for user profiles."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ProfileProject(BaseModel):
    """Project entries for user profiles."""

    __tablename__ = "profile_projects"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Project Information
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Role Information
    role: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # Developer, Designer, Project Manager, etc.

    # Technologies Used (stored as comma-separated values for now)
    technologies: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Links
    project_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Project Images (stored as comma-separated URLs for now)
    image_urls: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Duration
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Display Order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, user_id={self.user_id}, name='{self.project_name}', role='{self.role}')>"
