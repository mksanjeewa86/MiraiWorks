from typing import Any

from app.services.email_template_service import email_template_service

# Force reload after email_template_service fixes


class EmailPreviewService:
    def __init__(self):
        self.sample_data = self._get_sample_data()

    def _get_sample_data(self) -> dict[str, dict[str, Any]]:
        """Get sample data for different email types."""
        return {
            "auth/activation": {
                "context": {
                    "first_name": "John",
                    "email": "john.doe@example.com",
                    "temporary_password": "TempPass123!",
                    "activation_url": "http://localhost:3001/activate/42",
                },
                "subject": "Activate your MiraiWorks Account",
                "header_title": "Welcome to MiraiWorks",
            },
            "auth/2fa_code": {
                "context": {
                    "user_name": "John Doe",
                    "code": "123456",
                },
                "subject": "Your MiraiWorks Verification Code",
                "header_title": "Your Verification Code",
            },
            "admin/company_activation": {
                "context": {
                    "company_name": "Tech Solutions Inc",
                    "email": "admin@techsolutions.com",
                    "temporary_password": "AdminPass456!",
                    "activation_url": "http://localhost:3001/activate/99",
                },
                "subject": "Welcome to MiraiWorks - Activate your Tech Solutions Inc admin account",
                "header_title": "Welcome to MiraiWorks",
            },
            "notifications/message_notification": {
                "context": {
                    "recipient_name": "Jane Smith",
                    "sender_name": "Alex Johnson",
                    "message_content": "Hi Jane, I wanted to follow up on our conversation about the job opportunity. Are you available for a call this week?",
                    "conversation_url": "http://localhost:3001/messages?user=123",
                },
                "subject": "New message from Alex Johnson - MiraiWorks",
                "header_title": "New Message",
            },
        }

    def get_available_templates(self) -> list[str]:
        """Get list of available email templates."""
        return list(self.sample_data.keys())

    def preview_email(self, template_path: str) -> dict[str, str]:
        """Generate preview for a specific email template."""
        if template_path not in self.sample_data:
            raise ValueError(f"Template '{template_path}' not found")

        template_config = self.sample_data[template_path]

        try:
            html_body, text_body = email_template_service.render_email_template(
                template_path,
                template_config["context"],
                template_config["subject"],
                template_config["header_title"],
            )

            return {
                "template_path": template_path,
                "subject": template_config["subject"],
                "html_body": html_body,
                "text_body": text_body,
            }
        except Exception as e:
            raise ValueError(
                f"Failed to render template '{template_path}': {str(e)}"
            ) from e

    def preview_all_emails(self) -> dict[str, dict[str, str]]:
        """Generate previews for all available email templates."""
        previews = {}
        for template_path in self.get_available_templates():
            try:
                previews[template_path] = self.preview_email(template_path)
            except Exception as e:
                previews[template_path] = {
                    "error": str(e),
                    "template_path": template_path,
                }
        return previews


# Global instance
email_preview_service = EmailPreviewService()
