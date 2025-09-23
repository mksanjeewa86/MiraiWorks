"""API endpoints for MBTI personality test."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.mbti import mbti_test, mbti_question
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.mbti import (
    MBTIQuestionRead,
    MBTIAnswerSubmit,
    MBTITestStart,
    MBTITestSubmit,
    MBTITestResult,
    MBTITestSummary,
    MBTITestProgress,
    MBTITypeInfo,
    get_mbti_type_info
)
from app.services.todo_permissions import TodoPermissionService
from app.utils.constants import UserRole as UserRoleEnum, MBTITestStatus

router = APIRouter()


async def _check_candidate_permission(current_user: User, db: AsyncSession):
    """Check if user has candidate role."""
    user_roles = await TodoPermissionService.get_user_roles(db, current_user.id)
    if UserRoleEnum.CANDIDATE.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MBTI test is only available for candidates"
        )


@router.post("/start", response_model=MBTITestProgress)
async def start_mbti_test(
    test_data: MBTITestStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start or restart MBTI personality test."""
    await _check_candidate_permission(current_user, db)
    
    # Create or get existing test
    test = await mbti_test.create_or_get_test(
        db, user_id=current_user.id, test_data=test_data
    )
    
    # Get progress information
    progress = await mbti_test.get_test_progress(db, user_id=current_user.id)
    
    return MBTITestProgress(**progress)


@router.get("/questions", response_model=List[dict])
async def get_mbti_questions(
    language: str = Query("ja", pattern="^(en|ja)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get MBTI test questions."""
    await _check_candidate_permission(current_user, db)
    
    # Check if user has started the test
    user_test = await mbti_test.get_by_user_id(db, user_id=current_user.id)
    if not user_test or user_test.status == MBTITestStatus.NOT_TAKEN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please start the test first"
        )
    
    questions = await mbti_question.get_questions_for_test(db, language=language)
    return questions


@router.post("/answer", response_model=MBTITestProgress)
async def submit_mbti_answer(
    answer_data: MBTIAnswerSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit an answer for a single question."""
    await _check_candidate_permission(current_user, db)
    
    # Get user's test
    user_test = await mbti_test.get_by_user_id(db, user_id=current_user.id)
    if not user_test or user_test.status != MBTITestStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active test found. Please start the test first."
        )
    
    # Submit answer
    await mbti_test.submit_answer(
        db, 
        test=user_test, 
        question_id=answer_data.question_id, 
        answer=answer_data.answer
    )
    
    # Get updated progress
    progress = await mbti_test.get_test_progress(db, user_id=current_user.id)
    return MBTITestProgress(**progress)


@router.post("/submit", response_model=MBTITestResult)
async def submit_mbti_test(
    test_submission: MBTITestSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit complete MBTI test and get results."""
    await _check_candidate_permission(current_user, db)
    
    # Get user's test
    user_test = await mbti_test.get_by_user_id(db, user_id=current_user.id)
    if not user_test or user_test.status != MBTITestStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active test found. Please start the test first."
        )
    
    # Validate all questions are answered
    total_questions = await mbti_question.get_question_count(db)
    if len(test_submission.answers) != total_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please answer all {total_questions} questions. You answered {len(test_submission.answers)}."
        )
    
    # Complete the test
    completed_test = await mbti_test.complete_test(
        db, test=user_test, answers=test_submission.answers
    )
    
    return MBTITestResult.model_validate(completed_test)


@router.get("/result", response_model=MBTITestResult)
async def get_mbti_result(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get MBTI test result for current user."""
    await _check_candidate_permission(current_user, db)
    
    user_test = await mbti_test.get_by_user_id(db, user_id=current_user.id)
    if not user_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No MBTI test found for this user"
        )
    
    return MBTITestResult.model_validate(user_test)


@router.get("/summary", response_model=MBTITestSummary)
async def get_mbti_summary(
    language: str = Query("ja", pattern="^(en|ja)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get MBTI test summary with type information."""
    await _check_candidate_permission(current_user, db)
    
    user_test = await mbti_test.get_by_user_id(db, user_id=current_user.id)
    if not user_test or not user_test.is_completed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed MBTI test found for this user"
        )
    
    # Get type information
    type_info = get_mbti_type_info(user_test.mbti_type)
    if not type_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid MBTI type in database"
        )
    
    return MBTITestSummary(
        mbti_type=user_test.mbti_type,
        completed_at=user_test.completed_at,
        dimension_preferences=user_test.dimension_preferences,
        strength_scores=user_test.strength_scores,
        type_name_en=type_info.name_en,
        type_name_ja=type_info.name_ja,
        type_description_en=type_info.description_en,
        type_description_ja=type_info.description_ja,
        temperament=type_info.temperament
    )


@router.get("/progress", response_model=MBTITestProgress)
async def get_mbti_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current test progress."""
    await _check_candidate_permission(current_user, db)
    
    progress = await mbti_test.get_test_progress(db, user_id=current_user.id)
    if not progress:
        # Return default progress for user who hasn't started
        return MBTITestProgress(
            status=MBTITestStatus.NOT_TAKEN,
            completion_percentage=0,
            current_question=None,
            total_questions=60,
            started_at=None
        )
    
    return MBTITestProgress(**progress)


@router.get("/types", response_model=List[MBTITypeInfo])
async def get_all_mbti_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get information about all MBTI types."""
    # This endpoint can be accessed by any authenticated user
    from app.schemas.mbti import MBTI_TYPE_INFO
    return list(MBTI_TYPE_INFO.values())


@router.get("/types/{mbti_type}", response_model=MBTITypeInfo)
async def get_mbti_type_details(
    mbti_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed information about a specific MBTI type."""
    type_info = get_mbti_type_info(mbti_type.upper())
    if not type_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MBTI type '{mbti_type}' not found"
        )
    
    return type_info


# Admin endpoints for managing questions
@router.post("/admin/questions/bulk", response_model=List[MBTIQuestionRead])
async def bulk_create_questions(
    questions_data: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk create MBTI questions (admin only)."""
    # Check if user is admin
    user_roles = await TodoPermissionService.get_user_roles(db, current_user.id)
    if UserRoleEnum.COMPANY_ADMIN.value not in user_roles and UserRoleEnum.SUPER_ADMIN.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    questions = await mbti_question.bulk_create_questions(db, questions_data)
    return [MBTIQuestionRead.model_validate(q) for q in questions]