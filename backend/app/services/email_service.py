import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.services.email_template_service import email_template_service

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
        text_body: str | None = None,
    ) -> bool:
        """Send an email via SMTP."""
        try:
            # Log what we're about to send for debugging
            logger.info(f"Sending email to {to_emails}")
            logger.info(f"Subject: {subject}")
            logger.info(f"HTML body length: {len(html_body)}")
            logger.info(f"Text body provided: {text_body is not None}")

            # Create message with proper structure
            if text_body:
                # Send multipart alternative (HTML + text)
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{settings.from_name} <{settings.from_email}>"
                msg["To"] = ", ".join(to_emails)

                # Set proper headers
                msg["MIME-Version"] = "1.0"
                msg["Content-Type"] = "multipart/alternative"

                # Add text part first (fallback)
                text_part = MIMEText(text_body, "plain", "utf-8")
                msg.attach(text_part)

                # Add HTML part second (preferred)
                html_part = MIMEText(html_body, "html", "utf-8")
                msg.attach(html_part)

                logger.info("Created multipart/alternative email")
            else:
                # Send HTML only
                msg = MIMEText(html_body, "html", "utf-8")
                msg["Subject"] = subject
                msg["From"] = f"{settings.from_name} <{settings.from_email}>"
                msg["To"] = ", ".join(to_emails)
                msg["MIME-Version"] = "1.0"

                logger.info("Created HTML-only email")

            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                elif settings.smtp_use_ssl:
                    server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)

                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)

                server.send_message(msg)

            logger.info(
                f"Email sent successfully to {to_emails} with subject: {subject}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {str(e)}")
            return False

    async def send_2fa_code(self, email: str, code: str, user_name: str) -> bool:
        """Send 2FA verification code via email."""
        subject = "Your MiraiWorks Verification Code"

        # Prepare template context
        context = {
            "user_name": user_name,
            "code": code,
        }

        try:
            html_body, text_body = email_template_service.render_email_template(
                "auth/2fa_code", context, subject, "Your Verification Code"
            )
            return await self.send_email([email], subject, html_body, text_body)
        except Exception as e:
            logger.error(f"Failed to render 2FA email template: {e}")
            # Fallback to a simple message if template fails
            return await self.send_email(
                [email],
                subject,
                f"<p>Hi {user_name}, your 2FA code is: <strong>{code}</strong></p>",
                f"Hi {user_name}, your 2FA code is: {code}",
            )

    async def send_password_reset(
        self, email: str, reset_token: str, user_name: str
    ) -> bool:
        """Send password reset link via email."""
        logger.info("[STUB] Password reset email triggered for %s", email)
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

    async def send_registration_completion_email(self, email: str, first_name: str) -> bool:
        """Send registration completion email with login button."""
        subject = "Welcome to MiraiWorks - Registration Complete!"

        login_url = f"{self.app_base_url}/auth/login"
        jobs_url = f"{self.app_base_url}/jobs"

        # Prepare template context
        context = {
            "first_name": first_name,
            "email": email,
            "login_url": login_url,
            "jobs_url": jobs_url,
        }

        try:
            html_body, text_body = email_template_service.render_email_template(
                "auth/registration_complete", context, subject, "Welcome to MiraiWorks"
            )
            return await self.send_email([email], subject, html_body, text_body)
        except Exception as e:
            logger.error(f"Failed to render registration completion email template: {e}")
            # Fallback to a simple HTML message if template fails
            html_fallback = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #6C63FF;">Welcome to MiraiWorks, {first_name}!</h2>

                <p>Congratulations! Your account has been successfully created.</p>

                <p>You can now:</p>
                <ul>
                    <li>Browse thousands of job opportunities</li>
                    <li>Apply to positions that interest you</li>
                    <li>Build your professional profile</li>
                    <li>Get matched with top employers in Japan</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="background-color: #6C63FF; color: white; padding: 12px 24px; text-decoration: none; border-radius: 24px; display: inline-block;">
                        Login to Your Account
                    </a>
                </div>

                <p>Or start browsing jobs immediately:</p>
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{jobs_url}" style="background-color: #22C55E; color: white; padding: 12px 24px; text-decoration: none; border-radius: 24px; display: inline-block;">
                        Browse Jobs
                    </a>
                </div>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 14px;">
                    Thank you for joining MiraiWorks - Your future starts here!<br>
                    <a href="{self.app_base_url}">Visit MiraiWorks</a>
                </p>
            </div>
            """

            text_fallback = f"""
Welcome to MiraiWorks, {first_name}!

Congratulations! Your account has been successfully created.

You can now:
- Browse thousands of job opportunities
- Apply to positions that interest you
- Build your professional profile
- Get matched with top employers in Japan

Login to your account: {login_url}
Or browse jobs: {jobs_url}

Thank you for joining MiraiWorks - Your future starts here!
Visit: {self.app_base_url}
            """

            return await self.send_email([email], subject, html_fallback, text_fallback)

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

    async def send_company_activation_email(
        self, email: str, company_name: str, temporary_password: str, user_id: int
    ) -> bool:
        """Send company admin activation email with login details."""
        subject = f"Welcome to MiraiWorks - Activate your {company_name} admin account"

        activation_url = f"{settings.app_base_url}/activate/{user_id}"

        # Prepare template context
        context = {
            "company_name": company_name,
            "email": email,
            "temporary_password": temporary_password,
            "activation_url": activation_url,
        }

        try:
            html_body, text_body = email_template_service.render_email_template(
                "admin/company_activation", context, subject, "Welcome to MiraiWorks"
            )
            return await self.send_email([email], subject, html_body, text_body)
        except Exception as e:
            logger.error(f"Failed to render company activation email template: {e}")
            # Fallback to a simple message if template fails
            return await self.send_email(
                [email],
                subject,
                f"<p>Hi, your {company_name} admin account is ready. Please activate at: {activation_url}</p>",
                f"Hi, your {company_name} admin account is ready. Please activate at: {activation_url}",
            )

    async def send_activation_email(
        self,
        email: str,
        first_name: str,
        activation_token: str,
        temporary_password: str | None = None,
        user_id: int | None = None,
    ) -> bool:
        """Send account activation email with activation link and optional temporary password."""
        subject = "Activate your MiraiWorks Account"

        # Use user_id if provided, otherwise fall back to token-based URL
        if user_id:
            activation_url = f"{self.app_base_url}/activate/{user_id}"
        else:
            activation_url = f"{self.app_base_url}/activate?token={activation_token}"

        # Prepare template context
        context = {
            "first_name": first_name,
            "email": email,
            "temporary_password": temporary_password or "Not provided",
            "activation_url": activation_url,
        }

        try:
            html_body, text_body = email_template_service.render_email_template(
                "auth/activation", context, subject, "Welcome to MiraiWorks"
            )
            return await self.send_email([email], subject, html_body, text_body)
        except Exception as e:
            logger.error(f"Failed to render activation email template: {e}")
            # Fallback to a simple message if template fails
            return await self.send_email(
                [email],
                subject,
                f"<p>Hi {first_name}, please activate your account at: {activation_url}</p>",
                f"Hi {first_name}, please activate your account at: {activation_url}",
            )

    async def send_template_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: dict,
    ) -> bool:
        """Send email using a template."""
        try:
            html_body, text_body = email_template_service.render_email_template(
                template_name, template_data, subject, "Email Notification"
            )
            return await self.send_email([to_email], subject, html_body, text_body)
        except Exception as e:
            logger.error(f"Failed to render email template '{template_name}': {e}")
            # Fallback to a simple message if template fails
            return await self.send_email(
                [to_email],
                subject,
                "<p>Email notification from MiraiWorks</p>",
                "Email notification from MiraiWorks",
            )

    async def send_message_notification(
        self,
        recipient_email: str,
        recipient_name: str,
        sender_name: str,
        message_content: str,
        conversation_url: str,
    ) -> bool:
        """Send email notification for new message."""
        subject = f"New message from {sender_name} - MiraiWorks"

        # Truncate message content if too long
        display_content = (
            message_content[:100] + "..."
            if len(message_content) > 100
            else message_content
        )

        # Prepare template context
        context = {
            "recipient_name": recipient_name,
            "sender_name": sender_name,
            "message_content": display_content,
            "conversation_url": conversation_url,
        }

        try:
            html_body, text_body = email_template_service.render_email_template(
                "notifications/message_notification", context, subject, "New Message"
            )
            return await self.send_email(
                [recipient_email], subject, html_body, text_body
            )
        except Exception as e:
            logger.error(f"Failed to render message notification email template: {e}")
            # Fallback to a simple message if template fails
            return await self.send_email(
                [recipient_email],
                subject,
                f"<p>Hi {recipient_name}, you have a new message from {sender_name}: {display_content}</p>",
                f"Hi {recipient_name}, you have a new message from {sender_name}: {display_content}",
            )


# Global instance
email_service = EmailService()
