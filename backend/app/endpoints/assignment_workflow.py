"""Assignment workflow API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.todo import todo as todo_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.todo import (
    AssignmentReview,
    AssignmentSubmission,
    AssignmentWorkflowResponse,
    TodoListResponse,
    TodoRead,
)
from app.services.todo_permissions import TodoPermissionService

router = APIRouter()


async def _get_todo_or_404(
    db: AsyncSession, *, todo_id: int, current_user: User, allow_deleted: bool = True
):
    """Get todo or raise 404 if not found or not accessible."""
    todo_obj = await todo_crud.get(db, id=todo_id)
    if not todo_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    # Check if user can view this todo
    if not await TodoPermissionService.can_view_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    if not allow_deleted and todo_obj.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo_obj


# Assignment workflow endpoints
@router.post(API_ROUTES.ASSIGNMENTS.PUBLISH, response_model=AssignmentWorkflowResponse)
async def publish_assignment(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Publish an assignment (make it visible to assignee and viewers)."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user owns this todo
    if todo_obj.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can publish assignments",
        )

    # Check if it's an assignment and not already published
    if not todo_obj.is_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assignments can be published",
        )

    if todo_obj.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment is already published",
        )

    todo_obj = await todo_crud.publish_assignment(
        db, todo=todo_obj, published_by=current_user.id
    )
    return AssignmentWorkflowResponse(
        success=True,
        message="Assignment published successfully",
        todo=TodoRead.model_validate(todo_obj),
    )


@router.post(
    API_ROUTES.ASSIGNMENTS.MAKE_DRAFT, response_model=AssignmentWorkflowResponse
)
async def make_assignment_draft(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Make assignment a draft (hide from assignee and viewers)."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user owns this todo
    if todo_obj.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can make assignments draft",
        )

    # Check if it's an assignment and not already draft
    if not todo_obj.is_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assignments can be made draft",
        )

    if todo_obj.is_draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment is already a draft",
        )

    todo_obj = await todo_crud.make_draft(db, todo=todo_obj, updated_by=current_user.id)
    return AssignmentWorkflowResponse(
        success=True, message="Assignment made draft successfully", todo=TodoRead.model_validate(todo_obj)
    )


@router.post(API_ROUTES.ASSIGNMENTS.SUBMIT, response_model=AssignmentWorkflowResponse)
async def submit_assignment(
    todo_id: int,
    submission_data: AssignmentSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit assignment for review."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user is the owner of this todo
    if todo_obj.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can submit assignments",
        )

    # Check if it's an assignment and can be edited
    if not todo_obj.is_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assignments can be submitted",
        )

    if not todo_obj.can_be_edited_by_assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment has already been submitted or is under review",
        )

    todo_obj = await todo_crud.submit_assignment(
        db, todo=todo_obj, submitted_by=current_user.id, assignee_memo=submission_data.assignee_memo or ""
    )
    return AssignmentWorkflowResponse(
        success=True,
        message="Assignment submitted for review successfully",
        todo=TodoRead.model_validate(todo_obj),
    )


@router.post(API_ROUTES.ASSIGNMENTS.REVIEW, response_model=AssignmentWorkflowResponse)
async def review_assignment(
    todo_id: int,
    review_data: AssignmentReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Review and assess an assignment."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user owns this todo
    if todo_obj.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can review assignments",
        )

    # Check if it's an assignment and is in submitted state
    if not todo_obj.is_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assignments can be reviewed",
        )

    if todo_obj.assignment_status not in ["submitted", "under_review"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment must be submitted before it can be reviewed",
        )

    todo_obj = await todo_crud.review_assignment(
        db,
        todo=todo_obj,
        reviewer_id=current_user.id,
        approved=review_data.approved,
        assessment=review_data.assessment or "",
    )

    status_text = "approved" if review_data.approved else "rejected"
    return AssignmentWorkflowResponse(
        success=True, message=f"Assignment {status_text} successfully", todo=TodoRead.model_validate(todo_obj)
    )


@router.get(API_ROUTES.ASSIGNMENTS.PENDING_REVIEW, response_model=list[TodoRead])
async def get_assignments_for_review(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get assignments that need review by the current user."""
    assignments = await todo_crud.get_assignments_for_review(
        db, reviewer_id=current_user.id
    )
    return assignments


@router.get(API_ROUTES.ASSIGNMENTS.BASE, response_model=TodoListResponse)
async def list_user_assignments(
    visibility_status: str = Query(None, description="Filter by visibility status"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List assignments for the current user (as assignee or viewer)."""
    assignments, total = await todo_crud.get_user_assignments(
        db,
        user_id=current_user.id,
        visibility_status=visibility_status,
        limit=limit,
        offset=offset,
    )
    return TodoListResponse(
        items=[TodoRead.model_validate(a) for a in assignments], total=total
    )
