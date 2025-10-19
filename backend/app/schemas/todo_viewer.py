"""Schemas for Todo Viewer functionality."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_serializer


class UserInfo(BaseModel):
    """Basic user information for relationships."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str


class TodoViewerCreate(BaseModel):
    """Schema for adding a viewer to a todo."""

    user_id: int


class TodoViewerRead(BaseModel):
    """Schema for reading viewer information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    todo_id: int
    user_id: int
    added_by: int | None
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime | None, _info) -> str | None:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Serialize to ISO format
        return dt.isoformat()


class TodoViewerWithUser(TodoViewerRead):
    """Schema for viewer with user details (for creator view only)."""

    user: UserInfo


class TodoViewerListResponse(BaseModel):
    """Response schema for list of viewers."""

    items: list[TodoViewerWithUser]
    total: int
