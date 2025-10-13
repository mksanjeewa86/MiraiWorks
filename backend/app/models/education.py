"""Education model for user profiles."""

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProfileEducation(BaseModel):
    """Education entries for user profiles."""

    __tablename__ = "profile_educations"
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Institution Information
    institution_name = Column(String(255), nullable=False)
    institution_logo_url = Column(String(500), nullable=True)

    # Degree Information
    degree_type = Column(String(100), nullable=False)  # Bachelor's, Master's, PhD, etc.
    field_of_study = Column(String(255), nullable=False)

    # Duration
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # NULL if currently enrolled
    graduation_year = Column(Integer, nullable=True)

    # Academic Performance
    gpa = Column(Numeric(3, 2), nullable=True)  # e.g., 3.85
    gpa_max = Column(Numeric(3, 2), nullable=True)  # e.g., 4.00

    # Additional Information
    honors_awards = Column(Text, nullable=True)  # Honors, awards, achievements
    description = Column(Text, nullable=True)  # Additional details

    # Display Order
    display_order = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="educations")

    def __repr__(self):
        return f"<Education(id={self.id}, user_id={self.user_id}, institution='{self.institution_name}', degree='{self.degree_type}')>"
