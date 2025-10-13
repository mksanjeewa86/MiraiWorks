"""Question bank schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exam import QuestionType


class QuestionBankItemBase(BaseModel):
    """Base schema for question bank item."""

    question_text: str = Field(..., min_length=1)
    question_type: QuestionType
    order_index: int = Field(0, ge=0)
    points: float = Field(1.0, ge=0)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard)$")
    options: dict[str, str] | None = None  # {"A": "Option 1", "B": "Option 2"}
    correct_answers: list[str] | None = None  # ["A"] or ["A", "B"]
    explanation: str | None = None
    tags: list[str] | None = None
    max_length: int | None = Field(None, ge=1, le=10000)
    min_length: int | None = Field(None, ge=0)
    rating_scale: int | None = Field(None, ge=2, le=10)


class QuestionBankItemCreate(QuestionBankItemBase):
    """Schema for creating question bank item."""

    pass


class QuestionBankItemUpdate(BaseModel):
    """Schema for updating question bank item."""

    question_text: str | None = Field(None, min_length=1)
    question_type: QuestionType | None = None
    order_index: int | None = Field(None, ge=0)
    points: float | None = Field(None, ge=0)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard)$")
    options: dict[str, str] | None = None
    correct_answers: list[str] | None = None
    explanation: str | None = None
    tags: list[str] | None = None
    max_length: int | None = Field(None, ge=1, le=10000)
    min_length: int | None = Field(None, ge=0)
    rating_scale: int | None = Field(None, ge=2, le=10)


class QuestionBankItemInfo(QuestionBankItemBase):
    """Schema for question bank item information."""

    id: int
    bank_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionBankBase(BaseModel):
    """Base schema for question bank."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    exam_type: str = Field(..., min_length=1, max_length=50)
    category: str | None = Field(None, max_length=100)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard|mixed)$")
    is_public: bool = False


class QuestionBankCreate(QuestionBankBase):
    """Schema for creating question bank."""

    company_id: int | None = None  # NULL = global bank (system admin only)
    questions: list[QuestionBankItemCreate] = []


class QuestionBankUpdate(BaseModel):
    """Schema for updating question bank."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    exam_type: str | None = Field(None, min_length=1, max_length=50)
    category: str | None = Field(None, max_length=100)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard|mixed)$")
    is_public: bool | None = None


class QuestionBankInfo(QuestionBankBase):
    """Schema for question bank information."""

    id: int
    company_id: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Additional computed fields
    question_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


class QuestionBankDetail(QuestionBankInfo):
    """Schema for detailed question bank with questions."""

    questions: list[QuestionBankItemInfo] = []

    model_config = ConfigDict(from_attributes=True)


class QuestionBankListResponse(BaseModel):
    """Response schema for listing question banks."""

    banks: list[QuestionBankInfo]
    total: int
    page: int
    page_size: int
    has_more: bool


class TemplateQuestionSelection(BaseModel):
    """Configuration for selecting questions from a question bank."""

    bank_id: int
    count: int = Field(..., ge=1, le=100, description="Number of questions to select")
    category: str | None = Field(None, description="Filter by category")
    difficulty: str | None = Field(
        None, pattern="^(easy|medium|hard)$", description="Filter by difficulty"
    )
    tags: list[str] | None = Field(None, description="Filter by tags")


class QuestionBankStats(BaseModel):
    """Statistics for a question bank."""

    bank_id: int
    total_questions: int
    questions_by_type: dict[str, int]
    questions_by_difficulty: dict[str, int]
    average_points: float
    tags_used: list[str]
    times_used_in_exams: int
