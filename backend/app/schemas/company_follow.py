"""Company Follow schemas for candidate-to-company relationships."""

from datetime import datetime
from pydantic import BaseModel


class CompanyFollowBase(BaseModel):
    """Base schema for company follows."""
    notify_new_positions: bool = True
    notify_company_updates: bool = False
    notify_events: bool = False


class CompanyFollowCreate(CompanyFollowBase):
    """Schema for creating a company follow."""
    company_id: int


class CompanyFollowUpdate(BaseModel):
    """Schema for updating follow preferences."""
    notify_new_positions: bool | None = None
    notify_company_updates: bool | None = None
    notify_events: bool | None = None


class CompanyFollowInfo(CompanyFollowBase):
    """Schema for company follow information."""
    id: int
    candidate_id: int
    company_id: int
    is_active: bool
    followed_at: datetime
    unfollowed_at: datetime | None = None

    class Config:
        from_attributes = True


class CompanyFollowWithCompany(CompanyFollowInfo):
    """Schema for company follow with company details."""
    company: dict  # Basic company info

    class Config:
        from_attributes = True


class CompanyFollowWithCandidate(CompanyFollowInfo):
    """Schema for company follow with candidate details."""
    candidate: dict  # Basic candidate info

    class Config:
        from_attributes = True