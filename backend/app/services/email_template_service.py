import os
from pathlib import Path
from typing import Dict, Any, Tuple
from string import Template


class EmailTemplateService:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.base_template_path = self.template_dir / "base.html"

    def _load_template(self, template_path: str, format_type: str = "html") -> str:
        """Load a template file from the templates directory.

        Args:
            template_path: Path to template like 'auth/activation' or 'notifications/message_notification'
            format_type: File extension ('html' or 'txt')
        """
        full_template_path = self.template_dir / f"{template_path}.{format_type}"

        if not full_template_path.exists():
            raise FileNotFoundError(f"Template not found: {full_template_path}")

        with open(full_template_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _load_base_template(self) -> str:
        """Load the base HTML template."""
        if not self.base_template_path.exists():
            raise FileNotFoundError(f"Base template not found: {self.base_template_path}")

        with open(self.base_template_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context using string templating."""
        template = Template(template_content)
        try:
            return template.substitute(context)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def render_email_template(
        self,
        template_path: str,
        context: Dict[str, Any],
        subject: str,
        header_title: str = "MiraiWorks"
    ) -> Tuple[str, str]:
        """
        Render both HTML and text versions of an email template.

        Args:
            template_path: Path to template like 'auth/activation' or 'notifications/message_notification'
            context: Variables to substitute in the template
            subject: Email subject line
            header_title: Title to show in the email header

        Returns:
            Tuple of (html_content, text_content)
        """
        try:
            # Load and render the content template (HTML)
            html_content_template = self._load_template(template_path, "html")
            rendered_content = self._render_template(html_content_template, context)

            # Load base template and wrap the content
            base_template = self._load_base_template()
            base_context = {
                "subject": subject,
                "header_title": header_title,
                "content": rendered_content
            }
            html_body = self._render_template(base_template, base_context)

            # Load and render the text template
            text_template = self._load_template(template_path, "txt")
            text_body = self._render_template(text_template, context)

            return html_body, text_body

        except FileNotFoundError as e:
            raise ValueError(f"Email template error: {e}")
        except Exception as e:
            raise ValueError(f"Error rendering email template: {e}")


# Global instance
email_template_service = EmailTemplateService()