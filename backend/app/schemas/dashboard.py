from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_users: Optional[int] = 0
    total_companies: Optional[int] = 0
    total_interviews: Optional[int] = 0
    total_resumes: Optional[int] = 0
    active_conversations: Optional[int] = 0


class ActivityItem(BaseModel):
    id: str
    type: str  # 'interview' | 'message' | 'resume' | 'user' | 'company'
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True
