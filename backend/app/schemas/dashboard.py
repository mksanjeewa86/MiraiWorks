from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class DashboardStats(BaseModel):
    total_users: Optional[int] = 0
    total_companies: Optional[int] = 0
    total_interviews: Optional[int] = 0
    total_resumes: Optional[int] = 0
    active_conversations: Optional[int] = 0
    total_exams: Optional[int] = 0
    total_exam_assignments: Optional[int] = 0
    total_exam_sessions: Optional[int] = 0
    completed_exam_sessions: Optional[int] = 0
    avg_exam_score: Optional[float] = None


class ActivityItem(BaseModel):
    id: str
    type: str  # 'interview' | 'message' | 'resume' | 'user' | 'company' | 'exam'
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[int] = None
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
