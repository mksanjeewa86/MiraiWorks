from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.recruitment_workflow.candidate_process import CandidateProcessInfo
from app.schemas.recruitment_workflow.enums import ProcessStatus
from app.schemas.recruitment_workflow.process_node import ProcessNodeInfo
from app.schemas.recruitment_workflow.process_viewer import ProcessViewerInfo


class RecruitmentProcessBase(BaseModel):
    """Base schema for recruitment process"""

    name: str = Field(..., min_length=1, max_length=255, description="Process name")
    description: Optional[str] = Field(None, description="Process description")
    position_id: Optional[int] = Field(None, description="Associated position ID")
    settings: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Process settings"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v.strip()


class RecruitmentProcessCreate(RecruitmentProcessBase):
    """Schema for creating a recruitment process"""

    is_template: bool = Field(False, description="Whether this is a template")
    template_name: Optional[str] = Field(
        None, max_length=255, description="Template name if is_template=True"
    )

    @field_validator("template_name")
    @classmethod
    def validate_template_name(cls, v, info):
        if info.data.get("is_template") and not v:
            raise ValueError("Template name is required when creating a template")
        if v:
            return v.strip()
        return v


class RecruitmentProcessUpdate(BaseModel):
    """Schema for updating a recruitment process"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            return v.strip()
        return v


class RecruitmentProcessInfo(RecruitmentProcessBase):
    """Schema for recruitment process information"""

    id: int
    employer_company_id: int
    created_by: int
    updated_by: Optional[int]
    status: ProcessStatus
    version: int
    is_template: bool
    template_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime]
    archived_at: Optional[datetime]

    # Computed fields
    node_count: Optional[int] = Field(
        None, description="Number of nodes in the process"
    )
    active_candidate_count: Optional[int] = Field(
        None, description="Number of active candidates"
    )

    class Config:
        from_attributes = True


class RecruitmentProcessDetails(RecruitmentProcessInfo):
    """Detailed schema for recruitment process with relationships"""

    nodes: list[ProcessNodeInfo] = Field(default_factory=list)
    candidate_workflows: list[CandidateProcessInfo] = Field(default_factory=list)
    viewers: list[ProcessViewerInfo] = Field(default_factory=list)

    # Statistics
    completion_rate: Optional[float] = Field(
        None, description="Process completion rate"
    )
    average_duration_days: Optional[float] = Field(
        None, description="Average completion time in days"
    )


class ProcessActivation(BaseModel):
    """Schema for activating a process"""

    force_activate: bool = Field(
        False, description="Force activation even if validation fails"
    )


class ProcessArchive(BaseModel):
    """Schema for archiving a process"""

    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for archiving"
    )


class ProcessClone(BaseModel):
    """Schema for cloning a process"""

    new_name: str = Field(
        ..., min_length=1, max_length=255, description="Name for the cloned process"
    )
    clone_candidates: bool = Field(
        False, description="Whether to clone candidate assignments"
    )
    clone_viewers: bool = Field(True, description="Whether to clone viewers")

    @field_validator("new_name")
    @classmethod
    def validate_new_name(cls, v):
        return v.strip()


class ProcessTemplate(BaseModel):
    """Schema for creating a process template"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(
        None, max_length=100, description="Template category (e.g., engineering, sales)"
    )
    industry: Optional[str] = Field(
        None, max_length=100, description="Industry this template is for"
    )
    is_public: bool = Field(
        False, description="Whether this template is publicly available"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v.strip()


class ProcessTemplateInfo(ProcessTemplate):
    """Schema for process template information"""

    id: int
    created_by: int
    company_id: Optional[int]
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessStatistics(BaseModel):
    """Schema for process statistics"""

    total_processes: int
    active_processes: int
    draft_processes: int
    archived_processes: int
    total_candidates: int
    active_candidates: int
    completed_candidates: int
    average_completion_rate: float
    average_duration_days: float


class ProcessAnalytics(BaseModel):
    """Schema for detailed process analytics"""

    workflow_id: int
    process_name: str
    total_candidates: int
    completed_candidates: int
    failed_candidates: int
    withdrawn_candidates: int
    completion_rate: float
    average_duration_days: float
    node_statistics: list[dict[str, Any]]
    bottleneck_nodes: list[dict[str, Any]]
    recruiter_workload: list[dict[str, Any]]
