"""CRUD operations for exam templates."""
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.exam_template import ExamTemplate
from app.schemas.exam_template import ExamTemplateCreate, ExamTemplateUpdate


class CRUDExamTemplate(CRUDBase[ExamTemplate, ExamTemplateCreate, ExamTemplateUpdate]):
    """CRUD operations for exam templates."""

    async def get_templates(
        self,
        db: AsyncSession,
        *,
        company_id: int | None = None,
        is_system_admin: bool = False,
        category: str | None = None,
        is_public: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExamTemplate], int]:
        """
        Get exam templates with filtering.

        Args:
            db: Database session
            company_id: Filter by company (if not system admin)
            is_system_admin: Whether user is system admin
            category: Filter by category
            is_public: Filter by public status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (templates list, total count)
        """
        # Build query
        query = select(ExamTemplate)

        # Filter conditions
        conditions = []

        # Access control
        if not is_system_admin:
            # Regular users can see public templates or their company's templates
            if company_id:
                conditions.append(
                    or_(
                        ExamTemplate.is_public is True,
                        ExamTemplate.company_id == company_id,
                    )
                )
            else:
                conditions.append(ExamTemplate.is_public is True)
        # System admins can see all templates

        # Additional filters
        if category:
            conditions.append(ExamTemplate.category == category)

        if is_public is not None:
            conditions.append(ExamTemplate.is_public == is_public)

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(ExamTemplate.created_at.desc())

        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()

        return templates, total

    async def create_from_exam(
        self,
        db: AsyncSession,
        *,
        exam_id: int,
        template_name: str,
        template_description: str | None,
        created_by_id: int,
        company_id: int | None,
        is_public: bool = False,
    ) -> ExamTemplate:
        """
        Create a template from an existing exam.

        Args:
            db: Database session
            exam_id: Source exam ID
            template_name: Name for the template
            template_description: Optional description
            created_by_id: User creating the template
            company_id: Company ID
            is_public: Whether template is public

        Returns:
            Created template
        """
        from app.models.exam import Exam, ExamQuestion

        # Get exam
        exam = await db.get(Exam, exam_id)
        if not exam:
            raise ValueError("Exam not found")

        # Get questions
        questions_query = select(ExamQuestion).where(ExamQuestion.exam_id == exam_id)
        questions_result = await db.execute(questions_query)
        questions = questions_result.scalars().all()

        # Build questions template
        questions_template = []
        for q in questions:
            question_dict = {
                "question_text": q.question_text,
                "question_type": q.question_type,
                "points": q.points,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "order_index": q.order_index,
            }
            questions_template.append(question_dict)

        # Create template
        template = ExamTemplate(
            name=template_name,
            description=template_description,
            exam_type=exam.exam_type,
            time_limit_minutes=exam.time_limit_minutes,
            max_attempts=exam.max_attempts,
            passing_score=exam.passing_score,
            shuffle_questions=exam.shuffle_questions,
            shuffle_options=exam.shuffle_options,
            show_score=exam.show_score,
            show_correct_answers=exam.show_correct_answers,
            show_results_immediately=exam.show_results_immediately,
            enable_monitoring=exam.enable_monitoring,
            enable_face_recognition=exam.enable_face_recognition,
            require_full_screen=exam.require_full_screen,
            questions_template={"questions": questions_template},
            created_by_id=created_by_id,
            company_id=company_id,
            is_public=is_public,
        )

        db.add(template)
        await db.commit()
        await db.refresh(template)

        return template


# Create instance
from sqlalchemy import func

exam_template = CRUDExamTemplate(ExamTemplate)
