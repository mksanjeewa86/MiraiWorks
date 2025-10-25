"""
Subscription Email Service
Handles email notifications for subscription-related events
"""
import logging

from app.config import settings
from app.models.plan_change_request import PlanChangeRequest
from app.services.email_service import EmailService
from app.services.email_template_service import EmailTemplateService

logger = logging.getLogger(__name__)


class SubscriptionEmailService:
    def __init__(self):
        self.email_service = EmailService()
        self.template_service = EmailTemplateService()

    async def send_plan_change_request_notification(
        self,
        request: PlanChangeRequest,
        admin_emails: list[str],
    ) -> bool:
        """
        Send notification to admins when a plan change request is submitted.

        Args:
            request: The plan change request
            admin_emails: List of system admin email addresses
        """
        try:
            # Determine request type color
            is_upgrade = float(request.requested_plan.price_monthly) > float(
                request.current_plan.price_monthly
            )
            request_type_color = "#28a745" if is_upgrade else "#007bff"
            request_type = "Upgrade" if is_upgrade else "Downgrade"

            # Prepare context
            context = {
                "company_name": request.company.name if request.company else "Unknown",
                "requester_name": (
                    request.requester.full_name if request.requester else "Unknown"
                ),
                "current_plan_name": request.current_plan.display_name,
                "requested_plan_name": request.requested_plan.display_name,
                "request_type": request_type,
                "request_type_color": request_type_color,
                "request_message": request.request_message or "",
                "review_url": f"{settings.app_base_url}/admin/plan-requests",
            }

            # Render template
            html_content, text_content = self.template_service.render_email_template(
                template_path="subscription/plan_change_request",
                context=context,
                subject="New Plan Change Request",
                header_title="Plan Change Request",
            )

            # Send email
            success = await self.email_service.send_email(
                to_emails=admin_emails,
                subject="New Plan Change Request - Action Required",
                html_body=html_content,
                text_body=text_content,
            )

            if success:
                logger.info(
                    f"Plan change request notification sent to {len(admin_emails)} admins"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to send plan change request notification: {e}")
            return False

    async def send_plan_change_approved_notification(
        self,
        request: PlanChangeRequest,
        requester_email: str,
    ) -> bool:
        """
        Send notification to requester when plan change is approved.

        Args:
            request: The approved plan change request
            requester_email: Email address of the requester
        """
        try:
            # Format price
            new_price = f"¥{float(request.requested_plan.price_monthly):,.0f}"

            # Prepare context
            context = {
                "requester_name": (
                    request.requester.full_name if request.requester else "User"
                ),
                "current_plan_name": request.current_plan.display_name,
                "requested_plan_name": request.requested_plan.display_name,
                "new_price": new_price,
                "review_message": request.review_message or "",
                "subscription_url": f"{settings.app_base_url}/subscription",
            }

            # Render template
            html_content, text_content = self.template_service.render_email_template(
                template_path="subscription/plan_change_approved",
                context=context,
                subject="Plan Change Approved",
                header_title="Plan Change Approved",
            )

            # Send email
            success = await self.email_service.send_email(
                to_emails=[requester_email],
                subject="Your Plan Change Request Has Been Approved! 🎉",
                html_body=html_content,
                text_body=text_content,
            )

            if success:
                logger.info(
                    f"Plan change approved notification sent to {requester_email}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to send plan change approved notification: {e}")
            return False

    async def send_plan_change_rejected_notification(
        self,
        request: PlanChangeRequest,
        requester_email: str,
    ) -> bool:
        """
        Send notification to requester when plan change is rejected.

        Args:
            request: The rejected plan change request
            requester_email: Email address of the requester
        """
        try:
            # Prepare context
            context = {
                "requester_name": (
                    request.requester.full_name if request.requester else "User"
                ),
                "current_plan_name": request.current_plan.display_name,
                "requested_plan_name": request.requested_plan.display_name,
                "review_message": request.review_message or "",
                "subscription_url": f"{settings.app_base_url}/subscription",
            }

            # Render template
            html_content, text_content = self.template_service.render_email_template(
                template_path="subscription/plan_change_rejected",
                context=context,
                subject="Plan Change Request Update",
                header_title="Plan Change Request Update",
            )

            # Send email
            success = await self.email_service.send_email(
                to_emails=[requester_email],
                subject="Plan Change Request Update",
                html_body=html_content,
                text_body=text_content,
            )

            if success:
                logger.info(
                    f"Plan change rejected notification sent to {requester_email}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to send plan change rejected notification: {e}")
            return False


# Singleton instance
subscription_email_service = SubscriptionEmailService()
