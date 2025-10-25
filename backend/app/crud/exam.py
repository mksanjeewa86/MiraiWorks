import random
from datetime import timedelta
from typing import Any

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base import CRUDBase
from app.models.exam import (
    Exam,
    ExamAnswer,
    ExamAssignment,
    ExamMonitoringEvent,
    ExamQuestion,
    ExamSession,
    ExamStatus,
    QuestionType,
    SessionStatus,
)
from app.schemas.exam import (
    ExamAnswerSubmit,
    ExamAssignmentCreate,
    ExamAssignmentUpdate,
    ExamCreate,
    ExamMonitoringEventCreate,
    ExamQuestionCreate,
    ExamQuestionUpdate,
    ExamSessionCreate,
    ExamSessionUpdate,
    ExamUpdate,
    HybridExamCreate,
)
from app.utils.datetime_utils import get_utc_now


class CRUDExam(CRUDBase[Exam, ExamCreate, ExamUpdate]):
    async def get_by_company(
        self,
        db: AsyncSession,
        company_id: int | None = None,
        status: ExamStatus | None = None,
        skip: int = 0,
        limit: int = 100,
        include_public: bool = True,
    ) -> list[Exam]:
        """Get exams for a specific company or all exams if company_id is None.

        Args:
            company_id: Filter by company. None returns all exams.
            status: Filter by exam status
            skip: Offset for pagination
            limit: Limit results
            include_public: If True and company_id provided, also include global/public exams

        Returns:
            List of exams matching the criteria
        """
        query = select(Exam)

        # Only filter by company if company_id is provided
        if company_id is not None:
            if include_public:
                # Include company's own exams + global/public exams
                query = query.where(
                    or_(
                        Exam.company_id == company_id,  # Own company's exams
                        and_(
                            Exam.company_id.is_(None), Exam.is_public is True
                        ),  # Global public exams
                        Exam.is_public is True,  # Any public exam
                    )
                )
            else:
                # Only company's own exams
                query = query.where(Exam.company_id == company_id)

        if status:
            query = query.where(Exam.status == status)

        query = query.offset(skip).limit(limit).order_by(desc(Exam.created_at))
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_details(self, db: AsyncSession, id: int) -> Exam | None:
        """Get exam with all related data."""
        query = (
            select(Exam)
            .options(
                selectinload(Exam.questions),
                selectinload(Exam.sessions).selectinload(ExamSession.candidate),
                selectinload(Exam.assignments).selectinload(ExamAssignment.candidate),
                joinedload(Exam.company),
                joinedload(Exam.creator),
            )
            .where(Exam.id == id)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_with_questions(
        self,
        db: AsyncSession,
        exam_data: ExamCreate,
        questions_data: list[ExamQuestionCreate],
        created_by_id: int,
    ) -> Exam:
        """Create exam with questions in one transaction."""
        # Create exam
        exam_dict = exam_data.model_dump()
        exam_dict["created_by"] = created_by_id
        exam = Exam(**exam_dict)

        db.add(exam)
        await db.flush()  # Get the exam ID

        # Create questions
        for i, question_data in enumerate(questions_data):
            question_dict = question_data.model_dump()
            question_dict["exam_id"] = exam.id
            question_dict["order_index"] = i
            question = ExamQuestion(**question_dict)
            db.add(question)

        await db.commit()
        await db.refresh(exam)
        return exam

    async def create_hybrid_exam(
        self,
        db: AsyncSession,
        hybrid_data: HybridExamCreate,
        created_by_id: int,
    ) -> tuple[Exam, dict[str, Any]]:
        """
        Create a hybrid exam with custom questions + randomly selected questions from question banks.

        Returns:
            tuple[Exam, dict]: The created exam and selection rules metadata
        """
        from app.crud.question_bank import question_bank_item as question_bank_item_crud

        # Validate that at least one question source is provided
        if not hybrid_data.validate_has_questions():
            raise ValueError(
                "At least one custom question or template selection is required"
            )

        # Create the base exam
        exam_dict = hybrid_data.exam_data.model_dump()
        exam_dict["created_by"] = created_by_id
        exam = Exam(**exam_dict)

        db.add(exam)
        await db.flush()  # Get the exam ID

        # Track question creation
        question_count = 0
        custom_count = 0
        template_count = 0
        selection_metadata: dict[str, Any] = {
            "custom_count": 0,
            "template_selections": [],
        }

        # 1. Add custom questions
        for _i, custom_q in enumerate(hybrid_data.custom_questions):
            question_dict = custom_q.model_dump()
            question_dict["exam_id"] = exam.id
            question_dict["order_index"] = question_count
            question_dict["source_type"] = "custom"
            question_dict["source_bank_id"] = None
            question_dict["source_question_id"] = None

            question = ExamQuestion(**question_dict)
            db.add(question)

            question_count += 1
            custom_count += 1

        selection_metadata["custom_count"] = custom_count

        # 2. Add questions from template selections (question banks)
        for template_selection in hybrid_data.template_selections:
            # Randomly select questions from the question bank
            selected_questions = await question_bank_item_crud.get_random_questions(
                db=db,
                bank_id=template_selection.bank_id,
                count=template_selection.count,
                category=template_selection.category,
                difficulty=template_selection.difficulty,
                tags=template_selection.tags,
            )

            # Track metadata for this selection
            selection_info = {
                "bank_id": template_selection.bank_id,
                "requested_count": template_selection.count,
                "actual_count": len(selected_questions),
                "category": template_selection.category,
                "difficulty": template_selection.difficulty,
                "tags": template_selection.tags,
                "question_ids": [],
            }

            # Create exam questions from selected question bank items
            for bank_question in selected_questions:
                question_dict = {
                    "exam_id": exam.id,
                    "order_index": question_count,
                    "question_text": bank_question.question_text,
                    "question_type": bank_question.question_type,
                    "options": bank_question.options,
                    "correct_answers": bank_question.correct_answers,
                    "points": bank_question.points,
                    "time_limit_seconds": bank_question.time_limit_seconds,
                    "is_required": True,
                    "max_length": bank_question.max_length,
                    "min_length": bank_question.min_length,
                    "rating_scale": bank_question.rating_scale,
                    "explanation": bank_question.explanation,
                    "tags": bank_question.tags,
                    # Source tracking
                    "source_type": "question_bank",
                    "source_bank_id": bank_question.bank_id,
                    "source_question_id": bank_question.id,
                }

                question = ExamQuestion(**question_dict)
                db.add(question)

                selection_info["question_ids"].append(bank_question.id)
                question_count += 1
                template_count += 1

            selection_metadata["template_selections"].append(selection_info)

        # Store selection rules in exam
        exam.question_selection_rules = selection_metadata

        await db.commit()
        await db.refresh(exam)

        return exam, {
            "total_questions": question_count,
            "custom_count": custom_count,
            "template_count": template_count,
            "selection_rules": selection_metadata,
        }

    async def get_statistics(self, db: AsyncSession, exam_id: int) -> dict[str, Any]:
        """Get comprehensive statistics for an exam."""
        # Basic counts
        total_assigned = await db.scalar(
            select(func.count(ExamAssignment.id)).where(
                ExamAssignment.exam_id == exam_id
            )
        )

        total_started = await db.scalar(
            select(func.count(ExamSession.id.distinct())).where(
                and_(
                    ExamSession.exam_id == exam_id, ExamSession.started_at.is_not(None)
                )
            )
        )

        total_completed = await db.scalar(
            select(func.count(ExamSession.id)).where(
                and_(
                    ExamSession.exam_id == exam_id,
                    ExamSession.status == SessionStatus.COMPLETED,
                )
            )
        )

        # Score statistics
        score_stats = await db.execute(
            select(
                func.avg(ExamSession.percentage),
                func.min(ExamSession.percentage),
                func.max(ExamSession.percentage),
            ).where(
                and_(
                    ExamSession.exam_id == exam_id,
                    ExamSession.status == SessionStatus.COMPLETED,
                    ExamSession.percentage.is_not(None),
                )
            )
        )
        avg_score, min_score, max_score = score_stats.first() or (None, None, None)

        # Time statistics (in minutes)
        time_stats = await db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch", ExamSession.completed_at - ExamSession.started_at
                    )
                    / 60
                )
            ).where(
                and_(
                    ExamSession.exam_id == exam_id,
                    ExamSession.status == SessionStatus.COMPLETED,
                    ExamSession.started_at.is_not(None),
                    ExamSession.completed_at.is_not(None),
                )
            )
        )
        avg_time = time_stats.scalar()

        completion_rate = (
            (total_completed / total_started * 100) if total_started > 0 else 0
        )

        return {
            "total_assigned": total_assigned or 0,
            "total_started": total_started or 0,
            "total_completed": total_completed or 0,
            "completion_rate": round(completion_rate, 2),
            "average_score": round(avg_score, 2) if avg_score else None,
            "min_score": round(min_score, 2) if min_score else None,
            "max_score": round(max_score, 2) if max_score else None,
            "average_time_minutes": round(avg_time, 2) if avg_time else None,
        }


class CRUDExamQuestion(CRUDBase[ExamQuestion, ExamQuestionCreate, ExamQuestionUpdate]):
    async def get_by_exam(self, db: AsyncSession, exam_id: int) -> list[ExamQuestion]:
        """Get all questions for an exam, ordered by order_index."""
        query = (
            select(ExamQuestion)
            .where(ExamQuestion.exam_id == exam_id)
            .order_by(ExamQuestion.order_index)
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def get_randomized_questions(
        self, db: AsyncSession, exam_id: int
    ) -> list[ExamQuestion]:
        """Get questions in randomized order."""
        questions = await self.get_by_exam(db, exam_id)
        random.shuffle(questions)
        return questions

    async def reorder_questions(
        self,
        db: AsyncSession,
        exam_id: int,
        question_orders: list[dict[str, int]],  # [{"question_id": 1, "order_index": 0}]
    ) -> list[ExamQuestion]:
        """Reorder questions in an exam."""
        for order_data in question_orders:
            await db.execute(
                select(ExamQuestion)
                .where(
                    and_(
                        ExamQuestion.id == order_data["question_id"],
                        ExamQuestion.exam_id == exam_id,
                    )
                )
                .update({"order_index": order_data["order_index"]})
            )

        await db.commit()
        return await self.get_by_exam(db, exam_id)


class CRUDExamSession(CRUDBase[ExamSession, ExamSessionCreate, ExamSessionUpdate]):
    async def get_by_candidate_and_exam(
        self, db: AsyncSession, candidate_id: int, exam_id: int
    ) -> list[ExamSession]:
        """Get all sessions for a candidate and exam."""
        query = (
            select(ExamSession)
            .where(
                and_(
                    ExamSession.candidate_id == candidate_id,
                    ExamSession.exam_id == exam_id,
                )
            )
            .order_by(desc(ExamSession.created_at))
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def get_active_session(
        self, db: AsyncSession, candidate_id: int, exam_id: int
    ) -> ExamSession | None:
        """Get active (in-progress) session for candidate."""
        query = select(ExamSession).where(
            and_(
                ExamSession.candidate_id == candidate_id,
                ExamSession.exam_id == exam_id,
                ExamSession.status == SessionStatus.IN_PROGRESS,
            )
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_session(
        self,
        db: AsyncSession,
        candidate_id: int,
        exam_id: int,
        assignment_id: int | None = None,
    ) -> ExamSession:
        """Create a new exam session."""
        # Get exam details
        exam = await db.get(Exam, exam_id)
        if not exam:
            raise ValueError("Exam not found")

        # Count questions
        questions_count = await db.scalar(
            select(func.count(ExamQuestion.id)).where(ExamQuestion.exam_id == exam_id)
        )

        # Check existing attempts
        existing_count = await db.scalar(
            select(func.count(ExamSession.id)).where(
                and_(
                    ExamSession.candidate_id == candidate_id,
                    ExamSession.exam_id == exam_id,
                )
            )
        )

        if existing_count >= exam.max_attempts:
            raise ValueError(f"Maximum attempts ({exam.max_attempts}) exceeded")

        # Calculate expiration time
        expires_at = None
        if exam.time_limit_minutes:
            expires_at = get_utc_now() + timedelta(minutes=exam.time_limit_minutes)

        session = ExamSession(
            exam_id=exam_id,
            candidate_id=candidate_id,
            assignment_id=assignment_id,
            attempt_number=existing_count + 1,
            total_questions=questions_count,
            expires_at=expires_at,
            time_remaining_seconds=exam.time_limit_minutes * 60
            if exam.time_limit_minutes
            else None,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def create_test_session(
        self, db: AsyncSession, candidate_id: int, exam_id: int
    ) -> ExamSession:
        """Create a test session that doesn't count towards attempts."""
        # Get exam details
        exam = await db.get(Exam, exam_id)
        if not exam:
            raise ValueError("Exam not found")

        # Count questions
        questions_count = await db.scalar(
            select(func.count(ExamQuestion.id)).where(ExamQuestion.exam_id == exam_id)
        )

        # Calculate expiration time (shorter for test sessions)
        expires_at = None
        if exam.time_limit_minutes:
            expires_at = get_utc_now() + timedelta(minutes=exam.time_limit_minutes)

        session = ExamSession(
            exam_id=exam_id,
            candidate_id=candidate_id,
            assignment_id=None,  # Test sessions don't have assignments
            attempt_number=0,  # Test sessions don't count as attempts
            total_questions=questions_count,
            expires_at=expires_at,
            time_remaining_seconds=exam.time_limit_minutes * 60
            if exam.time_limit_minutes
            else None,
            # Mark as test session in a way that doesn't interfere with regular sessions
            web_usage_detected=False,  # Don't enforce strict monitoring for test sessions
            face_verification_failed=False,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def start_session(self, db: AsyncSession, session_id: int) -> ExamSession:
        """Mark session as started."""
        session = await db.get(ExamSession, session_id)
        if not session:
            raise ValueError("Session not found")

        session.status = SessionStatus.IN_PROGRESS
        session.started_at = get_utc_now()

        await db.commit()
        await db.refresh(session)
        return session

    async def complete_session(
        self, db: AsyncSession, session_id: int, calculate_score: bool = True
    ) -> ExamSession:
        """Complete a session and calculate final score."""
        session = await db.get(ExamSession, session_id)
        if not session:
            raise ValueError("Session not found")

        session.status = SessionStatus.COMPLETED
        session.completed_at = get_utc_now()

        if calculate_score:
            # Calculate score from answers
            total_points = await db.scalar(
                select(func.sum(ExamAnswer.points_earned)).where(
                    ExamAnswer.session_id == session_id
                )
            )

            max_points = await db.scalar(
                select(func.sum(ExamAnswer.points_possible)).where(
                    ExamAnswer.session_id == session_id
                )
            )

            session.score = total_points or 0
            session.max_score = max_points or 0
            session.percentage = (
                (total_points / max_points * 100) if max_points > 0 else 0
            )

            # Check if passed
            exam = await db.get(Exam, session.exam_id)
            if exam and exam.passing_score is not None:
                session.passed = session.percentage >= exam.passing_score

        await db.commit()
        await db.refresh(session)
        return session

    async def get_with_details(
        self, db: AsyncSession, session_id: int
    ) -> ExamSession | None:
        """Get session with all related data."""
        query = (
            select(ExamSession)
            .options(
                joinedload(ExamSession.exam),
                joinedload(ExamSession.candidate),
                selectinload(ExamSession.answers).joinedload(ExamAnswer.question),
                selectinload(ExamSession.monitoring_events),
            )
            .where(ExamSession.id == session_id)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_sessions_by_exam(
        self, db: AsyncSession, exam_id: int, status: str | None = None
    ) -> list[ExamSession]:
        """Get all sessions for an exam, optionally filtered by status."""
        query = select(ExamSession).where(ExamSession.exam_id == exam_id)

        if status:
            query = query.where(ExamSession.status == status)

        query = query.order_by(desc(ExamSession.created_at))

        result = await db.execute(query)
        return result.scalars().all()


class CRUDExamAnswer(CRUDBase[ExamAnswer, ExamAnswerSubmit, ExamAnswerSubmit]):
    async def submit_answer(
        self, db: AsyncSession, session_id: int, answer_data: ExamAnswerSubmit
    ) -> ExamAnswer:
        """Submit an answer for a question."""
        # Get the question
        question = await db.get(ExamQuestion, answer_data.question_id)
        if not question:
            raise ValueError("Question not found")

        # Check if answer already exists
        existing = await db.scalar(
            select(ExamAnswer).where(
                and_(
                    ExamAnswer.session_id == session_id,
                    ExamAnswer.question_id == answer_data.question_id,
                )
            )
        )

        if existing:
            # Update existing answer
            answer = existing
        else:
            # Create new answer
            answer = ExamAnswer(
                session_id=session_id,
                question_id=answer_data.question_id,
                points_possible=question.points,
            )
            db.add(answer)

        # Update answer data
        answer.answer_data = answer_data.answer_data
        answer.answer_text = answer_data.answer_text
        answer.selected_options = answer_data.selected_options
        answer.time_spent_seconds = answer_data.time_spent_seconds
        answer.answered_at = get_utc_now()

        # Auto-grade if possible
        if question.question_type in [
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.SINGLE_CHOICE,
            QuestionType.TRUE_FALSE,
        ]:
            is_correct = self._grade_choice_question(
                question, answer_data.selected_options or []
            )
            answer.is_correct = is_correct
            answer.points_earned = question.points if is_correct else 0

        await db.commit()
        await db.refresh(answer)

        # Update session progress
        await self._update_session_progress(db, session_id)

        return answer

    def _grade_choice_question(
        self, question: ExamQuestion, selected_options: list[str]
    ) -> bool:
        """Grade multiple choice, single choice, or true/false questions."""
        if not question.correct_answers:
            return False

        correct_set = set(question.correct_answers)
        selected_set = set(selected_options)

        return correct_set == selected_set

    async def _update_session_progress(self, db: AsyncSession, session_id: int):
        """Update session progress after answer submission."""
        answered_count = await db.scalar(
            select(func.count(ExamAnswer.id)).where(ExamAnswer.session_id == session_id)
        )

        session = await db.get(ExamSession, session_id)
        if session:
            session.questions_answered = answered_count
            await db.commit()


class CRUDExamAssignment(
    CRUDBase[ExamAssignment, ExamAssignmentCreate, ExamAssignmentUpdate]
):
    async def create_assignments(
        self,
        db: AsyncSession,
        assignment_data: ExamAssignmentCreate,
        assigned_by_id: int,
    ) -> list[ExamAssignment]:
        """Create assignments for multiple candidates."""
        assignments = []

        for candidate_id in assignment_data.candidate_ids:
            # Check if assignment already exists
            existing = await db.scalar(
                select(ExamAssignment).where(
                    and_(
                        ExamAssignment.exam_id == assignment_data.exam_id,
                        ExamAssignment.candidate_id == candidate_id,
                        ExamAssignment.is_active is True,
                    )
                )
            )

            if existing:
                continue  # Skip if already assigned

            assignment = ExamAssignment(
                exam_id=assignment_data.exam_id,
                candidate_id=candidate_id,
                assigned_by=assigned_by_id,
                due_date=assignment_data.due_date,
                custom_time_limit_minutes=assignment_data.custom_time_limit_minutes,
                custom_max_attempts=assignment_data.custom_max_attempts,
            )

            db.add(assignment)
            assignments.append(assignment)

        await db.commit()
        return assignments

    async def get_candidate_assignments(
        self, db: AsyncSession, candidate_id: int, is_active: bool = True
    ) -> list[ExamAssignment]:
        """Get assignments for a candidate."""
        from sqlalchemy import case

        # MySQL-compatible way to put NULL values last
        # Using CASE to sort NULL values as a very high value
        query = (
            select(ExamAssignment)
            .options(
                joinedload(ExamAssignment.exam), joinedload(ExamAssignment.assigner)
            )
            .where(
                and_(
                    ExamAssignment.candidate_id == candidate_id,
                    ExamAssignment.is_active == is_active,
                )
            )
            .order_by(
                case((ExamAssignment.due_date.is_(None), 1), else_=0),
                ExamAssignment.due_date.asc(),
            )
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_exam(self, db: AsyncSession, exam_id: int) -> list[ExamAssignment]:
        """Get all assignments for an exam."""
        query = (
            select(ExamAssignment)
            .options(
                joinedload(ExamAssignment.candidate),
                selectinload(ExamAssignment.sessions),
            )
            .where(ExamAssignment.exam_id == exam_id)
        )

        result = await db.execute(query)
        return result.scalars().all()


class CRUDExamMonitoringEvent(
    CRUDBase[ExamMonitoringEvent, ExamMonitoringEventCreate, ExamMonitoringEventCreate]
):
    async def create_event(
        self, db: AsyncSession, event_data: ExamMonitoringEventCreate
    ) -> ExamMonitoringEvent:
        """Create a monitoring event."""
        event = ExamMonitoringEvent(**event_data.model_dump())
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    async def get_session_events(
        self, db: AsyncSession, session_id: int, event_type: str | None = None
    ) -> list[ExamMonitoringEvent]:
        """Get monitoring events for a session."""
        query = select(ExamMonitoringEvent).where(
            ExamMonitoringEvent.session_id == session_id
        )

        if event_type:
            query = query.where(ExamMonitoringEvent.event_type == event_type)

        query = query.order_by(ExamMonitoringEvent.timestamp.desc())
        result = await db.execute(query)
        return result.scalars().all()


# Create instances
exam = CRUDExam(Exam)
exam_question = CRUDExamQuestion(ExamQuestion)
exam_session = CRUDExamSession(ExamSession)
exam_answer = CRUDExamAnswer(ExamAnswer)
exam_assignment = CRUDExamAssignment(ExamAssignment)
exam_monitoring = CRUDExamMonitoringEvent(ExamMonitoringEvent)
