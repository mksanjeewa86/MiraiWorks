"""API endpoints for todo extension requests."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.todo import todo as todo_crud
from app.crud.todo_extension_request import todo_extension_request
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.todo import TodoExtensionValidation
from app.schemas.todo_extension import (
    TodoExtensionRequestCreate,
    TodoExtensionRequestList,
    TodoExtensionRequestRead,
    TodoExtensionRequestResponse,
)
from app.services.todo_extension_notification_service import (
    todo_extension_notification_service,
)
from app.services.todo_permissions import TodoPermissionService
from app.utils.constants import ExtensionRequestStatus

router = APIRouter()


async def _get_extension_request_or_404(
    db: AsyncSession, *, request_id: int, current_user: User
) -> object:
    """Get extension request by ID and check permissions."""
    extension_request_obj = await todo_extension_request.get_by_id_with_relationships(
        db, request_id=request_id
    )

    if not extension_request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension request not found"
        )

    # Check if user can view this extension request
    if not await TodoPermissionService.can_view_extension_request(
        db, current_user.id, extension_request_obj
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension request not found"
        )

    return extension_request_obj


@router.post(API_ROUTES.TODO_EXTENSIONS.CREATE, response_model=TodoExtensionRequestRead)
async def create_extension_request(
    todo_id: int,
    request_data: TodoExtensionRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new extension request for a todo."""
    # Get todo and check if user can request extension
    todo_obj = await todo_crud.get(db, id=todo_id)
    if not todo_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    # Check basic permission to request extension
    if not await TodoPermissionService.can_request_extension(
        db, current_user.id, todo_obj
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to request extension for this todo",
        )

    # Validate the extension request
    validation = await todo_extension_request.validate_extension_request(
        db,
        todo=todo_obj,
        requested_by_id=current_user.id,
        requested_due_date=request_data.requested_due_date,
    )

    if not validation.can_request_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation.reason or "Extension request is not valid",
        )

    # Create the extension request
    extension_request_obj = await todo_extension_request.create_extension_request(
        db, todo=todo_obj, request_data=request_data, requested_by_id=current_user.id
    )

    # Send notifications and emails
    await todo_extension_notification_service.notify_extension_request_created(
        db, extension_request_obj
    )

    return extension_request_obj


@router.get(API_ROUTES.TODO_EXTENSIONS.VALIDATE, response_model=TodoExtensionValidation)
async def validate_extension_request(
    todo_id: int,
    requested_due_date: str = Query(
        ..., description="Requested due date in ISO format"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Validate if an extension request can be made for a todo."""
    from datetime import datetime

    # Parse the requested due date
    try:
        requested_date = datetime.fromisoformat(
            requested_due_date.replace("Z", "+00:00")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format.",
        ) from e

    # Get todo
    todo_obj = await todo_crud.get(db, id=todo_id)
    if not todo_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    # Check basic permission to request extension
    if not await TodoPermissionService.can_request_extension(
        db, current_user.id, todo_obj
    ):
        return TodoExtensionValidation(
            can_request_extension=False,
            reason="You don't have permission to request extension for this todo",
        )

    # Validate the extension request
    validation = await todo_extension_request.validate_extension_request(
        db,
        todo=todo_obj,
        requested_by_id=current_user.id,
        requested_due_date=requested_date,
    )

    return validation


@router.put(API_ROUTES.TODO_EXTENSIONS.RESPOND, response_model=TodoExtensionRequestRead)
async def respond_to_extension_request(
    request_id: int,
    response_data: TodoExtensionRequestResponse,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Respond to an extension request (approve or reject)."""
    extension_request_obj = await _get_extension_request_or_404(
        db, request_id=request_id, current_user=current_user
    )

    # Check if user can respond to this request
    if not await TodoPermissionService.can_respond_to_extension(
        db, current_user.id, extension_request_obj
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to respond to this extension request",
        )

    # Check if request is still pending
    if extension_request_obj.status != ExtensionRequestStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extension request has already been responded to",
        )

    # Respond to the request
    extension_request_obj = await todo_extension_request.respond_to_request(
        db,
        request_obj=extension_request_obj,
        response_data=response_data,
        responded_by_id=current_user.id,
    )

    # Send notifications and emails
    await todo_extension_notification_service.notify_extension_request_responded(
        db, extension_request_obj
    )

    return extension_request_obj


@router.get(
    API_ROUTES.TODO_EXTENSIONS.MY_REQUESTS, response_model=TodoExtensionRequestList
)
async def list_my_extension_requests(
    status_filter: ExtensionRequestStatus = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List extension requests made by the current user."""
    requests, total = await todo_extension_request.list_for_requester(
        db,
        requester_id=current_user.id,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )

    # Get statistics
    stats = await todo_extension_request.get_statistics_for_creator(
        db, creator_id=current_user.id
    )

    return TodoExtensionRequestList(
        items=requests,
        total=total,
        pending_count=stats.get("pending", 0),
        approved_count=stats.get("approved", 0),
        rejected_count=stats.get("rejected", 0),
    )


@router.get(
    API_ROUTES.TODO_EXTENSIONS.TO_REVIEW, response_model=TodoExtensionRequestList
)
async def list_extension_requests_to_review(
    status_filter: ExtensionRequestStatus = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List extension requests that the current user needs to review."""
    requests, total = await todo_extension_request.list_for_creator(
        db,
        creator_id=current_user.id,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )

    # Get statistics
    stats = await todo_extension_request.get_statistics_for_creator(
        db, creator_id=current_user.id
    )

    return TodoExtensionRequestList(
        items=requests,
        total=total,
        pending_count=stats.get("pending", 0),
        approved_count=stats.get("approved", 0),
        rejected_count=stats.get("rejected", 0),
    )


@router.get(API_ROUTES.TODO_EXTENSIONS.BY_ID, response_model=TodoExtensionRequestRead)
async def get_extension_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get details of a specific extension request."""
    extension_request_obj = await _get_extension_request_or_404(
        db, request_id=request_id, current_user=current_user
    )

    return extension_request_obj
