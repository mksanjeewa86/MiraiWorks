from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DashboardStats(BaseModel):
    total_users: int | None = 0
    total_companies: int | None = 0
    total_interviews: int | None = 0
    total_resumes: int | None = 0
    active_conversations: int | None = 0


class ActivityItem(BaseModel):
    id: str
    type: str  # 'interview' | 'message' | 'resume' | 'user' | 'company'
    title: str
    description: str
    timestamp: datetime
    user_id: int | None = None
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
