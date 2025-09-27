"""Schemas for MBTI personality test."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.constants import MBTITestStatus, MBTIType


class MBTIQuestionRead(BaseModel):
    """Schema for reading MBTI test questions."""

    id: int
    question_number: int
    dimension: str
    question_text_en: str
    question_text_ja: str
    option_a_en: str
    option_a_ja: str
    option_b_en: str
    option_b_ja: str

    model_config = ConfigDict(from_attributes=True)


class MBTIAnswerSubmit(BaseModel):
    """Schema for submitting a single MBTI answer."""

    question_id: int
    answer: str = Field(..., pattern="^[AB]$")  # Must be "A" or "B"


class MBTITestStart(BaseModel):
    """Schema for starting an MBTI test."""

    language: str = Field(default="ja", pattern="^(en|ja)$")


class MBTITestSubmit(BaseModel):
    """Schema for submitting MBTI test answers."""

    answers: dict[int, str] = Field(..., description="Question ID to answer (A/B) mapping")

    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v):
        # Validate all answers are A or B
        for question_id, answer in v.items():
            if answer not in ['A', 'B']:
                raise ValueError(f"Invalid answer '{answer}' for question {question_id}. Must be 'A' or 'B'.")
        return v


class MBTITestResult(BaseModel):
    """Schema for MBTI test results."""

    id: int
    user_id: int
    status: MBTITestStatus
    mbti_type: str | None = None

    # Dimension scores (0-100)
    extraversion_introversion_score: int | None = None
    sensing_intuition_score: int | None = None
    thinking_feeling_score: int | None = None
    judging_perceiving_score: int | None = None

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Audit
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_completed: bool
    completion_percentage: int
    dimension_preferences: dict[str, str] = Field(default_factory=dict)
    strength_scores: dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class MBTITestSummary(BaseModel):
    """Schema for MBTI test summary (for candidate profile)."""

    mbti_type: str
    completed_at: datetime
    dimension_preferences: dict[str, str]
    strength_scores: dict[str, int]

    # MBTI type information
    type_name_en: str
    type_name_ja: str
    type_description_en: str
    type_description_ja: str
    temperament: str  # NT, NF, SJ, SP

    model_config = ConfigDict(from_attributes=True)


class MBTITestProgress(BaseModel):
    """Schema for MBTI test progress."""

    status: MBTITestStatus
    completion_percentage: int
    current_question: int | None = None
    total_questions: int = 60
    started_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MBTITypeInfo(BaseModel):
    """Schema for MBTI type information."""

    type_code: MBTIType
    name_en: str
    name_ja: str
    description_en: str
    description_ja: str
    temperament: str
    strengths_en: list[str]
    strengths_ja: list[str]
    weaknesses_en: list[str]
    weaknesses_ja: list[str]
    careers_en: list[str]
    careers_ja: list[str]


# Static MBTI type information
MBTI_TYPE_INFO = {
    MBTIType.INTJ: MBTITypeInfo(
        type_code=MBTIType.INTJ,
        name_en="The Architect",
        name_ja="建築家",
        description_en="Imaginative and strategic thinkers, with a plan for everything.",
        description_ja="想像力豊かで戦略的な思考の持ち主で、あらゆることに対して計画を持っています。",
        temperament="NT",
        strengths_en=["Strategic thinking", "Independent", "Decisive", "Hard-working", "Determined"],
        strengths_ja=["戦略的思考", "独立性", "決断力", "勤勉", "決意"],
        weaknesses_en=["Arrogant", "Judgmental", "Overly analytical", "Loathe highly structured environments"],
        weaknesses_ja=["傲慢", "批判的", "過度に分析的", "高度に構造化された環境を嫌う"],
        careers_en=["Scientist", "Engineer", "Doctor", "Lawyer", "Teacher", "Computer Programmer"],
        careers_ja=["科学者", "エンジニア", "医師", "弁護士", "教師", "プログラマー"]
    ),
    MBTIType.INTP: MBTITypeInfo(
        type_code=MBTIType.INTP,
        name_en="The Thinker",
        name_ja="論理学者",
        description_en="Innovative inventors with an unquenchable thirst for knowledge.",
        description_ja="知識に対する飽くなき探求心を持つ革新的な発明家です。",
        temperament="NT",
        strengths_en=["Analytical", "Original", "Open-minded", "Curious", "Objective"],
        strengths_ja=["分析的", "独創的", "オープンマインド", "好奇心旺盛", "客観的"],
        weaknesses_en=["Disconnected", "Insensitive", "Dissatisfied", "Impatient"],
        weaknesses_ja=["つながりの欠如", "鈍感", "不満足", "短気"],
        careers_en=["Scientist", "Mathematician", "Engineer", "Economist", "Philosopher"],
        careers_ja=["科学者", "数学者", "エンジニア", "経済学者", "哲学者"]
    ),
    MBTIType.ENTJ: MBTITypeInfo(
        type_code=MBTIType.ENTJ,
        name_en="The Commander",
        name_ja="指揮官",
        description_en="Bold, imaginative and strong-willed leaders, always finding a way – or making one.",
        description_ja="大胆で想像力豊かで意志の強いリーダーで、常に道を見つけるか、作り出します。",
        temperament="NT",
        strengths_en=["Efficient", "Energetic", "Self-confident", "Strong-willed", "Strategic thinker"],
        strengths_ja=["効率的", "エネルギッシュ", "自信", "意志の強さ", "戦略的思考"],
        weaknesses_en=["Stubborn", "Impatient", "Arrogant", "Poor handling of emotions"],
        weaknesses_ja=["頑固", "短気", "傲慢", "感情の扱いが苦手"],
        careers_en=["CEO", "Manager", "Lawyer", "Judge", "Business Analyst"],
        careers_ja=["CEO", "マネージャー", "弁護士", "裁判官", "ビジネスアナリスト"]
    ),
    MBTIType.ENTP: MBTITypeInfo(
        type_code=MBTIType.ENTP,
        name_en="The Debater",
        name_ja="討論者",
        description_en="Smart and curious thinkers who cannot resist an intellectual challenge.",
        description_ja="知的な挑戦に抗うことができない、スマートで好奇心旺盛な思考者です。",
        temperament="NT",
        strengths_en=["Knowledgeable", "Quick thinker", "Original", "Excellent brainstormer"],
        strengths_ja=["博識", "素早い思考", "独創的", "優れたブレインストーマー"],
        weaknesses_en=["Argumentative", "Insensitive", "Intolerant", "Can be unreliable"],
        weaknesses_ja=["議論好き", "鈍感", "不寛容", "信頼性に欠ける場合がある"],
        careers_en=["Journalist", "Engineer", "Scientist", "Actor", "Lawyer"],
        careers_ja=["ジャーナリスト", "エンジニア", "科学者", "俳優", "弁護士"]
    ),
    # Add more types as needed...
}


def get_mbti_type_info(mbti_type: str) -> MBTITypeInfo:
    """Get detailed information about an MBTI type."""
    try:
        type_enum = MBTIType(mbti_type)
        return MBTI_TYPE_INFO.get(type_enum, None)
    except ValueError:
        return None
