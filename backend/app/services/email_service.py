import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        to_emails: list[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.from_name} <{settings.from_email}>"
            msg['To'] = ', '.join(to_emails)

            # Add text part
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                elif settings.smtp_use_ssl:
                    server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)
                
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_emails} with subject: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {str(e)}")
            return False

    async def send_2fa_code(self, email: str, code: str, user_name: str) -> bool:
        """Send 2FA verification code via email."""
        subject = "Your MiraiWorks Verification Code"
        
        html_body = f"""
        <html>
        <head></head>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Your Verification Code</h2>
                <p>Hi {user_name},</p>
                <p>Your two-factor authentication verification code is:</p>
                <div style="background: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                    <h1 style="color: #007bff; letter-spacing: 5px; margin: 0;">{code}</h1>
                </div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated message from MiraiWorks. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Your MiraiWorks Verification Code
        
        Hi {user_name},
        
        Your two-factor authentication verification code is: {code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        
        This is an automated message from MiraiWorks.
        """
        
        return await self.send_email([email], subject, html_body, text_body)

    async def send_password_reset(
        self, email: str, reset_token: str, user_name: str
    ) -> bool:
        """Send password reset link via email."""
        logger.info(f"[STUB] Would send password reset token {reset_token} to {email}")
        return True

    async def send_interview_notification(
        self, email: str, interview_data: dict
    ) -> bool:
        """Send interview notification email."""
        logger.info(f"[STUB] Would send interview notification to {email}")
        return True

    async def send_welcome_email(self, email: str, user_name: str, role: str) -> bool:
        """Send welcome email to new user."""
        logger.info(f"[STUB] Would send welcome email to {email} for role {role}")
        return True

    async def send_password_reset_notification(
        self, email: str, user_name: str, admin_name: str
    ) -> bool:
        """Send password reset request notification to admin."""
        logger.info(
            f"[STUB] Would send password reset notification for {user_name} to admin {admin_name}"
        )
        return True

    async def send_user_activation(
        self, email: str, user_name: str, temporary_password: str
    ) -> bool:
        """Send user activation email with temporary password."""
        logger.info(f"[STUB] Would send activation email to {email} with temp password")
        return True


# Global instance
email_service = EmailService()
