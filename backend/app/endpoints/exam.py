from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.exam import exam as exam_crud
from app.crud.exam import exam_answer as exam_answer_crud
from app.crud.exam import exam_assignment as exam_assignment_crud
from app.crud.exam import exam_monitoring as exam_monitoring_crud
from app.crud.exam import exam_question as exam_question_crud
from app.crud.exam import exam_session as exam_session_crud
from app.database import get_db
from app.dependencies import get_current_active_user, get_current_user_with_company
from app.models.exam import ExamStatus, SessionStatus
from app.models.user import User
from app.schemas.exam import (
    ExamAnswerInfo,
    ExamAnswerSubmit,
    ExamAssignmentCreate,
    ExamAssignmentInfo,
    ExamCreate,
    ExamInfo,
    ExamListResponse,
    ExamMonitoringEventCreate,
    ExamMonitoringEventInfo,
    ExamQuestionCreate,
    ExamQuestionInfo,
    ExamQuestionUpdate,
    ExamResultSummary,
    ExamSessionInfo,
    ExamSessionListResponse,
    ExamTakeRequest,
    ExamTakeResponse,
    ExamUpdate,
    FaceVerificationResponse,
    FaceVerificationSubmit,
)
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter()


# Exam management endpoints (for employers)

@router.post("/exams", response_model=ExamInfo)
async def create_exam(
    exam_data: ExamCreate,
    questions_data: list[ExamQuestionCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Create a new exam with questions."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    # Verify company access
    if exam_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create exam for different company"
        )

    if not questions_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one question is required"
        )

    try:
        exam = await exam_crud.create_with_questions(
            db=db,
            exam_data=exam_data,
            questions_data=questions_data,
            created_by_id=current_user.id
        )
        return exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/exams", response_model=ExamListResponse)
async def get_company_exams(
    status_filter: ExamStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Get exams for current user's company."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exams = await exam_crud.get_by_company(
        db=db,
        company_id=current_user.company_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    total = len(exams)  # For simplicity, could be optimized with count query

    return ExamListResponse(
        exams=exams,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(exams) == limit
    )


@router.get("/exams/{exam_id}", response_model=ExamInfo)
async def get_exam_details(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Get detailed exam information."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get_with_details(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return exam


@router.put("/exams/{exam_id}", response_model=ExamInfo)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Update exam details."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    exam = await exam_crud.update(db=db, db_obj=exam, obj_in=exam_data)
    return exam


@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Delete an exam."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await exam_crud.remove(db=db, id=exam_id)
    return {"message": "Exam deleted successfully"}


@router.get("/exams/{exam_id}/statistics", response_model=dict[str, Any])
async def get_exam_statistics(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Get comprehensive exam statistics."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    stats = await exam_crud.get_statistics(db=db, exam_id=exam_id)
    return stats


# Question management endpoints

@router.get("/exams/{exam_id}/questions", response_model=list[ExamQuestionInfo])
async def get_exam_questions(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Get all questions for an exam."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    questions = await exam_question_crud.get_by_exam(db=db, exam_id=exam_id)
    return questions


@router.post("/exams/{exam_id}/questions", response_model=ExamQuestionInfo)
async def add_exam_question(
    exam_id: int,
    question_data: ExamQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Add a new question to an exam."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    question_data.exam_id = exam_id
    question = await exam_question_crud.create(db=db, obj_in=question_data)
    return question


@router.put("/questions/{question_id}", response_model=ExamQuestionInfo)
async def update_exam_question(
    question_id: int,
    question_data: ExamQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Update an exam question."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    question = await exam_question_crud.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Verify company access through exam
    exam = await exam_crud.get(db=db, id=question.exam_id)
    if not exam or exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    question = await exam_question_crud.update(db=db, db_obj=question, obj_in=question_data)
    return question


@router.delete("/questions/{question_id}")
async def delete_exam_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Delete an exam question."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    question = await exam_question_crud.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Verify company access through exam
    exam = await exam_crud.get(db=db, id=question.exam_id)
    if not exam or exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await exam_question_crud.remove(db=db, id=question_id)
    return {"message": "Question deleted successfully"}


# Assignment management endpoints

@router.post("/exams/{exam_id}/assignments", response_model=list[ExamAssignmentInfo])
async def create_exam_assignments(
    exam_id: int,
    assignment_data: ExamAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Assign exam to candidates."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    assignment_data.exam_id = exam_id
    assignments = await exam_assignment_crud.create_assignments(
        db=db,
        assignment_data=assignment_data,
        assigned_by_id=current_user.id
    )

    return assignments


@router.get("/exams/{exam_id}/assignments", response_model=list[ExamAssignmentInfo])
async def get_exam_assignments(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Get all assignments for an exam."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    assignments = await exam_assignment_crud.get_by_exam(db=db, exam_id=exam_id)
    return assignments


# Candidate endpoints (for taking exams)

@router.get("/my-assignments", response_model=list[ExamAssignmentInfo])
async def get_my_exam_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get exam assignments for current candidate."""
    assignments = await exam_assignment_crud.get_candidate_assignments(
        db=db,
        candidate_id=current_user.id,
        is_active=True
    )
    return assignments


@router.post("/exams/take", response_model=ExamTakeResponse)
async def start_exam(
    take_request: ExamTakeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start taking an exam."""
    exam = await exam_crud.get(db=db, id=take_request.exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.status != ExamStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam is not active"
        )

    # Check if user has assignment (skip for test mode)
    if take_request.assignment_id and not take_request.test_mode:
        assignment = await exam_assignment_crud.get(db=db, id=take_request.assignment_id)
        if not assignment or assignment.candidate_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid assignment"
            )

    # Check for existing active session (skip for test mode)
    active_session = None
    if not take_request.test_mode:
        active_session = await exam_session_crud.get_active_session(
            db=db,
            candidate_id=current_user.id,
            exam_id=take_request.exam_id
        )

    if active_session:
        # Resume existing session
        session = active_session
    else:
        # Create new session
        try:
            # For test mode, create a special test session that doesn't count towards attempts
            if take_request.test_mode:
                session = await exam_session_crud.create_test_session(
                    db=db,
                    candidate_id=current_user.id,
                    exam_id=take_request.exam_id
                )
            else:
                session = await exam_session_crud.create_session(
                    db=db,
                    candidate_id=current_user.id,
                    exam_id=take_request.exam_id,
                    assignment_id=take_request.assignment_id
                )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    # Start session if not already started
    if session.status == SessionStatus.NOT_STARTED:
        session = await exam_session_crud.start_session(db=db, session_id=session.id)

        # Update session with browser info
        if take_request.user_agent or take_request.screen_resolution:
            update_data = {}
            if take_request.user_agent:
                update_data["user_agent"] = take_request.user_agent
            if take_request.screen_resolution:
                update_data["screen_resolution"] = take_request.screen_resolution

            await exam_session_crud.update(db=db, db_obj=session, obj_in=update_data)

    # Get questions (randomized if needed)
    if exam.is_randomized:
        questions = await exam_question_crud.get_randomized_questions(db=db, exam_id=exam.id)
    else:
        questions = await exam_question_crud.get_by_exam(db=db, exam_id=exam.id)

    # Convert to public format (no correct answers exposed)
    public_questions = []
    for q in questions:
        public_q = {
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "order_index": q.order_index,
            "points": q.points,
            "time_limit_seconds": q.time_limit_seconds,
            "is_required": q.is_required,
            "options": q.options,
            "max_length": q.max_length,
            "min_length": q.min_length,
            "rating_scale": q.rating_scale
        }
        public_questions.append(public_q)

    current_question = public_questions[session.current_question_index] if public_questions else None

    return ExamTakeResponse(
        session=session,
        questions=public_questions,
        current_question=current_question,
        time_remaining_seconds=session.time_remaining_seconds,
        can_navigate=True
    )


@router.post("/sessions/{session_id}/answers", response_model=ExamAnswerInfo)
async def submit_answer(
    session_id: int,
    answer_data: ExamAnswerSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit an answer for a question."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if session.status not in [SessionStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not active"
        )

    try:
        answer = await exam_answer_crud.submit_answer(
            db=db,
            session_id=session_id,
            answer_data=answer_data
        )
        return answer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/sessions/{session_id}/complete", response_model=ExamSessionInfo)
async def complete_exam(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Complete an exam session."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if session.status != SessionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not in progress"
        )

    try:
        session = await exam_session_crud.complete_session(
            db=db,
            session_id=session_id,
            calculate_score=True
        )
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sessions/{session_id}/results", response_model=ExamResultSummary)
async def get_exam_results(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get exam results for a completed session."""
    session = await exam_session_crud.get_with_details(db=db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session not completed"
        )

    exam = session.exam
    if not exam.show_results_immediately:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Results not available"
        )

    result_summary = ExamResultSummary(
        session=session,
        answers=session.answers
    )

    # Include questions with correct answers if allowed
    if exam.show_correct_answers:
        questions = await exam_question_crud.get_by_exam(db=db, exam_id=exam.id)
        result_summary.questions = questions

    return result_summary


# Monitoring endpoints

@router.post("/sessions/{session_id}/monitoring", response_model=ExamMonitoringEventInfo)
async def create_monitoring_event(
    session_id: int,
    event_data: ExamMonitoringEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a monitoring event."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    event_data.session_id = session_id
    event = await exam_monitoring_crud.create_event(db=db, event_data=event_data)

    # Update session counters based on event type
    if event_data.event_type == "web_usage":
        session.web_usage_detected = True
        session.web_usage_count += 1
        await db.commit()
    elif event_data.event_type == "face_check_failed":
        session.face_verification_failed = True
        session.face_check_count += 1
        await db.commit()

    return event


@router.post("/sessions/{session_id}/face-verification", response_model=FaceVerificationResponse)
async def submit_face_verification(
    session_id: int,
    face_data: FaceVerificationSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit face verification data."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # TODO: Implement actual face recognition logic
    # For now, return a mock response

    # Create monitoring event
    monitoring_event = ExamMonitoringEventCreate(
        session_id=session_id,
        event_type="face_verification",
        event_data={
            "verification_type": face_data.verification_type,
            "timestamp": face_data.timestamp.isoformat(),
            "confidence_score": 0.95  # Mock value
        },
        severity="info"
    )

    await exam_monitoring_crud.create_event(db=db, event_data=monitoring_event)

    return FaceVerificationResponse(
        verified=True,  # Mock response
        confidence_score=0.95,
        message="Face verification successful",
        requires_human_review=False
    )


# Session management endpoints

@router.get("/sessions/{session_id}", response_model=ExamSessionInfo)
async def get_session_details(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get session details."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return session


@router.get("/exams/{exam_id}/sessions", response_model=ExamSessionListResponse)
async def get_exam_sessions(
    exam_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company)
):
    """Get all sessions for an exam (employer view)."""
    require_roles(current_user, [UserRole.COMPANY_ADMIN, UserRole.COMPANY_RECRUITER])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # This would need to be implemented in CRUD
    # For now, return empty list
    return ExamSessionListResponse(
        sessions=[],
        total=0,
        page=skip // limit + 1,
        page_size=limit,
        has_more=False
    )
