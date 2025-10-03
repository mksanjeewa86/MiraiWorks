from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.constants import (
    AssignmentStatus,
    TodoPublishStatus,
    TodoStatus,
    TodoType,
    TodoVisibility,
)


class TodoBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = Field(default=None, max_length=20)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(default=TodoStatus.PENDING.value)
    assigned_user_id: Optional[int] = None
    visibility: Optional[str] = Field(default=TodoVisibility.PRIVATE.value)
    viewer_ids: list[int] | None = None
    workflow_id: Optional[int] = None

    # Assignment workflow fields
    todo_type: Optional[str] = Field(default=TodoType.REGULAR.value)
    publish_status: Optional[str] = Field(default=TodoPublishStatus.PUBLISHED.value)
    assignment_status: Optional[str] = None
    assignment_assessment: Optional[str] = None
    assignment_score: Optional[int] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def ensure_timezone(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime format for due_date") from exc
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> str:
        if value is None:
            return TodoStatus.PENDING.value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: Optional[str]) -> str:
        if value is None:
            return TodoVisibility.PRIVATE.value
        allowed = {visibility.value for visibility in TodoVisibility}
        if value not in allowed:
            raise ValueError(f"Visibility must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Title is required")
        return value.strip()

    @field_validator("todo_type")
    @classmethod
    def validate_todo_type(cls, value: Optional[str]) -> str:
        if value is None:
            return TodoType.REGULAR.value
        allowed = {todo_type.value for todo_type in TodoType}
        if value not in allowed:
            raise ValueError(f"Todo type must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("publish_status")
    @classmethod
    def validate_publish_status(cls, value: Optional[str]) -> str:
        if value is None:
            return TodoPublishStatus.PUBLISHED.value
        allowed = {status.value for status in TodoPublishStatus}
        if value not in allowed:
            raise ValueError(f"Publish status must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("assignment_status")
    @classmethod
    def validate_assignment_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {status.value for status in AssignmentStatus}
        if value not in allowed:
            raise ValueError(f"Assignment status must be one of: {', '.join(sorted(allowed))}")
        return value


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = Field(default=None, max_length=20)
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    assigned_user_id: Optional[int] = None
    visibility: Optional[str] = None
    viewer_ids: list[int] | None = None

    # Assignment workflow fields
    todo_type: Optional[str] = None
    publish_status: Optional[str] = None
    assignment_status: Optional[str] = None
    assignment_assessment: Optional[str] = None
    assignment_score: Optional[int] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def ensure_timezone(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime format for due_date") from exc
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip() if value else value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {visibility.value for visibility in TodoVisibility}
        if value not in allowed:
            raise ValueError(f"Visibility must be one of: {', '.join(sorted(allowed))}")
        return value


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_by: Optional[int] = None  # Add created_by field
    last_updated_by: Optional[int] = None  # Add last_updated_by field
    assigned_user_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    status: str
    priority: Optional[str] = None
    visibility: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_expired: bool

    # Assignment workflow fields
    todo_type: str
    publish_status: str
    assignment_status: Optional[str] = None
    assignment_assessment: Optional[str] = None
    assignment_score: Optional[int] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None


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


class TodoAssignmentUpdate(BaseModel):
    assigned_user_id: Optional[int] = None
    visibility: Optional[str] = None

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {visibility.value for visibility in TodoVisibility}
        if value not in allowed:
            raise ValueError(f"Visibility must be one of: {', '.join(sorted(allowed))}")
        return value


class AssignableUser(BaseModel):
    """User that can be assigned to todos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class TodoViewer(BaseModel):
    """Todo viewer information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    todo_id: int
    added_at: datetime
    user: AssignableUser


class TodoViewersUpdate(BaseModel):
    """Update viewers for a todo."""
    viewer_ids: list[int]


class TodoWithAssignedUser(TodoRead):
    """Todo with assigned user information."""
    assigned_user: Optional[AssignableUser] = None
    viewers: list[TodoViewer] | None = None


class TodoExtensionValidation(BaseModel):
    """Validation response for todo extension requests."""
    model_config = ConfigDict(from_attributes=True)

    can_request_extension: bool
    max_allowed_due_date: Optional[datetime] = None
    days_extension_allowed: int = 3
    reason: Optional[str] = None  # Reason why extension cannot be requested


# Assignment workflow schemas
class TodoPublishUpdate(BaseModel):
    """Update publish status of a todo."""
    publish_status: str

    @field_validator("publish_status")
    @classmethod
    def validate_publish_status(cls, value: str) -> str:
        allowed = {status.value for status in TodoPublishStatus}
        if value not in allowed:
            raise ValueError(f"Publish status must be one of: {', '.join(sorted(allowed))}")
        return value


class AssignmentSubmission(BaseModel):
    """Submit an assignment for review."""
    notes: Optional[str] = None  # Optional submission notes


class AssignmentReview(BaseModel):
    """Review an assignment and provide assessment."""
    assignment_status: str
    assessment: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=0, le=100)

    @field_validator("assignment_status")
    @classmethod
    def validate_assignment_status(cls, value: str) -> str:
        allowed = {AssignmentStatus.APPROVED.value, AssignmentStatus.REJECTED.value}
        if value not in allowed:
            raise ValueError("Assignment status for review must be either 'approved' or 'rejected'")
        return value


class AssignmentWorkflowResponse(BaseModel):
    """Response for assignment workflow actions."""
    success: bool
    message: str
    todo: Optional[TodoRead] = None
