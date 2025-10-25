"""Project schemas for API validation and serialization."""

from datetime import date

from pydantic import BaseModel, Field


# Base schema
class ProjectBase(BaseModel):
    """Base project schema with common fields."""

    project_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    role: str | None = Field(None, max_length=100)
    technologies: str | None = None  # Comma-separated list
    project_url: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=500)
    image_urls: str | None = None  # Comma-separated list of image URLs
    start_date: date | None = None
    end_date: date | None = None  # NULL if ongoing
    display_order: int = 0


# Create schema (for POST requests)
class ProjectCreate(ProjectBase):
    """Schema for creating a new project entry."""

    pass


# Update schema (for PUT/PATCH requests)
class ProjectUpdate(BaseModel):
    """Schema for updating an existing project entry."""

    project_name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    role: str | None = Field(None, max_length=100)
    technologies: str | None = None
    project_url: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=500)
    image_urls: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    display_order: int | None = None


# Response schema (what API returns)
class ProjectInfo(ProjectBase):
    """Schema for project information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
