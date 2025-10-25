from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.utils.constants import (
    TodoPriority,
    TodoPublishStatus,
    TodoStatus,
    TodoType,
    VisibilityStatus,
)


class TodoBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    assignee_memo: str | None = None
    priority: str | None = Field(default=TodoPriority.MID.value)
    # Due datetime in UTC (will be converted from user's local timezone on input)
    due_datetime: datetime | None = None
    status: str | None = Field(default=TodoStatus.PENDING.value)
    workflow_id: int | None = None

    # Assignment workflow fields
    todo_type: str | None = Field(default=TodoType.REGULAR.value)
    publish_status: str | None = Field(default=TodoPublishStatus.PUBLISHED.value)
    assignee_id: int | None = None
    visibility_status: str | None = None
    assignment_assessment: str | None = None
    assignment_score: int | None = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is None:
            return TodoPriority.MID.value
        allowed = {priority.value for priority in TodoPriority}
        if value not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str:
        if value is None:
            return TodoStatus.PENDING.value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Title is required")
        return value.strip()

    @field_validator("todo_type")
    @classmethod
    def validate_todo_type(cls, value: str | None) -> str:
        if value is None:
            return TodoType.REGULAR.value
        allowed = {todo_type.value for todo_type in TodoType}
        if value not in allowed:
            raise ValueError(f"Todo type must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("publish_status")
    @classmethod
    def validate_publish_status(cls, value: str | None) -> str:
        if value is None:
            return TodoPublishStatus.PUBLISHED.value
        allowed = {status.value for status in TodoPublishStatus}
        if value not in allowed:
            raise ValueError(
                f"Publish status must be one of: {', '.join(sorted(allowed))}"
            )
        return value

    @field_validator("visibility_status")
    @classmethod
    def validate_visibility_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {status.value for status in VisibilityStatus}
        if value not in allowed:
            raise ValueError(
                f"Visibility status must be one of: {', '.join(sorted(allowed))}"
            )
        return value


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    assignee_memo: str | None = None
    priority: str | None = None
    # Due datetime in UTC (will be converted from user's local timezone on input)
    due_datetime: datetime | None = None
    status: str | None = None

    # Assignment workflow fields
    todo_type: str | None = None
    publish_status: str | None = None
    assignee_id: int | None = None
    visibility_status: str | None = None
    assignment_assessment: str | None = None
    assignment_score: int | None = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {priority.value for priority in TodoPriority}
        if value not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip() if value else value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_by: int | None = None
    last_updated_by: int | None = None
    title: str
    description: str | None = None
    assignee_memo: str | None = None
    viewer_memo: str | None = None  # Private memo for current viewer
    status: str
    priority: str | None = None
    # Due datetime stored in UTC, serialized with timezone info
    due_datetime: datetime | None = None
    completed_at: datetime | None = None
    expired_at: datetime | None = None
    is_deleted: bool
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    is_expired: bool

    # Assignment workflow fields
    todo_type: str
    publish_status: str
    assignee_id: int | None = None
    visibility_status: str | None = None
    assignment_assessment: str | None = None
    assignment_score: int | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None

    @field_serializer(
        "due_datetime",
        "completed_at",
        "expired_at",
        "deleted_at",
        "created_at",
        "updated_at",
        "submitted_at",
        "reviewed_at",
    )
    def serialize_datetime(self, dt: datetime | None, _info) -> str | None:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        # Serialize to ISO format
        return dt.isoformat()


class TodoListResponse(BaseModel):
    items: list[TodoRead]
    total: int


class TodoStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value


class TodoExtensionValidation(BaseModel):
    """Validation response for todo extension requests."""

    model_config = ConfigDict(from_attributes=True)

    can_request_extension: bool
    max_allowed_due_date: datetime | None = None
    days_extension_allowed: int = 3
    reason: str | None = None  # Reason why extension cannot be requested

    @field_serializer("max_allowed_due_date")
    def serialize_datetime(self, dt: datetime | None, _info) -> str | None:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        # Serialize to ISO format
        return dt.isoformat()


# Assignment workflow schemas
class TodoPublishUpdate(BaseModel):
    """Update publish status of a todo."""

    publish_status: str

    @field_validator("publish_status")
    @classmethod
    def validate_publish_status(cls, value: str) -> str:
        allowed = {status.value for status in TodoPublishStatus}
        if value not in allowed:
            raise ValueError(
                f"Publish status must be one of: {', '.join(sorted(allowed))}"
            )
        return value


class AssignmentSubmission(BaseModel):
    """Submit an assignment for review."""

    assignee_memo: str | None = None  # Optional submission notes


class AssignmentReview(BaseModel):
    """Review an assignment and provide assessment."""

    approved: bool
    assessment: str | None = None
    score: int | None = Field(default=None, ge=0, le=100)


class AssignmentWorkflowResponse(BaseModel):
    """Response for assignment workflow actions."""

    success: bool
    message: str
    todo: TodoRead | None = None


class UserInfo(BaseModel):
    """Basic user information for relationships."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
