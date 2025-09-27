import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, select
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
)


class CRUDExam(CRUDBase[Exam, ExamCreate, ExamUpdate]):
    
    async def get_by_company(
        self, 
        db: AsyncSession, 
        company_id: int,
        status: Optional[ExamStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Exam]:
        """Get exams for a specific company."""
        query = select(Exam).where(Exam.company_id == company_id)
        
        if status:
            query = query.where(Exam.status == status)
            
        query = query.offset(skip).limit(limit).order_by(desc(Exam.created_at))
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_details(self, db: AsyncSession, id: int) -> Optional[Exam]:
        """Get exam with all related data."""
        query = select(Exam).options(
            selectinload(Exam.questions),
            selectinload(Exam.sessions).selectinload(ExamSession.candidate),
            selectinload(Exam.assignments).selectinload(ExamAssignment.candidate),
            joinedload(Exam.company),
            joinedload(Exam.creator)
        ).where(Exam.id == id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_with_questions(
        self, 
        db: AsyncSession, 
        exam_data: ExamCreate, 
        questions_data: List[ExamQuestionCreate],
        created_by_id: int
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
    
    async def get_statistics(self, db: AsyncSession, exam_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for an exam."""
        # Basic counts
        total_assigned = await db.scalar(
            select(func.count(ExamAssignment.id)).where(ExamAssignment.exam_id == exam_id)
        )
        
        total_started = await db.scalar(
            select(func.count(ExamSession.id.distinct())).where(
                and_(ExamSession.exam_id == exam_id, ExamSession.started_at.is_not(None))
            )
        )
        
        total_completed = await db.scalar(
            select(func.count(ExamSession.id)).where(
                and_(ExamSession.exam_id == exam_id, ExamSession.status == SessionStatus.COMPLETED)
            )
        )
        
        # Score statistics
        score_stats = await db.execute(
            select(
                func.avg(ExamSession.percentage),
                func.min(ExamSession.percentage),
                func.max(ExamSession.percentage)
            ).where(
                and_(
                    ExamSession.exam_id == exam_id,
                    ExamSession.status == SessionStatus.COMPLETED,
                    ExamSession.percentage.is_not(None)
                )
            )
        )
        avg_score, min_score, max_score = score_stats.first() or (None, None, None)
        
        # Time statistics (in minutes)
        time_stats = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', ExamSession.completed_at - ExamSession.started_at) / 60
                )
            ).where(
                and_(
                    ExamSession.exam_id == exam_id,
                    ExamSession.status == SessionStatus.COMPLETED,
                    ExamSession.started_at.is_not(None),
                    ExamSession.completed_at.is_not(None)
                )
            )
        )
        avg_time = time_stats.scalar()
        
        completion_rate = (total_completed / total_started * 100) if total_started > 0 else 0
        
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
    
    async def get_by_exam(self, db: AsyncSession, exam_id: int) -> List[ExamQuestion]:
        """Get all questions for an exam, ordered by order_index."""
        query = select(ExamQuestion).where(
            ExamQuestion.exam_id == exam_id
        ).order_by(ExamQuestion.order_index)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_randomized_questions(self, db: AsyncSession, exam_id: int) -> List[ExamQuestion]:
        """Get questions in randomized order."""
        questions = await self.get_by_exam(db, exam_id)
        random.shuffle(questions)
        return questions
    
    async def reorder_questions(
        self, 
        db: AsyncSession, 
        exam_id: int, 
        question_orders: List[Dict[str, int]]  # [{"question_id": 1, "order_index": 0}]
    ) -> List[ExamQuestion]:
        """Reorder questions in an exam."""
        for order_data in question_orders:
            await db.execute(
                select(ExamQuestion).where(
                    and_(
                        ExamQuestion.id == order_data["question_id"],
                        ExamQuestion.exam_id == exam_id
                    )
                ).update({"order_index": order_data["order_index"]})
            )
        
        await db.commit()
        return await self.get_by_exam(db, exam_id)


class CRUDExamSession(CRUDBase[ExamSession, ExamSessionCreate, ExamSessionUpdate]):
    
    async def get_by_candidate_and_exam(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        exam_id: int
    ) -> List[ExamSession]:
        """Get all sessions for a candidate and exam."""
        query = select(ExamSession).where(
            and_(
                ExamSession.candidate_id == candidate_id,
                ExamSession.exam_id == exam_id
            )
        ).order_by(desc(ExamSession.created_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active_session(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        exam_id: int
    ) -> Optional[ExamSession]:
        """Get active (in-progress) session for candidate."""
        query = select(ExamSession).where(
            and_(
                ExamSession.candidate_id == candidate_id,
                ExamSession.exam_id == exam_id,
                ExamSession.status == SessionStatus.IN_PROGRESS
            )
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_session(
        self, 
        db: AsyncSession, 
        candidate_id: int,
        exam_id: int,
        assignment_id: Optional[int] = None
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
                    ExamSession.exam_id == exam_id
                )
            )
        )
        
        if existing_count >= exam.max_attempts:
            raise ValueError(f"Maximum attempts ({exam.max_attempts}) exceeded")
        
        # Calculate expiration time
        expires_at = None
        if exam.time_limit_minutes:
            expires_at = datetime.utcnow() + timedelta(minutes=exam.time_limit_minutes)
        
        session = ExamSession(
            exam_id=exam_id,
            candidate_id=candidate_id,
            assignment_id=assignment_id,
            attempt_number=existing_count + 1,
            total_questions=questions_count,
            expires_at=expires_at,
            time_remaining_seconds=exam.time_limit_minutes * 60 if exam.time_limit_minutes else None
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    
    async def create_test_session(
        self, 
        db: AsyncSession, 
        candidate_id: int,
        exam_id: int
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
            expires_at = datetime.utcnow() + timedelta(minutes=exam.time_limit_minutes)
        
        session = ExamSession(
            exam_id=exam_id,
            candidate_id=candidate_id,
            assignment_id=None,  # Test sessions don't have assignments
            attempt_number=0,  # Test sessions don't count as attempts
            total_questions=questions_count,
            expires_at=expires_at,
            time_remaining_seconds=exam.time_limit_minutes * 60 if exam.time_limit_minutes else None,
            # Mark as test session in a way that doesn't interfere with regular sessions
            web_usage_detected=False,  # Don't enforce strict monitoring for test sessions
            face_verification_failed=False
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
        session.started_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(session)
        return session
    
    async def complete_session(
        self, 
        db: AsyncSession, 
        session_id: int,
        calculate_score: bool = True
    ) -> ExamSession:
        """Complete a session and calculate final score."""
        session = await db.get(ExamSession, session_id)
        if not session:
            raise ValueError("Session not found")
        
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        
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
            session.percentage = (total_points / max_points * 100) if max_points > 0 else 0
            
            # Check if passed
            exam = await db.get(Exam, session.exam_id)
            if exam and exam.passing_score is not None:
                session.passed = session.percentage >= exam.passing_score
        
        await db.commit()
        await db.refresh(session)
        return session
    
    async def get_with_details(self, db: AsyncSession, session_id: int) -> Optional[ExamSession]:
        """Get session with all related data."""
        query = select(ExamSession).options(
            joinedload(ExamSession.exam),
            joinedload(ExamSession.candidate),
            selectinload(ExamSession.answers).joinedload(ExamAnswer.question),
            selectinload(ExamSession.monitoring_events)
        ).where(ExamSession.id == session_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()


class CRUDExamAnswer(CRUDBase[ExamAnswer, ExamAnswerSubmit, ExamAnswerSubmit]):
    
    async def submit_answer(
        self, 
        db: AsyncSession, 
        session_id: int,
        answer_data: ExamAnswerSubmit
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
                    ExamAnswer.question_id == answer_data.question_id
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
                points_possible=question.points
            )
            db.add(answer)
        
        # Update answer data
        answer.answer_data = answer_data.answer_data
        answer.answer_text = answer_data.answer_text
        answer.selected_options = answer_data.selected_options
        answer.time_spent_seconds = answer_data.time_spent_seconds
        answer.answered_at = datetime.utcnow()
        
        # Auto-grade if possible
        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SINGLE_CHOICE, QuestionType.TRUE_FALSE]:
            is_correct = self._grade_choice_question(question, answer_data.selected_options or [])
            answer.is_correct = is_correct
            answer.points_earned = question.points if is_correct else 0
        
        await db.commit()
        await db.refresh(answer)
        
        # Update session progress
        await self._update_session_progress(db, session_id)
        
        return answer
    
    def _grade_choice_question(self, question: ExamQuestion, selected_options: List[str]) -> bool:
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


class CRUDExamAssignment(CRUDBase[ExamAssignment, ExamAssignmentCreate, ExamAssignmentUpdate]):
    
    async def create_assignments(
        self, 
        db: AsyncSession, 
        assignment_data: ExamAssignmentCreate,
        assigned_by_id: int
    ) -> List[ExamAssignment]:
        """Create assignments for multiple candidates."""
        assignments = []
        
        for candidate_id in assignment_data.candidate_ids:
            # Check if assignment already exists
            existing = await db.scalar(
                select(ExamAssignment).where(
                    and_(
                        ExamAssignment.exam_id == assignment_data.exam_id,
                        ExamAssignment.candidate_id == candidate_id,
                        ExamAssignment.is_active == True
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
                custom_max_attempts=assignment_data.custom_max_attempts
            )
            
            db.add(assignment)
            assignments.append(assignment)
        
        await db.commit()
        return assignments
    
    async def get_candidate_assignments(
        self, 
        db: AsyncSession, 
        candidate_id: int,
        is_active: bool = True
    ) -> List[ExamAssignment]:
        """Get assignments for a candidate."""
        query = select(ExamAssignment).options(
            joinedload(ExamAssignment.exam),
            joinedload(ExamAssignment.assigner)
        ).where(
            and_(
                ExamAssignment.candidate_id == candidate_id,
                ExamAssignment.is_active == is_active
            )
        ).order_by(ExamAssignment.due_date.asc().nulls_last())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_exam(self, db: AsyncSession, exam_id: int) -> List[ExamAssignment]:
        """Get all assignments for an exam."""
        query = select(ExamAssignment).options(
            joinedload(ExamAssignment.candidate),
            selectinload(ExamAssignment.sessions)
        ).where(ExamAssignment.exam_id == exam_id)
        
        result = await db.execute(query)
        return result.scalars().all()


class CRUDExamMonitoringEvent(CRUDBase[ExamMonitoringEvent, ExamMonitoringEventCreate, ExamMonitoringEventCreate]):
    
    async def create_event(
        self, 
        db: AsyncSession, 
        event_data: ExamMonitoringEventCreate
    ) -> ExamMonitoringEvent:
        """Create a monitoring event."""
        event = ExamMonitoringEvent(**event_data.model_dump())
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
    
    async def get_session_events(
        self, 
        db: AsyncSession, 
        session_id: int,
        event_type: Optional[str] = None
    ) -> List[ExamMonitoringEvent]:
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