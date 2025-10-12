"""Project schemas for API validation and serialization."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# Base schema
class ProjectBase(BaseModel):
    """Base project schema with common fields."""

    project_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    role: Optional[str] = Field(None, max_length=100)
    technologies: Optional[str] = None  # Comma-separated list
    project_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    image_urls: Optional[str] = None  # Comma-separated list of image URLs
    start_date: Optional[date] = None
    end_date: Optional[date] = None  # NULL if ongoing
    display_order: int = 0


# Create schema (for POST requests)
class ProjectCreate(ProjectBase):
    """Schema for creating a new project entry."""

    pass


# Update schema (for PUT/PATCH requests)
class ProjectUpdate(BaseModel):
    """Schema for updating an existing project entry."""

    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    role: Optional[str] = Field(None, max_length=100)
    technologies: Optional[str] = None
    project_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    image_urls: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    display_order: Optional[int] = None


# Response schema (what API returns)
class ProjectInfo(ProjectBase):
    """Schema for project information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
