import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.exam import exam as exam_crud
from app.crud.exam import exam_answer as exam_answer_crud
from app.crud.exam import exam_assignment as exam_assignment_crud
from app.crud.exam import exam_monitoring as exam_monitoring_crud
from app.crud.exam import exam_question as exam_question_crud
from app.crud.exam import exam_session as exam_session_crud
from app.crud.user import user as user_crud
from app.database import get_db
from app.dependencies import get_current_active_user, get_current_user_with_company
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
    ExamStatus,
    ExamTakeRequest,
    ExamTakeResponse,
    ExamUpdate,
    FaceVerificationResponse,
    FaceVerificationSubmit,
    HybridExamCreate,
    HybridExamResponse,
    SessionStatus,
)
from app.services.exam_email_service import exam_email_service
from app.services.exam_export_service import exam_export_service
from app.services.exam_todo_service import exam_todo_service
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter()


# Exam management endpoints (for employers)


@router.post(API_ROUTES.EXAMS.BASE, response_model=ExamInfo)
async def create_exam(
    exam_data: ExamCreate,
    questions_data: list[ExamQuestionCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new exam with questions.

    System admins can create exams for any company (global exams).
    Company admins/recruiters can only create exams for their own company.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    # System admin can create exams for any company or create global exams
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Handle exam creation based on user role
    if is_system_admin:
        # System admin can:
        # 1. Create global exam (company_id = None, is_public must be True)
        # 2. Create exam for any specific company
        if exam_data.company_id is None:
            # Creating global exam - must be public
            if not exam_data.is_public:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Global exams must be public",
                )
        # else: creating for specific company - allowed
    else:
        # Company admin/recruiter restrictions
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be associated with a company",
            )

        if exam_data.company_id and exam_data.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create exam for different company",
            )

        # Force company_id for company admins/recruiters
        exam_data.company_id = current_user.company_id

    if not questions_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one question is required",
        )

    try:
        exam = await exam_crud.create_with_questions(
            db=db,
            exam_data=exam_data,
            questions_data=questions_data,
            created_by_id=current_user.id,
        )
        return exam
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(API_ROUTES.EXAMS.HYBRID, response_model=HybridExamResponse)
async def create_hybrid_exam(
    hybrid_data: HybridExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a hybrid exam with custom questions + randomly selected questions from question banks.

    Example use case:
    - Company creates 10 custom questions
    - Selects 20 random questions from SPI question bank (verbal section, medium difficulty)
    - Final exam has 30 questions total

    System admins can create hybrid exams for any company.
    Company admins/recruiters can only create hybrid exams for their own company.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    # System admin can create exams for any company
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Verify company access for non-system admins
    if not is_system_admin:
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be associated with a company",
            )

        if (
            hybrid_data.exam_data.company_id
            and hybrid_data.exam_data.company_id != current_user.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create exam for different company",
            )

        # Force company_id for company admins
        hybrid_data.exam_data.company_id = current_user.company_id

    # Validate has questions
    if not hybrid_data.validate_has_questions():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one custom question or template selection is required",
        )

    try:
        exam, metadata = await exam_crud.create_hybrid_exam(
            db=db,
            hybrid_data=hybrid_data,
            created_by_id=current_user.id,
        )

        # Convert exam to ExamInfo
        exam_info = ExamInfo.model_validate(exam)

        return HybridExamResponse(
            exam=exam_info,
            total_questions=metadata["total_questions"],
            custom_count=metadata["custom_count"],
            template_count=metadata["template_count"],
            selection_rules=metadata["selection_rules"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hybrid exam: {str(e)}",
        )


@router.get(API_ROUTES.EXAMS.BASE, response_model=ExamListResponse)
async def get_company_exams(
    status_filter: ExamStatus | None = Query(None, alias="status"),
    company_id: int | None = Query(
        None, description="Filter by company (system admin only)"
    ),
    include_global: bool = Query(True, description="Include global and public exams"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get exams for current user's company or all exams (system admin).

    System admins can view all exams or filter by company.
    Company admins/recruiters see their company's exams + global/public exams.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    # Check if user is system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Determine which company_id to filter by
    if is_system_admin:
        # System admin can view all exams or filter by specific company
        filter_company_id = company_id
    else:
        # Company admin/recruiter can only view their own company's exams
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be associated with a company",
            )
        filter_company_id = current_user.company_id

    exams = await exam_crud.get_by_company(
        db=db,
        company_id=filter_company_id,
        status=status_filter,
        skip=skip,
        limit=limit,
        include_public=include_global,  # Explicitly pass the parameter
    )

    total = len(exams)  # For simplicity, could be optimized with count query

    return ExamListResponse(
        exams=exams,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(exams) == limit,
    )


@router.get(API_ROUTES.EXAMS.BY_ID, response_model=ExamInfo)
async def get_exam_details(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed exam information.

    System admins can view any exam.
    Company admins can view:
    - Their own company's exams
    - Global/public exams (for cloning/assignment)
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    exam = await exam_crud.get_with_details(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Check if user is system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Verify access permissions
    if not is_system_admin:
        # Company admins can view:
        # 1. Own company's exams
        # 2. Global public exams
        # 3. Public exams from other companies
        can_view = (
            exam.company_id == current_user.company_id  # Own company's exam
            or (exam.company_id is None and exam.is_public)  # Global public exam
            or exam.is_public  # Any public exam
        )

        if not can_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this exam",
            )

    return exam


@router.put(API_ROUTES.EXAMS.BY_ID, response_model=ExamInfo)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update exam details.

    System admins can update any exam.
    Company admins can only update their own company's exams.
    Global exams (company_id=NULL) can only be edited by system admins.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Check if user is system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Verify access permissions
    if not is_system_admin:
        # Global exams cannot be edited by company admins
        if exam.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Global exams can only be edited by system admins. Clone the exam to customize it.",
            )

        if not current_user.company_id or exam.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    exam = await exam_crud.update(db=db, db_obj=exam, obj_in=exam_data)
    return exam


@router.delete(API_ROUTES.EXAMS.BY_ID)
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an exam.

    System admins can delete any exam.
    Company admins can only delete their own company's exams.
    Global exams (company_id=NULL) can only be deleted by system admins.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Check if user is system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Verify access permissions
    if not is_system_admin:
        # Global exams cannot be deleted by company admins
        if exam.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Global exams can only be deleted by system admins",
            )

        if not current_user.company_id or exam.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    await exam_crud.remove(db=db, id=exam_id)
    return {"message": "Exam deleted successfully"}


@router.post(API_ROUTES.EXAMS.CLONE, response_model=ExamInfo)
async def clone_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Clone an exam to company's exam library.

    Allows company admins to copy global/public exams to their company.
    The cloned exam will have company_id set to the current user's company.
    All questions are copied to the new exam.
    """
    require_roles(current_user, [UserRole.ADMIN])

    # Get the source exam
    source_exam = await exam_crud.get(db=db, id=exam_id)
    if not source_exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Verify the exam can be cloned
    # Company admins can only clone:
    # 1. Global/public exams (company_id = NULL, is_public = True)
    # 2. Public exams from other companies (is_public = True)
    if source_exam.company_id == current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot clone your own company's exam. Use duplicate instead.",
        )

    if not source_exam.is_public and source_exam.company_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This exam is not public and cannot be cloned",
        )

    # Get all questions from source exam
    source_questions = await exam_question_crud.get_by_exam(db=db, exam_id=exam_id)

    # Prepare cloned exam data
    from app.schemas.exam import ExamCreate, ExamQuestionCreate

    exam_create_data = ExamCreate(
        title=f"{source_exam.title} (Copy)",
        description=source_exam.description,
        exam_type=source_exam.exam_type,
        company_id=current_user.company_id,  # Set to current company
        time_limit_minutes=source_exam.time_limit_minutes,
        max_attempts=source_exam.max_attempts,
        passing_score=source_exam.passing_score,
        is_randomized=source_exam.is_randomized,
        is_public=False,  # Cloned exams are private by default
        allow_web_usage=source_exam.allow_web_usage,
        monitor_web_usage=source_exam.monitor_web_usage,
        require_face_verification=source_exam.require_face_verification,
        face_check_interval_minutes=source_exam.face_check_interval_minutes,
        show_results_immediately=source_exam.show_results_immediately,
        show_correct_answers=source_exam.show_correct_answers,
        show_score=source_exam.show_score,
        instructions=source_exam.instructions,
    )

    # Prepare cloned questions data
    questions_create_data = [
        ExamQuestionCreate(
            exam_id=0,  # Will be set during creation
            question_text=q.question_text,
            question_type=q.question_type,
            order_index=q.order_index,
            points=q.points,
            time_limit_seconds=q.time_limit_seconds,
            is_required=q.is_required,
            options=q.options,
            correct_answers=q.correct_answers,
            max_length=q.max_length,
            min_length=q.min_length,
            rating_scale=q.rating_scale,
            explanation=q.explanation,
            tags=q.tags,
        )
        for q in source_questions
    ]

    # Create the cloned exam with questions
    try:
        cloned_exam = await exam_crud.create_with_questions(
            db=db,
            exam_data=exam_create_data,
            questions_data=questions_create_data,
            created_by_id=current_user.id,
        )
        return cloned_exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to clone exam: {str(e)}",
        )


@router.get(API_ROUTES.EXAMS.STATISTICS, response_model=dict[str, Any])
async def get_exam_statistics(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Get comprehensive exam statistics."""
    require_roles(current_user, [UserRole.ADMIN])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    stats = await exam_crud.get_statistics(db=db, exam_id=exam_id)
    return stats


# Question management endpoints


@router.get(API_ROUTES.EXAMS.QUESTIONS, response_model=list[ExamQuestionInfo])
async def get_exam_questions(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Get all questions for an exam."""
    require_roles(current_user, [UserRole.ADMIN])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    questions = await exam_question_crud.get_by_exam(db=db, exam_id=exam_id)
    return questions


@router.post(API_ROUTES.EXAMS.QUESTIONS, response_model=ExamQuestionInfo)
async def add_exam_question(
    exam_id: int,
    question_data: ExamQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Add a new question to an exam.

    Company admins can only add questions to their own company's exams.
    Global exams (company_id=NULL) cannot have questions added by company admins.
    """
    require_roles(current_user, [UserRole.ADMIN])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Global exams cannot be modified by company admins
    if exam.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add questions to global exams. Clone the exam first.",
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    question_data.exam_id = exam_id
    question = await exam_question_crud.create(db=db, obj_in=question_data)
    return question


@router.put(API_ROUTES.EXAMS.QUESTION_BY_ID, response_model=ExamQuestionInfo)
async def update_exam_question(
    question_id: int,
    question_data: ExamQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Update an exam question.

    Company admins can only update questions in their own company's exams.
    Global exam questions cannot be edited by company admins.
    """
    require_roles(current_user, [UserRole.ADMIN])

    question = await exam_question_crud.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    # Verify company access through exam
    exam = await exam_crud.get(db=db, id=question.exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Global exams cannot be modified by company admins
    if exam.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update questions in global exams",
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    question = await exam_question_crud.update(
        db=db, db_obj=question, obj_in=question_data
    )
    return question


@router.delete(API_ROUTES.EXAMS.QUESTION_BY_ID)
async def delete_exam_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Delete an exam question.

    Company admins can only delete questions in their own company's exams.
    Global exam questions cannot be deleted by company admins.
    """
    require_roles(current_user, [UserRole.ADMIN])

    question = await exam_question_crud.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    # Verify company access through exam
    exam = await exam_crud.get(db=db, id=question.exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Global exams cannot be modified by company admins
    if exam.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete questions from global exams",
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await exam_question_crud.remove(db=db, id=question_id)
    return {"message": "Question deleted successfully"}


# Assignment management endpoints


@router.post(API_ROUTES.EXAMS.ASSIGNMENTS, response_model=list[ExamAssignmentInfo])
async def create_exam_assignments(
    exam_id: int,
    assignment_data: ExamAssignmentCreate,
    send_email: bool = Query(
        True, description="Send email notifications to candidates"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Assign exam to candidates and optionally send email notifications.

    Company admins can assign:
    1. Their own company's exams
    2. Global/public exams (company_id = NULL and is_public = True)
    3. Public exams from other companies (is_public = True)
    """
    require_roles(current_user, [UserRole.ADMIN])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Verify exam can be assigned
    # Allow if:
    # 1. Own company's exam (exam.company_id == current_user.company_id)
    # 2. Global exam (exam.company_id is NULL and exam.is_public is True)
    # 3. Public exam from another company (exam.is_public is True)
    can_assign = (
        exam.company_id == current_user.company_id  # Own company's exam
        or (exam.company_id is None and exam.is_public)  # Global public exam
        or exam.is_public  # Any public exam
    )

    if not can_assign:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign this exam. It is not public and does not belong to your company.",
        )

    assignment_data.exam_id = exam_id
    assignments = await exam_assignment_crud.create_assignments(
        db=db, assignment_data=assignment_data, assigned_by_id=current_user.id
    )

    # Send email notifications if requested
    if send_email and assignments:
        # Get candidate users
        candidate_ids = [a.candidate_id for a in assignments]
        candidates = []
        for candidate_id in candidate_ids:
            candidate = await user_crud.get(db=db, id=candidate_id)
            if candidate:
                candidates.append(candidate)

        # Send emails in background (don't block the response)
        base_url = "https://miraiworks.com"  # TODO: Get from config
        for assignment, candidate in zip(assignments, candidates):
            try:
                exam_url = f"{base_url}/exams/take/{exam_id}?assignment={assignment.id}"
                await exam_email_service.send_exam_assignment_notification(
                    candidate=candidate,
                    exam=exam,
                    assignment_id=assignment.id,
                    due_date=assignment_data.due_date,
                    assigned_by=current_user,
                    exam_url=exam_url,
                )
            except Exception as e:
                # Log error but don't fail the assignment
                print(f"Failed to send email to {candidate.email}: {e}")

    return assignments


@router.get(API_ROUTES.EXAMS.ASSIGNMENTS, response_model=list[ExamAssignmentInfo])
async def get_exam_assignments(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Get all assignments for an exam."""
    require_roles(current_user, [UserRole.ADMIN])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    assignments = await exam_assignment_crud.get_by_exam(db=db, exam_id=exam_id)
    return assignments


# Candidate endpoints (for taking exams)


@router.get(API_ROUTES.EXAMS.MY_ASSIGNMENTS, response_model=list[ExamAssignmentInfo])
async def get_my_exam_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get exam assignments for current candidate."""
    assignments = await exam_assignment_crud.get_candidate_assignments(
        db=db, candidate_id=current_user.id, is_active=True
    )
    return assignments


@router.post(API_ROUTES.EXAMS.TAKE, response_model=ExamTakeResponse)
async def start_exam(
    take_request: ExamTakeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start taking an exam."""
    exam = await exam_crud.get(db=db, id=take_request.exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    if exam.status != ExamStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Exam is not active"
        )

    # Check if user has assignment (skip for test mode)
    if take_request.assignment_id and not take_request.test_mode:
        assignment = await exam_assignment_crud.get(
            db=db, id=take_request.assignment_id
        )
        if not assignment or assignment.candidate_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid assignment"
            )

    # Check for existing active session (skip for test mode)
    active_session = None
    if not take_request.test_mode:
        active_session = await exam_session_crud.get_active_session(
            db=db, candidate_id=current_user.id, exam_id=take_request.exam_id
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
                    db=db, candidate_id=current_user.id, exam_id=take_request.exam_id
                )
            else:
                session = await exam_session_crud.create_session(
                    db=db,
                    candidate_id=current_user.id,
                    exam_id=take_request.exam_id,
                    assignment_id=take_request.assignment_id,
                )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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
        questions = await exam_question_crud.get_randomized_questions(
            db=db, exam_id=exam.id
        )
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
            "rating_scale": q.rating_scale,
        }
        public_questions.append(public_q)

    current_question = (
        public_questions[session.current_question_index] if public_questions else None
    )

    return ExamTakeResponse(
        session=session,
        questions=public_questions,
        current_question=current_question,
        time_remaining_seconds=session.time_remaining_seconds,
        can_navigate=True,
    )


@router.post(API_ROUTES.EXAMS.SESSION_ANSWERS, response_model=ExamAnswerInfo)
async def submit_answer(
    session_id: int,
    answer_data: ExamAnswerSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit an answer for a question."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    if session.status not in [SessionStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active"
        )

    try:
        answer = await exam_answer_crud.submit_answer(
            db=db, session_id=session_id, answer_data=answer_data
        )
        return answer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(API_ROUTES.EXAMS.SESSION_COMPLETE, response_model=ExamSessionInfo)
async def complete_exam(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Complete an exam session."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    if session.status != SessionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not in progress"
        )

    try:
        session = await exam_session_crud.complete_session(
            db=db, session_id=session_id, calculate_score=True
        )

        # If this exam was assigned via workflow TODO, auto-complete the TODO
        if session.assignment_id:
            try:
                await exam_todo_service.on_exam_completed(
                    db=db, exam_assignment_id=session.assignment_id
                )
            except Exception as e:
                # Log error but don't fail the exam completion
                print(f"Failed to auto-complete exam TODO: {str(e)}")

        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(API_ROUTES.EXAMS.SESSION_RESULTS, response_model=ExamResultSummary)
async def get_exam_results(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get exam results for a completed session."""
    session = await exam_session_crud.get_with_details(db=db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Session not completed"
        )

    exam = session.exam
    if not exam.show_results_immediately:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Results not available"
        )

    result_summary = ExamResultSummary(session=session, answers=session.answers)

    # Include questions with correct answers if allowed
    if exam.show_correct_answers:
        questions = await exam_question_crud.get_by_exam(db=db, exam_id=exam.id)
        result_summary.questions = questions

    return result_summary


# Monitoring endpoints


@router.post(
    API_ROUTES.EXAMS.SESSION_MONITORING, response_model=ExamMonitoringEventInfo
)
async def create_monitoring_event(
    session_id: int,
    event_data: ExamMonitoringEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a monitoring event."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
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


@router.post(
    API_ROUTES.EXAMS.SESSION_FACE_VERIFICATION, response_model=FaceVerificationResponse
)
async def submit_face_verification(
    session_id: int,
    face_data: FaceVerificationSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit face verification data."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
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
            "confidence_score": 0.95,  # Mock value
        },
        severity="info",
    )

    await exam_monitoring_crud.create_event(db=db, event_data=monitoring_event)

    return FaceVerificationResponse(
        verified=True,  # Mock response
        confidence_score=0.95,
        message="Face verification successful",
        requires_human_review=False,
    )


# Session management endpoints


@router.get(API_ROUTES.EXAMS.SESSION_BY_ID, response_model=ExamSessionInfo)
async def get_session_details(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get session details."""
    session = await exam_session_crud.get(db=db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return session


@router.get(API_ROUTES.EXAMS.SESSIONS, response_model=ExamSessionListResponse)
async def get_exam_sessions(
    exam_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_company),
):
    """Get all sessions for an exam (employer view)."""
    require_roles(current_user, [UserRole.ADMIN])

    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    if exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # This would need to be implemented in CRUD
    # For now, return empty list
    return ExamSessionListResponse(
        sessions=[], total=0, page=skip // limit + 1, page_size=limit, has_more=False
    )


# Export endpoints


@router.get(API_ROUTES.EXAMS.EXPORT_PDF)
async def export_exam_results_pdf(
    exam_id: int,
    include_answers: bool = Query(False, description="Include individual answers"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Export exam results as PDF."""
    require_roles(current_user, [UserRole.ADMIN])

    # Check if system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Get exam
    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Check permissions
    if not is_system_admin and exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Get all completed sessions for this exam
    sessions = await exam_session_crud.get_sessions_by_exam(db=db, exam_id=exam_id)

    # Generate PDF
    pdf_bytes = exam_export_service.generate_pdf_report(
        exam=exam, sessions=sessions, include_answers=include_answers
    )

    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=exam_{exam_id}_results.pdf"
        },
    )


@router.get(API_ROUTES.EXAMS.EXPORT_EXCEL)
async def export_exam_results_excel(
    exam_id: int,
    include_answers: bool = Query(False, description="Include individual answers"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Export exam results as Excel."""
    require_roles(current_user, [UserRole.ADMIN])

    # Check if system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Get exam
    exam = await exam_crud.get(db=db, id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Check permissions
    if not is_system_admin and exam.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Get all completed sessions for this exam
    sessions = await exam_session_crud.get_sessions_by_exam(db=db, exam_id=exam_id)

    # Generate Excel
    excel_bytes = exam_export_service.generate_excel_report(
        exam=exam, sessions=sessions, include_answers=include_answers
    )

    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=exam_{exam_id}_results.xlsx"
        },
    )
