from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InterviewNoteBase(BaseModel):
    """Base schema for interview notes."""
    content: Optional[str] = Field(None, description="Private note content")


class InterviewNoteCreate(InterviewNoteBase):
    """Schema for creating interview notes."""
    pass


class InterviewNoteUpdate(InterviewNoteBase):
    """Schema for updating interview notes."""
    pass


class InterviewNoteInfo(InterviewNoteBase):
    """Schema for interview note information."""
    id: int
    interview_id: int
    participant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)