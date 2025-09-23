from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.constants import TodoStatus, TodoVisibility


class TodoBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    notes: str | None = None
    priority: str | None = Field(default=None, max_length=20)
    due_date: datetime | None = None
    status: str | None = Field(default=TodoStatus.PENDING.value)
    assigned_user_id: int | None = None
    visibility: str | None = Field(default=TodoVisibility.PRIVATE.value)
    viewer_ids: list[int] | None = None

    @field_validator("due_date", mode="before")
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime format for due_date") from exc
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str:
        if value is None:
            return TodoStatus.PENDING.value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: str | None) -> str:
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


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    notes: str | None = None
    priority: str | None = Field(default=None, max_length=20)
    due_date: datetime | None = None
    status: str | None = None
    assigned_user_id: int | None = None
    visibility: str | None = None
    viewer_ids: list[int] | None = None

    @field_validator("due_date", mode="before")
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime format for due_date") from exc
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

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

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: str | None) -> str | None:
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
    assigned_user_id: int | None = None
    title: str
    description: str | None = None
    notes: str | None = None
    status: str
    priority: str | None = None
    visibility: str
    due_date: datetime | None = None
    completed_at: datetime | None = None
    expired_at: datetime | None = None
    is_deleted: bool
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    is_expired: bool


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
    assigned_user_id: int | None = None
    visibility: str | None = None

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: str | None) -> str | None:
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
    assigned_user: AssignableUser | None = None
    viewers: list[TodoViewer] | None = None


class TodoExtensionValidation(BaseModel):
    """Validation response for todo extension requests."""
    model_config = ConfigDict(from_attributes=True)
    
    can_request_extension: bool
    max_allowed_due_date: datetime | None = None
    days_extension_allowed: int = 3
    reason: str | None = None  # Reason why extension cannot be requested
