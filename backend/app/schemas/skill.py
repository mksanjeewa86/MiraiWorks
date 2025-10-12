"""Skill schemas for API validation and serialization."""

from typing import Optional

from pydantic import BaseModel, Field


# Enums
class SkillCategory:
    """Skill category constants."""

    TECHNICAL = "Technical"
    SOFT_SKILL = "Soft Skill"
    LANGUAGE = "Language"
    TOOL = "Tool"
    FRAMEWORK = "Framework"
    OTHER = "Other"


class ProficiencyLevel:
    """Proficiency level constants."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    NATIVE = "Native"  # For languages


# Base schema
class SkillBase(BaseModel):
    """Base skill schema with common fields."""

    skill_name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    proficiency_level: Optional[str] = Field(None, max_length=50)
    years_of_experience: Optional[int] = Field(None, ge=0, le=100)
    endorsement_count: int = 0
    display_order: int = 0


# Create schema (for POST requests)
class SkillCreate(SkillBase):
    """Schema for creating a new skill entry."""

    pass


# Update schema (for PUT/PATCH requests)
class SkillUpdate(BaseModel):
    """Schema for updating an existing skill entry."""

    skill_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    proficiency_level: Optional[str] = Field(None, max_length=50)
    years_of_experience: Optional[int] = Field(None, ge=0, le=100)
    endorsement_count: Optional[int] = Field(None, ge=0)
    display_order: Optional[int] = None


# Response schema (what API returns)
class SkillInfo(SkillBase):
    """Schema for skill information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
