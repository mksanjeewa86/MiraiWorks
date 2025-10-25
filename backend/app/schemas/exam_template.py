"""Exam template schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExamTemplateBase(BaseModel):
    """Base schema for exam template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    exam_type: str
    time_limit_minutes: int | None = Field(None, gt=0)
    max_attempts: int = Field(1, gt=0)
    passing_score: float | None = Field(None, ge=0, le=100)
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_score: bool = True
    show_correct_answers: bool = False
    show_results_immediately: bool = True
    enable_monitoring: bool = False
    enable_face_recognition: bool = False
    require_full_screen: bool = False
    is_public: bool = False
    category: str | None = None
    tags: str | None = None


class ExamTemplateCreate(ExamTemplateBase):
    """Schema for creating exam template."""

    questions_template: list[dict[str, Any]] | None = None
    company_id: int | None = None


class ExamTemplateUpdate(BaseModel):
    """Schema for updating exam template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    exam_type: str | None = None
    time_limit_minutes: int | None = Field(None, gt=0)
    max_attempts: int | None = Field(None, gt=0)
    passing_score: float | None = Field(None, ge=0, le=100)
    shuffle_questions: bool | None = None
    shuffle_options: bool | None = None
    show_score: bool | None = None
    show_correct_answers: bool | None = None
    show_results_immediately: bool | None = None
    enable_monitoring: bool | None = None
    enable_face_recognition: bool | None = None
    require_full_screen: bool | None = None
    questions_template: list[dict[str, Any]] | None = None
    is_public: bool | None = None
    category: str | None = None
    tags: str | None = None


class ExamTemplateInfo(ExamTemplateBase):
    """Schema for exam template information."""

    id: int
    created_by_id: int
    company_id: int | None = None
    questions_template: dict[str, Any] | None = None
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
