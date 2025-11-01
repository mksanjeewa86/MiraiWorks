
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.plan_change_request import PlanChangeRequest
from app.utils.constants import PlanChangeRequestStatus


class CRUDPlanChangeRequest(CRUDBase[PlanChangeRequest, Any, Any]):
    """CRUD operations for plan change requests."""

    async def get_by_company_id(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> list[PlanChangeRequest]:
        """Get all plan change requests for a company."""
        result = await db.execute(
            select(PlanChangeRequest)
            .where(PlanChangeRequest.company_id == company_id)
            .options(
                selectinload(PlanChangeRequest.current_plan),
                selectinload(PlanChangeRequest.requested_plan),
                selectinload(PlanChangeRequest.requester),
                selectinload(PlanChangeRequest.reviewer),
            )
            .order_by(PlanChangeRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        db: AsyncSession,
        *,
        status: PlanChangeRequestStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PlanChangeRequest]:
        """Get all plan change requests by status."""
        result = await db.execute(
            select(PlanChangeRequest)
            .where(PlanChangeRequest.status == status)
            .options(
                selectinload(PlanChangeRequest.company),
                selectinload(PlanChangeRequest.current_plan),
                selectinload(PlanChangeRequest.requested_plan),
                selectinload(PlanChangeRequest.requester),
                selectinload(PlanChangeRequest.reviewer),
            )
            .order_by(PlanChangeRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_requests(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[PlanChangeRequest]:
        """Get all pending plan change requests."""
        return await self.get_by_status(
            db, status=PlanChangeRequestStatus.PENDING, skip=skip, limit=limit
        )

    async def get_with_details(
        self, db: AsyncSession, *, request_id: int
    ) -> PlanChangeRequest | None:
        """Get plan change request with all details."""
        result = await db.execute(
            select(PlanChangeRequest)
            .where(PlanChangeRequest.id == request_id)
            .options(
                selectinload(PlanChangeRequest.company),
                selectinload(PlanChangeRequest.subscription),
                selectinload(PlanChangeRequest.current_plan),
                selectinload(PlanChangeRequest.requested_plan),
                selectinload(PlanChangeRequest.requester),
                selectinload(PlanChangeRequest.reviewer),
            )
        )
        return result.scalar_one_or_none()

    async def approve_request(
        self,
        db: AsyncSession,
        *,
        request_id: int,
        reviewed_by: int,
        review_message: str | None = None,
    ) -> PlanChangeRequest | None:
        """Approve a plan change request."""
        from app.utils.datetime_utils import get_utc_now

        request = await self.get(db, id=request_id)
        if not request or request.status != PlanChangeRequestStatus.PENDING:
            return None

        request.status = PlanChangeRequestStatus.APPROVED
        request.reviewed_by = reviewed_by
        request.review_message = review_message
        request.reviewed_at = get_utc_now()

        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    async def reject_request(
        self,
        db: AsyncSession,
        *,
        request_id: int,
        reviewed_by: int,
        review_message: str | None = None,
    ) -> PlanChangeRequest | None:
        """Reject a plan change request."""
        from app.utils.datetime_utils import get_utc_now

        request = await self.get(db, id=request_id)
        if not request or request.status != PlanChangeRequestStatus.PENDING:
            return None

        request.status = PlanChangeRequestStatus.REJECTED
        request.reviewed_by = reviewed_by
        request.review_message = review_message
        request.reviewed_at = get_utc_now()

        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    async def cancel_request(
        self, db: AsyncSession, *, request_id: int
    ) -> PlanChangeRequest | None:
        """Cancel a plan change request (user cancels their own request)."""
        from app.utils.datetime_utils import get_utc_now

        request = await self.get(db, id=request_id)
        if not request or request.status != PlanChangeRequestStatus.PENDING:
            return None

        request.status = PlanChangeRequestStatus.CANCELLED
        request.reviewed_at = get_utc_now()

        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    async def create_request(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        subscription_id: int,
        current_plan_id: int,
        requested_plan_id: int,
        request_type: str,
        requested_by: int,
        request_message: str | None = None,
    ) -> PlanChangeRequest:
        """Create a new plan change request."""
        from app.utils.constants import PlanChangeRequestType

        request = PlanChangeRequest(
            company_id=company_id,
            subscription_id=subscription_id,
            current_plan_id=current_plan_id,
            requested_plan_id=requested_plan_id,
            request_type=PlanChangeRequestType(request_type),
            requested_by=requested_by,
            request_message=request_message,
            status=PlanChangeRequestStatus.PENDING,
        )
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request


plan_change_request = CRUDPlanChangeRequest(PlanChangeRequest)
