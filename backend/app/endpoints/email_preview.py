from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Optional

from app.services.email_preview_service import email_preview_service

router = APIRouter(prefix="/api/dev/email-preview", tags=["Email Preview"])


@router.get("/", response_class=HTMLResponse)
async def email_preview_dashboard():
    """Email preview dashboard with links to all templates."""
    templates = email_preview_service.get_available_templates()

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MiraiWorks Email Preview</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: #007bff;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .template-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .template-card {{
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                background: #fafafa;
                transition: transform 0.2s ease;
            }}
            .template-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            .template-card h3 {{
                margin: 0 0 10px 0;
                color: #333;
            }}
            .template-card p {{
                color: #666;
                margin: 0 0 15px 0;
                font-size: 14px;
            }}
            .btn-group {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .btn {{
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .btn-primary {{
                background: #007bff;
                color: white;
            }}
            .btn-primary:hover {{
                background: #0056b3;
            }}
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background: #545b62;
            }}
            .btn-success {{
                background: #28a745;
                color: white;
            }}
            .btn-success:hover {{
                background: #1e7e34;
            }}
            .category {{
                font-size: 12px;
                background: #e9ecef;
                color: #495057;
                padding: 4px 8px;
                border-radius: 12px;
                margin-bottom: 10px;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📧 MiraiWorks Email Preview</h1>
                <p>Preview and test email templates locally</p>
            </div>

            <div class="content">
                <div class="btn-group" style="margin-bottom: 20px;">
                    <a href="/api/dev/email-preview/all" class="btn btn-success" target="_blank">
                        📋 Preview All Templates
                    </a>
                    <a href="/docs#/Email%20Preview" class="btn btn-secondary" target="_blank">
                        📖 API Documentation
                    </a>
                </div>

                <h2>Available Email Templates</h2>
                <div class="template-grid">
    """

    template_descriptions = {
        "auth/activation": ("User Account Activation", "Sent when a new user account needs to be activated"),
        "auth/2fa_code": ("Two-Factor Authentication", "Verification codes for 2FA login"),
        "admin/company_activation": ("Company Admin Setup", "Sent to new company administrators"),
        "notifications/message_notification": ("Message Notifications", "Alerts for new messages between users")
    }

    for template in templates:
        title, description = template_descriptions.get(template, (template, "Email template"))
        category = template.split('/')[0].title()

        html += f"""
                    <div class="template-card">
                        <div class="category">{category}</div>
                        <h3>{title}</h3>
                        <p>{description}</p>
                        <div class="btn-group">
                            <a href="/api/dev/email-preview/template?name={template}"
                               class="btn btn-primary" target="_blank">
                                👁️ Preview HTML
                            </a>
                            <a href="/api/dev/email-preview/template?name={template}&format=text"
                               class="btn btn-secondary" target="_blank">
                                📄 Preview Text
                            </a>
                        </div>
                    </div>
        """

    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return html


@router.get("/template", response_class=HTMLResponse)
async def preview_template(
    name: str = Query(..., description="Template path (e.g., auth/activation)"),
    format: str = Query("html", description="Format: html or text")
):
    """Preview a specific email template."""
    try:
        preview = email_preview_service.preview_email(name)

        if format.lower() == "text":
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Text Preview: {preview['subject']}</title>
                <style>
                    body {{ font-family: monospace; padding: 20px; background: #f5f5f5; }}
                    .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>📄 Text Version</h2>
                    <p><strong>Subject:</strong> {preview['subject']}</p>
                    <hr>
                    <pre>{preview['text_body']}</pre>
                </div>
            </body>
            </html>
            """
        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Email Preview: {preview['subject']}</title>
                <style>
                    body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f5; }}
                    .preview-header {{ background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .email-preview {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
                </style>
            </head>
            <body>
                <div class="preview-header">
                    <h2 style="margin: 0 0 10px 0; color: #333;">📧 Email Preview</h2>
                    <p style="margin: 0; color: #666;"><strong>Subject:</strong> {preview['subject']}</p>
                    <p style="margin: 5px 0 0 0; color: #666;"><strong>Template:</strong> {preview['template_path']}</p>
                </div>
                <div class="email-preview">
                    {preview['html_body']}
                </div>
            </body>
            </html>
            """

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/all", response_class=HTMLResponse)
async def preview_all_templates():
    """Preview all email templates on one page."""
    try:
        previews = email_preview_service.preview_all_emails()

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>All Email Previews - MiraiWorks</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                    background: #f5f5f5;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .template-section {{
                    margin-bottom: 40px;
                }}
                .template-header {{
                    background: #007bff;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px 8px 0 0;
                    margin: 0;
                }}
                .template-preview {{
                    background: white;
                    border: 1px solid #dee2e6;
                    border-top: none;
                    border-radius: 0 0 8px 8px;
                    overflow: hidden;
                }}
                .error {{
                    background: #f8d7da;
                    color: #721c24;
                    padding: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📧 All Email Template Previews</h1>
                <p>Complete overview of all MiraiWorks email templates</p>
                <a href="/api/dev/email-preview/" style="color: #007bff;">← Back to Dashboard</a>
            </div>
        """

        for template_path, preview in previews.items():
            html += f"""
            <div class="template-section">
                <h2 class="template-header">
                    {template_path.replace('/', ' / ').title()}
                </h2>
                <div class="template-preview">
            """

            if "error" in preview:
                html += f"""
                    <div class="error">
                        <strong>Error:</strong> {preview['error']}
                    </div>
                """
            else:
                html += f"""
                    <div style="padding: 15px; border-bottom: 1px solid #dee2e6; background: #f8f9fa;">
                        <strong>Subject:</strong> {preview['subject']}
                    </div>
                    {preview['html_body']}
                """

            html += """
                </div>
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate previews: {str(e)}")


@router.get("/templates")
async def list_templates():
    """Get list of available email templates."""
    return {
        "templates": email_preview_service.get_available_templates(),
        "count": len(email_preview_service.get_available_templates())
    }