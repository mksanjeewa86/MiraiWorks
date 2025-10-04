"""Exam template schemas."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExamTemplateBase(BaseModel):
    """Base schema for exam template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    exam_type: str
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    max_attempts: int = Field(1, gt=0)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_score: bool = True
    show_correct_answers: bool = False
    show_results_immediately: bool = True
    enable_monitoring: bool = False
    enable_face_recognition: bool = False
    require_full_screen: bool = False
    is_public: bool = False
    category: Optional[str] = None
    tags: Optional[str] = None


class ExamTemplateCreate(ExamTemplateBase):
    """Schema for creating exam template."""

    questions_template: Optional[list[dict[str, Any]]] = None
    company_id: Optional[int] = None


class ExamTemplateUpdate(BaseModel):
    """Schema for updating exam template."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    exam_type: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    max_attempts: Optional[int] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    show_score: Optional[bool] = None
    show_correct_answers: Optional[bool] = None
    show_results_immediately: Optional[bool] = None
    enable_monitoring: Optional[bool] = None
    enable_face_recognition: Optional[bool] = None
    require_full_screen: Optional[bool] = None
    questions_template: Optional[list[dict[str, Any]]] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class ExamTemplateInfo(ExamTemplateBase):
    """Schema for exam template information."""

    id: int
    created_by_id: int
    company_id: Optional[int] = None
    questions_template: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamTemplateListResponse(BaseModel):
    """Response schema for listing exam templates."""

    templates: list[ExamTemplateInfo]
    total: int
    page: int
    page_size: int
    has_more: bool
