"""Notification service for todo extension requests."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo_extension_request import TodoExtensionRequest
from app.services.email_service import email_service
from app.services.notification_service import NotificationService
from app.utils.constants import ExtensionRequestStatus, NotificationType

logger = logging.getLogger(__name__)


class TodoExtensionNotificationService:
    """Service for handling todo extension request notifications and emails."""

    def __init__(self):
        self.notification_service = NotificationService()

    async def notify_extension_request_created(
        self, db: AsyncSession, extension_request: TodoExtensionRequest
    ) -> None:
        """Send notifications when a new extension request is created."""
        try:
            # Notify the creator (todo owner) about the extension request
            await self._send_extension_request_notification(db, extension_request)

            # Send email to creator
            await self._send_extension_request_email(db, extension_request)

        except Exception as e:
            logger.error(f"Error sending extension request notifications: {e}")

    async def notify_extension_request_responded(
        self, db: AsyncSession, extension_request: TodoExtensionRequest
    ) -> None:
        """Send notifications when an extension request is responded to."""
        try:
            # Notify the requester about the response
            await self._send_extension_response_notification(db, extension_request)

            # Send email to requester
            await self._send_extension_response_email(db, extension_request)

        except Exception as e:
            logger.error(f"Error sending extension response notifications: {e}")

    async def _send_extension_request_notification(
        self, db: AsyncSession, extension_request: TodoExtensionRequest
    ) -> None:
        """Send in-app notification to creator about extension request."""
        requester_name = f"{extension_request.requested_by.first_name} {extension_request.requested_by.last_name}"

        # Get current due datetime from todo
        current_due_date_str = extension_request.todo.due_datetime.strftime('%Y-%m-%d') if extension_request.todo.due_datetime else "No due date"

        await self.notification_service.create_notification(
            db,
            user_id=extension_request.creator_id,
            notification_type=NotificationType.TODO_EXTENSION_REQUEST.value,
            title=f"Extension Request for Todo: {extension_request.todo.title}",
            message=f"{requester_name} has requested to extend the due date from "
            f"{current_due_date_str} to "
            f"{extension_request.requested_due_date.strftime('%Y-%m-%d')}",
            payload={
                "extension_request_id": extension_request.id,
                "todo_id": extension_request.todo_id,
                "requester_id": extension_request.requested_by_id,
                "requester_name": requester_name,
                "requested_due_date": extension_request.requested_due_date.isoformat(),
                "reason": extension_request.reason,
                "action_url": f"/todos/{extension_request.todo_id}/extensions/{extension_request.id}",
            },
        )

    async def _send_extension_response_notification(
        self, db: AsyncSession, extension_request: TodoExtensionRequest
    ) -> None:
        """Send in-app notification to requester about response."""
        status_text = (
            "approved"
            if extension_request.status == ExtensionRequestStatus.APPROVED.value
            else "rejected"
        )
        notification_type = (
            NotificationType.TODO_EXTENSION_APPROVED.value
            if extension_request.status == ExtensionRequestStatus.APPROVED.value
            else NotificationType.TODO_EXTENSION_REJECTED.value
        )

        title = (
            f"Extension Request {status_text.title()}: {extension_request.todo.title}"
        )

        message = f"Your extension request has been {status_text}"
        if extension_request.status == ExtensionRequestStatus.APPROVED.value:
            message += f". New due date: {extension_request.requested_due_date.strftime('%Y-%m-%d')}"

        if extension_request.response_reason:
            message += f". Reason: {extension_request.response_reason}"

        await self.notification_service.create_notification(
            db,
            user_id=extension_request.requested_by_id,
            notification_type=notification_type,
            title=title,
            message=message,
            payload={
                "extension_request_id": extension_request.id,
                "todo_id": extension_request.todo_id,
                "status": extension_request.status,
                "new_due_date": extension_request.requested_due_date.isoformat()
                if extension_request.status == ExtensionRequestStatus.APPROVED.value
                else None,
                "response_reason": extension_request.response_reason,
                "action_url": f"/todos/{extension_request.todo_id}",
            },
        )

    async def _send_extension_request_email(
        self, db: AsyncSession, extension_request: TodoExtensionRequest
    ) -> None:
        """Send email to creator about extension request."""
        try:
            requester_name = f"{extension_request.requested_by.first_name} {extension_request.requested_by.last_name}"

            subject = f"Todo Extension Request: {extension_request.todo.title}"

            # Get current due datetime from todo
            from datetime import datetime
            current_due_str = "No due date"
            if extension_request.todo.due_datetime:
                current_due_str = extension_request.todo.due_datetime.strftime('%B %d, %Y at %I:%M %p')

            # Create email content
            email_content = f"""
            <h2>Todo Extension Request</h2>

            <p><strong>{requester_name}</strong> has requested to extend the due date for the following todo:</p>

            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>{extension_request.todo.title}</h3>
                {f'<p><strong>Description:</strong> {extension_request.todo.description}</p>' if extension_request.todo.description else ''}

                <p><strong>Current Due Date:</strong> {current_due_str}</p>
                <p><strong>Requested Due Date:</strong> {extension_request.requested_due_date.strftime('%B %d, %Y at %I:%M %p')}</p>

                <h4>Reason for Extension:</h4>
                <p style="font-style: italic;">{extension_request.reason}</p>
            </div>

            <p>Please review and respond to this extension request at your earliest convenience.</p>

            <p>
                <a href="#" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Review Extension Request
                </a>
            </p>
            """

            await email_service.send_email(
                to_email=extension_request.creator.email,
                subject=subject,
                html_content=email_content,
            )

        except Exception as e:
            logger.error(f"Error sending extension request email: {e}")

    async def _send_extension_response_email(
        self, db: AsyncSession, extension_request: TodoExtensionRequest
    ) -> None:
        """Send email to requester about extension response."""
        try:
            status_text = (
                "Approved"
                if extension_request.status == ExtensionRequestStatus.APPROVED.value
                else "Rejected"
            )
            creator_name = f"{extension_request.creator.first_name} {extension_request.creator.last_name}"

            subject = (
                f"Todo Extension Request {status_text}: {extension_request.todo.title}"
            )

            # Get original due date from todo
            from datetime import datetime
            original_due_str = "No due date"
            if extension_request.todo.due_datetime:
                original_due_str = extension_request.todo.due_datetime.strftime('%B %d, %Y at %I:%M %p')

            # Create email content
            email_content = f"""
            <h2>Todo Extension Request {status_text}</h2>

            <p>Your extension request for the following todo has been <strong>{status_text.lower()}</strong> by {creator_name}:</p>

            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>{extension_request.todo.title}</h3>
                {f'<p><strong>Description:</strong> {extension_request.todo.description}</p>' if extension_request.todo.description else ''}

                <p><strong>Original Due Date:</strong> {original_due_str}</p>
                <p><strong>Requested Due Date:</strong> {extension_request.requested_due_date.strftime('%B %d, %Y at %I:%M %p')}</p>

                {f'<p><strong>New Due Date:</strong> {extension_request.requested_due_date.strftime("%B %d, %Y at %I:%M %p")}</p>' if extension_request.status == ExtensionRequestStatus.APPROVED.value else ''}

                {f'<h4>Response from {creator_name}:</h4><p style="font-style: italic;">{extension_request.response_reason}</p>' if extension_request.response_reason else ''}
            </div>

            <p>
                <a href="#" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Todo
                </a>
            </p>
            """

            await email_service.send_email(
                to_email=extension_request.requested_by.email,
                subject=subject,
                html_content=email_content,
            )

        except Exception as e:
            logger.error(f"Error sending extension response email: {e}")


# Create instance
todo_extension_notification_service = TodoExtensionNotificationService()
