"""CRUD operations for todo extension requests."""

from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.todo import Todo
from app.models.todo_extension_request import TodoExtensionRequest
from app.schemas.todo_extension import (
    TodoExtensionRequestCreate,
    TodoExtensionRequestResponse,
    TodoExtensionValidation,
)
from app.utils.constants import ExtensionRequestStatus, TodoStatus
from app.utils.datetime_utils import get_utc_now


class CRUDTodoExtensionRequest(CRUDBase[TodoExtensionRequest, dict, dict]):
    """CRUD operations for todo extension requests."""

    async def create_extension_request(
        self,
        db: AsyncSession,
        *,
        todo: Todo,
        request_data: TodoExtensionRequestCreate,
        requested_by_id: int,
    ) -> TodoExtensionRequest:
        """Create a new extension request."""
        now = get_utc_now()
        extension_request = TodoExtensionRequest(
            todo_id=todo.id,
            requested_by_id=requested_by_id,
            creator_id=todo.owner_id,
            requested_due_date=request_data.requested_due_date,
            reason=request_data.reason,
            status=ExtensionRequestStatus.PENDING.value,
            created_at=now,
            updated_at=now,
        )

        db.add(extension_request)
        await db.commit()
        await db.refresh(extension_request)

        # Load relationships
        await db.refresh(extension_request, ["requested_by", "creator", "todo"])

        return extension_request

    async def respond_to_request(
        self,
        db: AsyncSession,
        *,
        request_obj: TodoExtensionRequest,
        response_data: TodoExtensionRequestResponse,
        responded_by_id: int,
    ) -> TodoExtensionRequest:
        """Respond to an extension request."""
        request_obj.status = response_data.status.value
        request_obj.response_reason = response_data.response_reason
        request_obj.responded_at = get_utc_now()
        request_obj.responded_by_id = responded_by_id

        # If approved, update the todo's due datetime
        if response_data.status == ExtensionRequestStatus.APPROVED:
            todo = await db.get(Todo, request_obj.todo_id)
            if todo:
                # Use new_due_date if provided (for date change approval), otherwise use requested_due_date
                requested_datetime = response_data.new_due_date if response_data.new_due_date else request_obj.requested_due_date

                # Ensure timezone-aware (should already be UTC)
                if requested_datetime.tzinfo is None:
                    from datetime import UTC
                    requested_datetime = requested_datetime.replace(tzinfo=UTC)

                todo.due_datetime = requested_datetime
                todo.updated_at = get_utc_now()

        await db.commit()
        await db.refresh(request_obj)

        # Load relationships
        await db.refresh(
            request_obj, ["requested_by", "creator", "responded_by", "todo"]
        )

        return request_obj

    async def get_by_id_with_relationships(
        self, db: AsyncSession, *, request_id: int
    ) -> TodoExtensionRequest | None:
        """Get extension request by ID with all relationships loaded."""
        query = (
            select(TodoExtensionRequest)
            .options(
                selectinload(TodoExtensionRequest.requested_by),
                selectinload(TodoExtensionRequest.creator),
                selectinload(TodoExtensionRequest.responded_by),
                selectinload(TodoExtensionRequest.todo),
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
        status_filter: ExtensionRequestStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[TodoExtensionRequest], int]:
        """List extension requests for a creator to review."""
        base_query = (
            select(TodoExtensionRequest)
            .options(
                selectinload(TodoExtensionRequest.requested_by),
                selectinload(TodoExtensionRequest.creator),
                selectinload(TodoExtensionRequest.responded_by),
                selectinload(TodoExtensionRequest.todo),
            )
            .where(TodoExtensionRequest.creator_id == creator_id)
        )

        if status_filter:
            base_query = base_query.where(
                TodoExtensionRequest.status == status_filter.value
            )

        # Get total count
        count_query = select(func.count(TodoExtensionRequest.id)).where(
            TodoExtensionRequest.creator_id == creator_id
        )
        if status_filter:
            count_query = count_query.where(
                TodoExtensionRequest.status == status_filter.value
            )

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = (
            base_query.order_by(TodoExtensionRequest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(query)
        requests = result.scalars().all()

        return list(requests), total

    async def list_for_requester(
        self,
        db: AsyncSession,
        *,
        requester_id: int,
        status_filter: ExtensionRequestStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[TodoExtensionRequest], int]:
        """List extension requests made by a user."""
        base_query = (
            select(TodoExtensionRequest)
            .options(
                selectinload(TodoExtensionRequest.requested_by),
                selectinload(TodoExtensionRequest.creator),
                selectinload(TodoExtensionRequest.responded_by),
                selectinload(TodoExtensionRequest.todo),
            )
            .where(TodoExtensionRequest.requested_by_id == requester_id)
        )

        if status_filter:
            base_query = base_query.where(
                TodoExtensionRequest.status == status_filter.value
            )

        # Get total count
        count_query = select(func.count(TodoExtensionRequest.id)).where(
            TodoExtensionRequest.requested_by_id == requester_id
        )
        if status_filter:
            count_query = count_query.where(
                TodoExtensionRequest.status == status_filter.value
            )

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = (
            base_query.order_by(TodoExtensionRequest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(query)
        requests = result.scalars().all()

        return list(requests), total

    async def get_pending_request_for_todo(
        self, db: AsyncSession, *, todo_id: int, requested_by_id: int
    ) -> TodoExtensionRequest | None:
        """Check if there's already a pending extension request for this todo by this user."""
        query = select(TodoExtensionRequest).where(
            and_(
                TodoExtensionRequest.todo_id == todo_id,
                TodoExtensionRequest.requested_by_id == requested_by_id,
                TodoExtensionRequest.status == ExtensionRequestStatus.PENDING.value,
            )
        )

        result = await db.execute(query)
        return result.scalars().first()

    async def get_any_request_for_todo(
        self, db: AsyncSession, *, todo_id: int, requested_by_id: int
    ) -> TodoExtensionRequest | None:
        """Check if there's any extension request (any status) for this todo by this user."""
        query = select(TodoExtensionRequest).where(
            and_(
                TodoExtensionRequest.todo_id == todo_id,
                TodoExtensionRequest.requested_by_id == requested_by_id,
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
        requested_due_date: datetime,
    ) -> TodoExtensionValidation:
        """Validate if an extension request can be made."""

        # Check if todo has a due datetime
        if not todo.due_datetime:
            return TodoExtensionValidation(
                can_request_extension=False, reason="Todo has no due date set"
            )

        # Check if todo is completed
        if todo.status == TodoStatus.COMPLETED.value:
            return TodoExtensionValidation(
                can_request_extension=False, reason="Cannot extend completed todo"
            )

        # Check if todo is deleted
        if todo.is_deleted:
            return TodoExtensionValidation(
                can_request_extension=False, reason="Cannot extend deleted todo"
            )

        # Check if user is the assigned user
        if todo.assignee_id != requested_by_id:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Only assigned user can request extension",
            )

        # Check if there's already any extension request (pending, approved, or rejected)
        # Only allow 1 extension request per todo per user, ever
        existing_request = await self.get_any_request_for_todo(
            db, todo_id=todo.id, requested_by_id=requested_by_id
        )
        if existing_request:
            if existing_request.status == ExtensionRequestStatus.PENDING.value:
                return TodoExtensionValidation(
                    can_request_extension=False,
                    reason="You already have a pending extension request for this todo",
                )
            elif existing_request.status == ExtensionRequestStatus.APPROVED.value:
                return TodoExtensionValidation(
                    can_request_extension=False,
                    reason="Extension request was already approved for this todo",
                )
            else:  # REJECTED
                return TodoExtensionValidation(
                    can_request_extension=False,
                    reason="You have already used your extension request for this todo",
                )

        # Ensure both datetimes are timezone-aware for comparison
        from datetime import UTC

        current_due_datetime = todo.due_datetime
        if current_due_datetime.tzinfo is None:
            current_due_datetime = current_due_datetime.replace(tzinfo=UTC)

        if requested_due_date.tzinfo is None:
            requested_due_date = requested_due_date.replace(tzinfo=UTC)

        # Check if requested datetime is after current due datetime
        if requested_due_date <= current_due_datetime:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Extension date must be after current due date and time",
            )

        # Check if requested date is within allowed range (3 days max)
        max_allowed_datetime = current_due_datetime + timedelta(days=3)
        if requested_due_date > max_allowed_datetime:
            return TodoExtensionValidation(
                can_request_extension=False,
                max_allowed_due_date=max_allowed_datetime,
                reason="Extension cannot exceed 3 days from current due date",
            )

        # Check if requested date is not in the past
        now = get_utc_now()
        if requested_due_date < now:
            return TodoExtensionValidation(
                can_request_extension=False,
                reason="Extension date cannot be in the past",
            )

        return TodoExtensionValidation(
            can_request_extension=True, max_allowed_due_date=max_allowed_datetime
        )

    async def get_statistics_for_creator(
        self, db: AsyncSession, *, creator_id: int
    ) -> dict:
        """Get extension request statistics for a creator."""
        query = (
            select(
                TodoExtensionRequest.status,
                func.count(TodoExtensionRequest.id).label("count"),
            )
            .where(TodoExtensionRequest.creator_id == creator_id)
            .group_by(TodoExtensionRequest.status)
        )

        result = await db.execute(query)
        stats = {row.status: row.count for row in result}

        return {
            "total": sum(stats.values()),
            "pending": stats.get(ExtensionRequestStatus.PENDING.value, 0),
            "approved": stats.get(ExtensionRequestStatus.APPROVED.value, 0),
            "rejected": stats.get(ExtensionRequestStatus.REJECTED.value, 0),
        }


# Create instance
todo_extension_request = CRUDTodoExtensionRequest(TodoExtensionRequest)
