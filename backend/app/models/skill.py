"""Skill model for user profiles."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProfileSkill(BaseModel):
    """Skill entries for user profiles."""

    __tablename__ = "profile_skills"
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Skill Information
    skill_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # Technical, Soft, Language, Tool, etc.

    # Proficiency Level
    proficiency_level = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced, Expert

    # Years of Experience (optional)
    years_of_experience = Column(Integer, nullable=True)

    # Endorsements (for future use)
    endorsement_count = Column(Integer, default=0, nullable=False)

    # Display Order
    display_order = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="skills")

    def __repr__(self):
        return f"<Skill(id={self.id}, user_id={self.user_id}, skill='{self.skill_name}', proficiency='{self.proficiency_level}')>"
