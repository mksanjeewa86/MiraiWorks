from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer


class TodoViewerMemoBase(BaseModel):
    memo: Optional[str] = None


class TodoViewerMemoCreate(TodoViewerMemoBase):
    pass


class TodoViewerMemoUpdate(TodoViewerMemoBase):
    pass


class TodoViewerMemoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    todo_id: int
    user_id: int
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Serialize to ISO format
        return dt.isoformat()
