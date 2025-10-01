#!/usr/bin/env python3
"""
Email Client Compatibility Detector
Sends test emails with client detection headers to identify rendering issues
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.services.email_service import email_service


class EmailClientDetector:
    def __init__(self, test_email: str):
        self.test_email = test_email

    def create_detection_html(self) -> str:
        """Create HTML with client detection techniques."""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Client Detection</title>
    <!--[if mso]>
    <p style="color: red; font-weight: bold;">DETECTED: Microsoft Outlook</p>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">

        <h1 style="color: #333333; text-align: center; margin-bottom: 30px;">Email Client Detection Test</h1>

        <!-- Client Detection Indicators -->
        <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #007bff;">Client Detection Results:</h3>

            <!-- Outlook Detection -->
            <!--[if mso]>
            <p style="color: #dc3545; font-weight: bold;">✓ Microsoft Outlook Detected</p>
            <![endif]-->

            <!--[if !mso]><!-->
            <p style="color: #28a745;">✓ Non-Outlook Client (Gmail, Apple Mail, Thunderbird, etc.)</p>
            <!--<![endif]-->
        </div>

        <!-- HTML Rendering Test -->
        <div style="background-color: #e3f2fd; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #2196f3;">
            <h3 style="margin-top: 0; color: #1976d2;">HTML Rendering Test:</h3>
            <p>If you can see this blue box with proper styling, HTML is rendering correctly.</p>

            <!-- Advanced CSS Test -->
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <div style="flex: 1; background-color: #4caf50; color: white; padding: 10px; margin-right: 10px; text-align: center; border-radius: 4px;">
                    CSS Flexbox Test
                </div>
                <div style="flex: 1; background-color: #ff9800; color: white; padding: 10px; margin-left: 10px; text-align: center; border-radius: 4px;">
                    Advanced Styling
                </div>
            </div>
        </div>

        <!-- 2FA Code Example -->
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #856404;">2FA Code Rendering Test:</h3>
            <p style="margin: 0 0 15px 0;">Your verification code is:</p>

            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px; border: 2px solid #007bff;">
                <h1 style="color: #007bff; letter-spacing: 5px; margin: 0; font-size: 32px; font-family: monospace;">123456</h1>
            </div>

            <p style="margin: 0; font-size: 14px; color: #6c757d;">If you see raw HTML code instead of a blue box with the code, your client is not rendering HTML properly.</p>
        </div>

        <!-- Image Loading Test -->
        <div style="background-color: #f1f8ff; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #0366d6;">Image & External Content Test:</h3>
            <p>Some email clients block external images by default.</p>
            <div style="text-align: center; margin: 15px 0;">
                <div style="display: inline-block; width: 50px; height: 50px; background-color: #28a745; border-radius: 25px; line-height: 50px; color: white; font-weight: bold;">✓</div>
            </div>
            <p style="font-size: 14px; color: #6c757d;">This green circle is created with CSS, not an external image.</p>
        </div>

        <!-- Client Troubleshooting -->
        <div style="background-color: #fff; border: 2px solid #dc3545; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #dc3545;">If You See Raw HTML Code:</h3>
            <ul style="padding-left: 20px; color: #495057;">
                <li><strong>Gmail:</strong> Check if you're in "Basic HTML" mode, switch to standard view</li>
                <li><strong>Outlook:</strong> Enable HTML emails in Trust Center settings</li>
                <li><strong>Apple Mail:</strong> Go to View > Message > Best Alternative</li>
                <li><strong>Thunderbird:</strong> View > Message Body As > Original HTML</li>
                <li><strong>Mobile Apps:</strong> Check if HTML emails are enabled in app settings</li>
            </ul>
        </div>

        <!-- Footer -->
        <div style="border-top: 1px solid #dee2e6; padding-top: 20px; margin-top: 30px; text-align: center; color: #6c757d; font-size: 12px;">
            <p>This is a test email from MiraiWorks Email System</p>
            <p>Generated: $(date)</p>
        </div>
    </div>
</body>
</html>"""

    def create_detection_text(self) -> str:
        """Create plain text version."""
        return """Email Client Detection Test

CLIENT DETECTION RESULTS:
- This is the plain text version of the email
- If you're seeing this, your client may prefer text over HTML

HTML RENDERING TEST:
If you can see properly formatted content above this message, HTML is working.
If you see raw HTML code like <div> and <p> tags, HTML rendering is disabled.

2FA CODE RENDERING TEST:
Your verification code is: 123456

If you see raw HTML code instead of formatted styling, your email client has HTML rendering disabled.

CLIENT TROUBLESHOOTING:
- Gmail: Check if you're in "Basic HTML" mode, switch to standard view
- Outlook: Enable HTML emails in Trust Center settings
- Apple Mail: Go to View > Message > Best Alternative
- Thunderbird: View > Message Body As > Original HTML
- Mobile Apps: Check if HTML emails are enabled in app settings

This is a test email from MiraiWorks Email System
"""

    async def send_detection_email(self):
        """Send email client detection test."""
        print(f"📧 Sending detection email to {self.test_email}...")

        html_body = self.create_detection_html()
        text_body = self.create_detection_text()

        success = await email_service.send_email(
            [self.test_email],
            "🔍 Email Client Detection & HTML Rendering Test",
            html_body,
            text_body,
        )

        return success

    def send_minimal_html_test(self):
        """Send the most basic HTML email possible."""
        print("📧 Sending minimal HTML test...")

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "🧪 Minimal HTML Test - MiraiWorks"
            msg["From"] = f"{settings.from_name} <{settings.from_email}>"
            msg["To"] = self.test_email

            # Ultra-simple text
            text_content = """Minimal HTML Test

If you see this message with formatting below, HTML works:

Your code: 789123

If you see HTML tags like <h1> or <div>, HTML is disabled."""

            # Ultra-simple HTML
            html_content = """<html><body>
<h1>Minimal HTML Test</h1>
<p>If you see this message with formatting, HTML works:</p>
<h2 style="color: blue; text-align: center;">Your code: 789123</h2>
<p>If you see HTML tags like &lt;h1&gt; or &lt;div&gt;, HTML is disabled.</p>
</body></html>"""

            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")

            msg.attach(text_part)
            msg.attach(html_part)

            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()

                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)

                server.send_message(msg)

            print("✅ Minimal HTML test sent")
            return True

        except Exception as e:
            print(f"❌ Minimal HTML test failed: {e}")
            return False


async def main():
    """Run email client detection."""
    print("🔍 Email Client Detection Tool")
    print("=" * 50)

    test_email = input("Enter your email address for testing: ").strip()
    if not test_email or "@" not in test_email:
        print("❌ Invalid email address")
        return

    detector = EmailClientDetector(test_email)

    print(f"\n📧 Sending detection emails to: {test_email}")
    print("This will help identify why HTML emails show as raw code.\n")

    # Send detection email
    success1 = await detector.send_detection_email()
    print(f"Detection email sent: {'✅' if success1 else '❌'}")

    # Send minimal test
    success2 = detector.send_minimal_html_test()
    print(f"Minimal HTML test sent: {'✅' if success2 else '❌'}")

    print("\n" + "=" * 50)
    print("📬 Check your email inbox for:")
    print("1. '🔍 Email Client Detection & HTML Rendering Test'")
    print("2. '🧪 Minimal HTML Test'")
    print("\n💡 Next steps:")
    print(
        "- If you see formatted content: HTML works, original issue may be template-specific"
    )
    print("- If you see raw HTML: Your email client has HTML rendering disabled")
    print("- Try different email clients (Gmail web, mobile app, etc.)")
    print("- Check your email client's HTML/formatting settings")


if __name__ == "__main__":
    asyncio.run(main())
