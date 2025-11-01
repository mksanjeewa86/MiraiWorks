from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.company_subscription import company_subscription as subscription_crud
from app.crud.plan_change_request import (
    plan_change_request as plan_change_request_crud,
)
from app.crud.plan_feature import plan_feature as plan_feature_crud
from app.crud.subscription_plan import subscription_plan as plan_crud
from app.models.user import User
from app.services.subscription_email_service import subscription_email_service
from app.utils.constants import PlanChangeRequestStatus, PlanChangeRequestType, UserRole


class SubscriptionService:
    """Business logic for subscription management."""

    async def check_feature_access(
        self, db: AsyncSession, *, company_id: int, feature_name: str
    ) -> tuple[bool, str | None]:
        """
        Check if a company has access to a specific feature.

        Returns:
            (has_access, error_message)
        """
        # Get company subscription
        subscription = await subscription_crud.get_active_by_company_id(
            db, company_id=company_id
        )

        if not subscription:
            return False, "No active subscription found"

        # Check if plan has this feature
        has_feature = await plan_feature_crud.plan_has_feature_by_name(
            db, plan_id=subscription.plan_id, feature_name=feature_name
        )

        if not has_feature:
            return False, f"Feature '{feature_name}' not available in your plan"

        return True, None

    async def check_permission(
        self, db: AsyncSession, *, company_id: int, permission_key: str
    ) -> tuple[bool, str | None]:
        """
        Check if a company has a specific permission (hierarchical).

        Examples:
            - permission_key = 'user_management.deactivate'
            - permission_key = 'exam_management.create'

        Returns:
            (has_permission, error_message)
        """
        # Get company subscription
        subscription = await subscription_crud.get_active_by_company_id(
            db, company_id=company_id
        )

        if not subscription:
            return False, "No active subscription found"

        # Check if plan has feature with this permission key
        has_permission = await plan_feature_crud.plan_has_feature_by_permission_key(
            db, plan_id=subscription.plan_id, permission_key=permission_key
        )

        if not has_permission:
            return (
                False,
                f"Permission '{permission_key}' not available in your plan",
            )

        return True, None

    async def request_plan_change(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        requested_plan_id: int,
        requested_by: int,
        request_message: str | None = None,
    ):
        """
        Create a plan change request (upgrade or downgrade).
        Requires system admin approval.
        """
        # Get current subscription
        subscription = await subscription_crud.get_by_company_id(
            db, company_id=company_id
        )

        if not subscription:
            raise HTTPException(
                status_code=404, detail="No subscription found for this company"
            )

        current_plan_id = subscription.plan_id

        if current_plan_id == requested_plan_id:
            raise HTTPException(
                status_code=400, detail="Already subscribed to this plan"
            )

        # Get plans to determine if upgrade or downgrade
        current_plan = await plan_crud.get(db, id=current_plan_id)
        requested_plan = await plan_crud.get(db, id=requested_plan_id)

        if not current_plan or not requested_plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Determine request type based on price (simple logic)
        request_type = (
            PlanChangeRequestType.UPGRADE
            if requested_plan.price_monthly > current_plan.price_monthly
            else PlanChangeRequestType.DOWNGRADE
        )

        # Create the request
        change_request = await plan_change_request_crud.create_request(
            db,
            company_id=company_id,
            subscription_id=subscription.id,
            current_plan_id=current_plan_id,
            requested_plan_id=requested_plan_id,
            request_type=request_type.value,
            requested_by=requested_by,
            request_message=request_message,
        )

        # Get request with full details for email
        full_request = await plan_change_request_crud.get_with_details(
            db, request_id=change_request.id
        )

        # Send email notification to system admins
        try:
            # Get all system admin emails
            result = await db.execute(
                select(User).where(
                    User.role == UserRole.SYSTEM_ADMIN, User.is_active  # type: ignore
                )
            )
            system_admins = result.scalars().all()
            admin_emails = [admin.email for admin in system_admins if admin.email]

            if admin_emails:
                await subscription_email_service.send_plan_change_request_notification(
                    request=full_request,  # type: ignore
                    admin_emails=admin_emails,
                )
        except Exception as e:
            # Log but don't fail the request if email fails
            print(f"Failed to send email notification: {e}")

        return change_request

    async def review_plan_change_request(
        self,
        db: AsyncSession,
        *,
        request_id: int,
        reviewer: User,
        status: PlanChangeRequestStatus,
        review_message: str | None = None,
    ):
        """
        Review a plan change request (approve or reject).
        If approved, immediately change the plan.
        """
        # Get the request
        request = await plan_change_request_crud.get_with_details(
            db, request_id=request_id
        )

        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.status != PlanChangeRequestStatus.PENDING:
            raise HTTPException(
                status_code=400, detail="Request has already been reviewed"
            )

        # Update request status
        if status == PlanChangeRequestStatus.APPROVED:
            await plan_change_request_crud.approve_request(
                db,
                request_id=request_id,
                reviewed_by=reviewer.id,
                review_message=review_message,
            )

            # Change the subscription plan
            subscription = await subscription_crud.get_by_company_id(
                db, company_id=request.company_id
            )
            if subscription:
                await subscription_crud.update(
                    db,
                    db_obj=subscription,
                    obj_in={"plan_id": request.requested_plan_id},
                )

            # Send approval email to requester
            try:
                updated_request = await plan_change_request_crud.get_with_details(
                    db, request_id=request_id
                )
                if updated_request.requester and updated_request.requester.email:  # type: ignore
                    await subscription_email_service.send_plan_change_approved_notification(
                        request=updated_request,  # type: ignore
                        requester_email=updated_request.requester.email,  # type: ignore
                    )
            except Exception as e:
                print(f"Failed to send approval email: {e}")

        elif status == PlanChangeRequestStatus.REJECTED:
            await plan_change_request_crud.reject_request(
                db,
                request_id=request_id,
                reviewed_by=reviewer.id,
                review_message=review_message,
            )

            # Send rejection email to requester
            try:
                updated_request = await plan_change_request_crud.get_with_details(
                    db, request_id=request_id
                )
                if updated_request.requester and updated_request.requester.email:  # type: ignore
                    await subscription_email_service.send_plan_change_rejected_notification(
                        request=updated_request,  # type: ignore
                        requester_email=updated_request.requester.email,  # type: ignore
                    )
            except Exception as e:
                print(f"Failed to send rejection email: {e}")

        else:
            raise HTTPException(status_code=400, detail="Invalid status")

        return await plan_change_request_crud.get_with_details(
            db, request_id=request_id
        )

    async def cancel_plan_change_request(
        self, db: AsyncSession, *, request_id: int, user_id: int
    ):
        """
        Cancel a pending plan change request.
        Only the requester can cancel their own request, and only if it's pending.
        """
        # Get the request
        request = await plan_change_request_crud.get_with_details(
            db, request_id=request_id
        )

        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Only pending requests can be cancelled
        if request.status != PlanChangeRequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel request with status: {request.status}",
            )

        # Only the requester can cancel their own request
        if request.requested_by != user_id:
            raise HTTPException(
                status_code=403, detail="You can only cancel your own requests"
            )

        # Update request status to cancelled
        await plan_change_request_crud.cancel_request(db, request_id=request_id)

        return await plan_change_request_crud.get_with_details(
            db, request_id=request_id
        )


subscription_service = SubscriptionService()
