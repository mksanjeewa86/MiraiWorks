import logging
from typing import List
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_from = settings.smtp_from
        self.app_base_url = settings.app_base_url

    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP (stub for demo)."""
        # Stub implementation for demo purposes
        logger.info(f"[STUB] Would send email to {to_emails} with subject: {subject}")
        return True

    async def send_2fa_code(self, email: str, code: str, user_name: str) -> bool:
        """Send 2FA verification code via email."""
        logger.info(f"[STUB] Would send 2FA code {code} to {email}")
        return True

    async def send_password_reset(self, email: str, reset_token: str, user_name: str) -> bool:
        """Send password reset link via email."""
        logger.info(f"[STUB] Would send password reset token {reset_token} to {email}")
        return True

    async def send_interview_notification(self, email: str, interview_data: dict) -> bool:
        """Send interview notification email."""
        logger.info(f"[STUB] Would send interview notification to {email}")
        return True

    async def send_welcome_email(self, email: str, user_name: str, role: str) -> bool:
        """Send welcome email to new user."""
        logger.info(f"[STUB] Would send welcome email to {email} for role {role}")
        return True

    async def send_password_reset_notification(self, email: str, user_name: str, admin_name: str) -> bool:
        """Send password reset request notification to admin."""
        logger.info(f"[STUB] Would send password reset notification for {user_name} to admin {admin_name}")
        return True

    async def send_user_activation(self, email: str, user_name: str, temporary_password: str) -> bool:
        """Send user activation email with temporary password."""
        logger.info(f"[STUB] Would send activation email to {email} with temp password")
        return True


# Global instance
email_service = EmailService()