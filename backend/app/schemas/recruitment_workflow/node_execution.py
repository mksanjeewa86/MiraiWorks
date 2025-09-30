from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.recruitment_workflow.enums import ExecutionStatus, ExecutionResult


class NodeExecutionBase(BaseModel):
    """Base schema for node execution"""
    feedback: Optional[str] = Field(None, description="Feedback for the execution")
    assessor_notes: Optional[str] = Field(None, description="Internal notes from assessor")


class NodeExecutionCreate(NodeExecutionBase):
    """Schema for creating a node execution"""
    candidate_process_id: int = Field(..., description="Candidate process ID")
    node_id: int = Field(..., description="Process node ID")
    assigned_to: Optional[int] = Field(None, description="User ID to assign this execution to")
    due_date: Optional[datetime] = Field(None, description="Due date for completion")


class NodeExecutionUpdate(BaseModel):
    """Schema for updating a node execution"""
    status: Optional[ExecutionStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    feedback: Optional[str] = None
    assessor_notes: Optional[str] = None


class NodeExecutionCompletion(BaseModel):
    """Schema for completing a node execution"""
    result: ExecutionResult = Field(..., description="Execution result")
    score: Optional[float] = Field(None, ge=0, le=100, description="Score (0-100)")
    feedback: Optional[str] = Field(None, max_length=2000, description="Feedback for the candidate")
    assessor_notes: Optional[str] = Field(None, max_length=2000, description="Internal assessor notes")
    execution_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional execution data")

    @validator('score')
    def validate_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Score must be between 0 and 100")
        return v


class NodeExecutionFailure(BaseModel):
    """Schema for failing a node execution"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for failure")
    allow_retry: bool = Field(False, description="Whether to allow retry")
    retry_instructions: Optional[str] = Field(None, max_length=1000, description="Instructions for retry")


class NodeExecutionSkip(BaseModel):
    """Schema for skipping a node execution"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for skipping")
    notify_stakeholders: bool = Field(True, description="Whether to notify relevant stakeholders")


class NodeExecutionSchedule(BaseModel):
    """Schema for scheduling a node execution"""
    due_date: datetime = Field(..., description="Due date for the execution")
    assigned_to: Optional[int] = Field(None, description="User to assign the execution to")
    send_notification: bool = Field(True, description="Whether to send notification")
    custom_instructions: Optional[str] = Field(None, max_length=1000, description="Custom instructions")


class NodeExecutionInfo(NodeExecutionBase):
    """Schema for node execution information"""
    id: int
    candidate_process_id: int
    node_id: int
    status: ExecutionStatus
    result: Optional[ExecutionResult]
    score: Optional[float]
    execution_data: Optional[Dict[str, Any]]
    interview_id: Optional[int]
    todo_id: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
    assigned_to: Optional[int]
    completed_by: Optional[int]
    reviewed_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    duration_minutes: Optional[int] = Field(None, description="Execution duration in minutes")
    is_overdue: Optional[bool] = Field(None, description="Whether the execution is overdue")

    class Config:
        from_attributes = True


class NodeExecutionDetails(NodeExecutionInfo):
    """Detailed schema for node execution with relationships"""
    # Node information
    node_title: Optional[str] = Field(None, description="Title of the associated node")
    node_type: Optional[str] = Field(None, description="Type of the associated node")
    node_sequence_order: Optional[int] = Field(None, description="Sequence order of the node")

    # Actor information
    assignee_name: Optional[str] = Field(None, description="Name of assigned user")
    completer_name: Optional[str] = Field(None, description="Name of user who completed")
    reviewer_name: Optional[str] = Field(None, description="Name of reviewer")

    # Linked resource information
    interview_title: Optional[str] = Field(None, description="Title of linked interview")
    interview_status: Optional[str] = Field(None, description="Status of linked interview")
    todo_title: Optional[str] = Field(None, description="Title of linked todo")
    todo_status: Optional[str] = Field(None, description="Status of linked todo")


class NodeExecutionTimeline(BaseModel):
    """Schema for execution timeline/history"""
    execution_id: int
    timeline_events: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutionTimelineEvent(BaseModel):
    """Schema for individual timeline events"""
    timestamp: datetime
    event_type: str  # created, assigned, started, updated, completed, failed, etc.
    actor_id: Optional[int]
    actor_name: Optional[str]
    description: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BulkExecutionUpdate(BaseModel):
    """Schema for bulk updating executions"""
    execution_ids: List[int] = Field(..., min_items=1, description="List of execution IDs to update")
    status: Optional[ExecutionStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

    @validator('execution_ids')
    def validate_execution_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate execution IDs are not allowed")
        return v


class ExecutionBatchCompletion(BaseModel):
    """Schema for batch completing executions"""
    completions: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="List of {execution_id, result, score, feedback} objects"
    )

    @validator('completions')
    def validate_completions(cls, v):
        execution_ids = [c.get('execution_id') for c in v]
        if len(execution_ids) != len(set(execution_ids)):
            raise ValueError("Duplicate execution IDs in batch completion")

        for completion in v:
            if 'execution_id' not in completion or 'result' not in completion:
                raise ValueError("Each completion must have execution_id and result")

        return v


class ExecutionStatistics(BaseModel):
    """Schema for execution statistics"""
    total_executions: int
    by_status: Dict[str, int]
    by_result: Dict[str, int]
    average_duration_minutes: float
    completion_rate: float
    on_time_completion_rate: float


class NodeExecutionMetrics(BaseModel):
    """Schema for node-specific execution metrics"""
    node_id: int
    node_title: str
    node_type: str
    total_executions: int
    completed_executions: int
    failed_executions: int
    average_duration_minutes: float
    completion_rate: float
    average_score: Optional[float]
    bottleneck_score: float  # How much this node slows down the process


class ExecutionWorkload(BaseModel):
    """Schema for execution workload by assignee"""
    assignee_id: int
    assignee_name: str
    pending_executions: int
    in_progress_executions: int
    overdue_executions: int
    completed_this_week: int
    average_completion_time_hours: float
    workload_score: float  # Relative workload compared to other assignees