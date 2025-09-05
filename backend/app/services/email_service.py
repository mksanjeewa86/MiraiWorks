import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Optional
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
        """Send an email via SMTP."""
        try:
            msg = MimeMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from
            msg["To"] = ", ".join(to_emails)

            # Add text part if provided
            if text_body:
                text_part = MimeText(text_body, "plain")
                msg.attach(text_part)

            # Add HTML part
            html_part = MimeText(html_body, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {str(e)}")
            return False

    async def send_2fa_code(self, email: str, code: str, user_name: str) -> bool:
        """Send 2FA verification code via email."""
        subject = "Your MiraiWorks Verification Code"
        
        html_body = f"""
        <html>
            <body>
                <h2>MiraiWorks - Verification Code</h2>
                <p>Hello {user_name},</p>
                <p>Your verification code is:</p>
                <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{code}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please contact your administrator.</p>
                <br>
                <p>Best regards,<br>MiraiWorks Team</p>
            </body>
        </html>
        """
        
        text_body = f"""
        MiraiWorks - Verification Code
        
        Hello {user_name},
        
        Your verification code is: {code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please contact your administrator.
        
        Best regards,
        MiraiWorks Team
        """

        return await self.send_email([email], subject, html_body, text_body)

    async def send_password_reset_notification(
        self, 
        email: str, 
        user_name: str, 
        admin_name: str
    ) -> bool:
        """Send password reset request notification to admin."""
        subject = "Password Reset Request - MiraiWorks"
        
        html_body = f"""
        <html>
            <body>
                <h2>MiraiWorks - Password Reset Request</h2>
                <p>Hello {admin_name},</p>
                <p>A password reset has been requested for:</p>
                <ul>
                    <li><strong>User:</strong> {user_name}</li>
                    <li><strong>Email:</strong> {email}</li>
                </ul>
                <p>Please log into the admin panel to approve or deny this request.</p>
                <p><a href="{self.app_base_url}/admin/password-requests">View Password Requests</a></p>
                <br>
                <p>Best regards,<br>MiraiWorks System</p>
            </body>
        </html>
        """
        
        text_body = f"""
        MiraiWorks - Password Reset Request
        
        Hello {admin_name},
        
        A password reset has been requested for:
        - User: {user_name}
        - Email: {email}
        
        Please log into the admin panel to approve or deny this request.
        
        View Password Requests: {self.app_base_url}/admin/password-requests
        
        Best regards,
        MiraiWorks System
        """

        return await self.send_email([email], subject, html_body, text_body)

    async def send_user_activation(
        self, 
        email: str, 
        user_name: str, 
        temporary_password: str
    ) -> bool:
        """Send user activation email with temporary password."""
        subject = "Welcome to MiraiWorks - Account Created"
        
        html_body = f"""
        <html>
            <body>
                <h2>Welcome to MiraiWorks!</h2>
                <p>Hello {user_name},</p>
                <p>Your account has been created successfully. Here are your login details:</p>
                <ul>
                    <li><strong>Email:</strong> {email}</li>
                    <li><strong>Temporary Password:</strong> {temporary_password}</li>
                </ul>
                <p>Please log in and change your password immediately.</p>
                <p><a href="{self.app_base_url}/login">Login to MiraiWorks</a></p>
                <br>
                <p>Best regards,<br>MiraiWorks Team</p>
            </body>
        </html>
        """
        
        text_body = f"""
        Welcome to MiraiWorks!
        
        Hello {user_name},
        
        Your account has been created successfully. Here are your login details:
        - Email: {email}
        - Temporary Password: {temporary_password}
        
        Please log in and change your password immediately.
        
        Login: {self.app_base_url}/login
        
        Best regards,
        MiraiWorks Team
        """

        return await self.send_email([email], subject, html_body, text_body)


# Global instance
email_service = EmailService()