"""CRUD operations for todo extension requests."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.todo_extension_request import TodoExtensionRequest
from app.models.todo import Todo
from app.schemas.todo_extension import (
    TodoExtensionRequestCreate,
    TodoExtensionRequestResponse,
    TodoExtensionValidation
)
from app.utils.constants import ExtensionRequestStatus, TodoStatus


class CRUDTodoExtensionRequest(CRUDBase[TodoExtensionRequest, dict, dict]):
    """CRUD operations for todo extension requests."""

    async def create_extension_request(
        self,
        db: AsyncSession,
        *,
        todo: Todo,
        request_data: TodoExtensionRequestCreate,
        requested_by_id: int
    ) -> TodoExtensionRequest:
        """Create a new extension request."""
        extension_request = TodoExtensionRequest(
            todo_id=todo.id,
            requested_by_id=requested_by_id,
            creator_id=todo.owner_id,
            current_due_date=todo.due_date,
            requested_due_date=request_data.requested_due_date,
            reason=request_data.reason,
            status=ExtensionRequestStatus.PENDING.value
        )
        
        db.add(extension_request)
        await db.commit()
        await db.refresh(extension_request)
        
        # Load relationships
        await db.refresh(
            extension_request,
            ["requested_by", "creator", "todo"]
        )
        
        return extension_request

    async def respond_to_request(
        self,
        db: AsyncSession,
        *,
        request_obj: TodoExtensionRequest,
        response_data: TodoExtensionRequestResponse,
        responded_by_id: int
    ) -> TodoExtensionRequest:
        """Respond to an extension request."""
        request_obj.status = response_data.status.value
        request_obj.response_reason = response_data.response_reason
        request_obj.responded_at = datetime.utcnow()
        request_obj.responded_by_id = responded_by_id
        
        # If approved, update the todo's due date
        if response_data.status == ExtensionRequestStatus.APPROVED:
            todo = await db.get(Todo, request_obj.todo_id)
            if todo:
                todo.due_date = request_obj.requested_due_date
                todo.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(request_obj)
        
        # Load relationships
        await db.refresh(
            request_obj,
            ["requested_by", "creator", "responded_by", "todo"]
        )
        
        return request_obj

    async def get_by_id_with_relationships(
        self,
        db: AsyncSession,
        *,
        request_id: int
    ) -> Optional[TodoExtensionRequest]:
        """Get extension request by ID with all relationships loaded."""
        query = (
            select(TodoExtensionRequest)
            .options(
                selectinload(TodoExtensionRequest.requested_by),
                selectinload(TodoExtensionRequest.creator),
                selectinload(TodoExtensionRequest.responded_by),
                selectinload(TodoExtensionRequest.todo)
            )
            .where(TodoExtensionRequest.id == request_id)
        )
        
        result = await db.execute(query)
        return result.scalars().first()

    async def list_for_creator(
        self,
        db: AsyncSession,
        *,
        creator_id: int,
        status_filter: Optional[ExtensionRequestStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[TodoExtensionRequest], int]:
        """List extension requests for a creator to review."""
        base_query = (
            select(TodoExtensionRequest)
            .options(
                selectinload(TodoExtensionRequest.requested_by),
                selectinload(TodoExtensionRequest.creator),
                selectinload(TodoExtensionRequest.responded_by),
                selectinload(TodoExtensionRequest.todo)
            )
            .where(TodoExtensionRequest.creator_id == creator_id)
        )
        
        if status_filter:
            base_query = base_query.where(TodoExtensionRequest.status == status_filter.value)
        
        # Get total count
        count_query = (
            select(func.count(TodoExtensionRequest.id))
            .where(TodoExtensionRequest.creator_id == creator_id)
        )
        if status_filter:
            count_query = count_query.where(TodoExtensionRequest.status == status_filter.value)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = base_query.order_by(TodoExtensionRequest.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        requests = result.scalars().all()
        
        return list(requests), total

    async def list_for_requester(
        self,
        db: AsyncSession,
        *,
        requester_id: int,
        status_filter: Optional[ExtensionRequestStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[TodoExtensionRequest], int]:
        """List extension requests made by a user."""
        base_query = (
            select(TodoExtensionRequest)
            .options(
                selectinload(TodoExtensionRequest.requested_by),
                selectinload(TodoExtensionRequest.creator),
                selectinload(TodoExtensionRequest.responded_by),
                selectinload(TodoExtensionRequest.todo)
            )
            .where(TodoExtensionRequest.requested_by_id == requester_id)
        )
        
        if status_filter:
            base_query = base_query.where(TodoExtensionRequest.status == status_filter.value)
        
        # Get total count
        count_query = (
            select(func.count(TodoExtensionRequest.id))
            .where(TodoExtensionRequest.requested_by_id == requester_id)
        )
        if status_filter:
            count_query = count_query.where(TodoExtensionRequest.status == status_filter.value)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = base_query.order_by(TodoExtensionRequest.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        requests = result.scalars().all()
        
        return list(requests), total

    async def get_pending_request_for_todo(
        self,
        db: AsyncSession,
        *,
        todo_id: int,
        requested_by_id: int
    ) -> Optional[TodoExtensionRequest]:
        """Check if there's already a pending extension request for this todo by this user."""
        query = (
            select(TodoExtensionRequest)
            .where(
                and_(
                    TodoExtensionRequest.todo_id == todo_id,
                    TodoExtensionRequest.requested_by_id == requested_by_id,
                    TodoExtensionRequest.status == ExtensionRequestStatus.PENDING.value
                )
            )
        )
        
        result = await db.execute(query)
        return result.scalars().first()

    async def validate_extension_request(
        self,
        db: AsyncSession,
        *,
        todo: Todo,
        requested_by_id: int,
        requested_due_date: datetime
    ) -> TodoExtensionValidation:
        """Validate if an extension request can be made."""
        
        # Check if todo has a due date
        if not todo.due_date:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Todo has no due date set"
            )
        
        # Check if todo is completed
        if todo.status == TodoStatus.COMPLETED.value:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Cannot extend completed todo"
            )
        
        # Check if todo is deleted
        if todo.is_deleted:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Cannot extend deleted todo"
            )
        
        # Check if user is the assigned user
        if todo.assigned_user_id != requested_by_id:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Only assigned user can request extension"
            )
        
        # Check if there's already a pending request
        existing_request = await self.get_pending_request_for_todo(
            db, todo_id=todo.id, requested_by_id=requested_by_id
        )
        if existing_request:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="There is already a pending extension request"
            )
        
        # Check if requested date is within allowed range (3 days max)
        max_allowed_date = todo.due_date + timedelta(days=3)
        if requested_due_date > max_allowed_date:
            return TodoExtensionValidation(
                can_request_extension=False,
                max_allowed_due_date=max_allowed_date,
                reason="Extension cannot exceed 3 days from current due date"
            )
        
        # Check if requested date is not in the past
        if requested_due_date <= datetime.utcnow():
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Extension date cannot be in the past"
            )
        
        # Check if requested date is after current due date
        if requested_due_date <= todo.due_date:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Extension date must be after current due date"
            )
        
        return TodoExtensionValidation(
            can_request_extension=True,
            max_allowed_due_date=max_allowed_date
        )

    async def get_statistics_for_creator(
        self,
        db: AsyncSession,
        *,
        creator_id: int
    ) -> dict:
        """Get extension request statistics for a creator."""
        query = (
            select(
                TodoExtensionRequest.status,
                func.count(TodoExtensionRequest.id).label('count')
            )
            .where(TodoExtensionRequest.creator_id == creator_id)
            .group_by(TodoExtensionRequest.status)
        )
        
        result = await db.execute(query)
        stats = {row.status: row.count for row in result}
        
        return {
            'total': sum(stats.values()),
            'pending': stats.get(ExtensionRequestStatus.PENDING.value, 0),
            'approved': stats.get(ExtensionRequestStatus.APPROVED.value, 0),
            'rejected': stats.get(ExtensionRequestStatus.REJECTED.value, 0)
        }


# Create instance
todo_extension_request = CRUDTodoExtensionRequest(TodoExtensionRequest)