#!/usr/bin/env python3
"""
Comprehensive Email Testing Tool for MiraiWorks
Tests various email formats and configurations to diagnose rendering issues
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.email_service import email_service
from app.services.email_preview_service import email_preview_service
from app.config import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailTester:
    def __init__(self):
        self.test_email = "test@example.com"  # Replace with your email for testing

    async def test_basic_html_email(self):
        """Test basic HTML email with minimal styling."""
        print("🧪 Testing basic HTML email...")

        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Email</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
        <h1 style="color: #333; text-align: center;">Email Rendering Test</h1>
        <p style="color: #666; line-height: 1.6;">This is a test email to check HTML rendering.</p>
        <div style="background-color: #007bff; color: white; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
            <strong>This should be a blue box with white text</strong>
        </div>
        <p style="color: #666;">If you see HTML code instead of formatted content, your email client has HTML rendering disabled.</p>
    </div>
</body>
</html>"""

        text_content = """Email Rendering Test

This is a test email to check HTML rendering.

THIS SHOULD BE A BLUE BOX WITH WHITE TEXT

If you see HTML code instead of formatted content, your email client has HTML rendering disabled."""

        success = await email_service.send_email(
            [self.test_email],
            "Email Rendering Test - Basic HTML",
            html_content,
            text_content
        )

        print(f"✅ Basic HTML email sent: {success}")
        return success

    async def test_inline_styles_only(self):
        """Test email with only inline styles (most compatible)."""
        print("🧪 Testing inline styles only...")

        html_content = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<h2 style="color: #333333; margin: 0 0 20px 0;">Your Verification Code</h2>
<p style="color: #666666; margin: 0 0 15px 0;">Hi Company Administrator,</p>
<p style="color: #666666; margin: 0 0 20px 0;">Your two-factor authentication verification code is:</p>
<div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
<h1 style="color: #007bff; letter-spacing: 5px; margin: 0; font-size: 32px;">123456</h1>
</div>
<p style="color: #666666; margin: 0 0 15px 0;">This code will expire in 10 minutes.</p>
<p style="color: #666666; margin: 0;">If you didn't request this code, please ignore this email.</p>
</div>"""

        text_content = """Your Verification Code

Hi Company Administrator,

Your two-factor authentication verification code is: 123456

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email."""

        success = await email_service.send_email(
            [self.test_email],
            "Email Test - Inline Styles Only",
            html_content,
            text_content
        )

        print(f"✅ Inline styles email sent: {success}")
        return success

    async def test_plain_text_only(self):
        """Test plain text only email."""
        print("🧪 Testing plain text only...")

        text_content = """Your Verification Code

Hi Company Administrator,

Your two-factor authentication verification code is: 789012

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

---
This is an automated message from MiraiWorks."""

        # Send text-only email by passing None as html_body
        success = await email_service.send_email(
            [self.test_email],
            "Email Test - Plain Text Only",
            text_content  # Using text as HTML body for text-only
        )

        print(f"✅ Plain text email sent: {success}")
        return success

    def send_raw_multipart_email(self):
        """Send raw multipart email with explicit headers."""
        print("🧪 Testing raw multipart email...")

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Email Test - Raw Multipart'
            msg['From'] = f"{settings.from_name} <{settings.from_email}>"
            msg['To'] = self.test_email
            msg['MIME-Version'] = '1.0'

            # Text part
            text_part = MIMEText("""Your Verification Code

Hi Company Administrator,

Your two-factor authentication verification code is: 456789

This code will expire in 10 minutes.""", 'plain', 'utf-8')

            # HTML part with explicit content-type
            html_content = """<html><body style="font-family: Arial, sans-serif;">
<h2 style="color: #333;">Your Verification Code</h2>
<p>Hi Company Administrator,</p>
<p>Your two-factor authentication verification code is:</p>
<div style="background: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
<h1 style="color: #007bff; letter-spacing: 5px; margin: 0; font-size: 32px;">456789</h1>
</div>
<p>This code will expire in 10 minutes.</p>
</body></html>"""

            html_part = MIMEText(html_content, 'html', 'utf-8')
            html_part.set_charset('utf-8')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send with SMTP
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                elif settings.smtp_use_ssl:
                    server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)

                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)

                server.send_message(msg)

            print(f"✅ Raw multipart email sent successfully")
            return True

        except Exception as e:
            print(f"❌ Raw multipart email failed: {e}")
            return False

    async def test_2fa_template(self):
        """Test the actual 2FA template."""
        print("🧪 Testing 2FA template...")

        success = await email_service.send_2fa_code(
            self.test_email,
            "999888",
            "Test User"
        )

        print(f"✅ 2FA template email sent: {success}")
        return success

    def create_debug_email_files(self):
        """Create debug email files for manual inspection."""
        print("📁 Creating debug email files...")

        try:
            # Get 2FA email preview
            preview = email_preview_service.preview_email("auth/2fa_code")

            # Save HTML version
            with open("debug_2fa_email.html", "w", encoding="utf-8") as f:
                f.write(preview["html_body"])

            # Save text version
            with open("debug_2fa_email.txt", "w", encoding="utf-8") as f:
                f.write(preview["text_body"])

            # Save raw email source
            msg = MIMEMultipart('alternative')
            msg['Subject'] = preview["subject"]
            msg['From'] = f"{settings.from_name} <{settings.from_email}>"
            msg['To'] = "debug@example.com"

            text_part = MIMEText(preview["text_body"], 'plain', 'utf-8')
            html_part = MIMEText(preview["html_body"], 'html', 'utf-8')

            msg.attach(text_part)
            msg.attach(html_part)

            with open("debug_2fa_email_raw.eml", "w", encoding="utf-8") as f:
                f.write(str(msg))

            print("✅ Debug files created:")
            print("   - debug_2fa_email.html (HTML preview)")
            print("   - debug_2fa_email.txt (Text version)")
            print("   - debug_2fa_email_raw.eml (Raw email source)")

        except Exception as e:
            print(f"❌ Failed to create debug files: {e}")

    def print_email_client_tips(self):
        """Print troubleshooting tips for email clients."""
        print("\n" + "="*60)
        print("📧 EMAIL CLIENT TROUBLESHOOTING TIPS")
        print("="*60)
        print("""
If you're seeing raw HTML instead of formatted emails:

1. GMAIL/GOOGLE WORKSPACE:
   • Check if "Always display external images" is enabled
   • Try viewing in different Gmail view (Basic HTML vs Standard)
   • Check if HTML emails are blocked in settings

2. OUTLOOK/OFFICE 365:
   • Go to File > Options > Trust Center > Trust Center Settings
   • Check "Automatic Download" settings
   • Enable HTML email format in Reading Pane

3. APPLE MAIL:
   • Check View > Message > Best Alternative
   • Ensure "Load remote content" is enabled

4. THUNDERBIRD:
   • View > Message Body As > Original HTML
   • Check if HTML rendering is disabled

5. GENERAL TROUBLESHOOTING:
   • Try viewing the email in a different email client
   • Check if your organization blocks HTML emails
   • Look for "View as HTML" or "Enable HTML" options
   • Try forwarding the email to a different email address

6. DEBUG FILES:
   • Check the created debug_2fa_email.html file in browser
   • If HTML file looks correct, it's a client-side rendering issue

""")

async def main():
    """Run comprehensive email tests."""
    print("🚀 Starting comprehensive email testing...")
    print("="*60)

    tester = EmailTester()

    # Update with your test email
    print("⚠️  Please update test_email in the script with your actual email address")
    print(f"📧 Current test email: {tester.test_email}")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Test cancelled")
        return

    results = []

    # Run all tests
    results.append(await tester.test_plain_text_only())
    results.append(await tester.test_inline_styles_only())
    results.append(await tester.test_basic_html_email())
    results.append(tester.send_raw_multipart_email())
    results.append(await tester.test_2fa_template())

    # Create debug files
    tester.create_debug_email_files()

    # Print results
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    test_names = [
        "Plain Text Only",
        "Inline Styles Only",
        "Basic HTML",
        "Raw Multipart",
        "2FA Template"
    ]

    for i, result in enumerate(results):
        status = "✅ SENT" if result else "❌ FAILED"
        print(f"{test_names[i]}: {status}")

    # Print troubleshooting tips
    tester.print_email_client_tips()

    print("\n🎯 Next Steps:")
    print("1. Check your email inbox for the test emails")
    print("2. Compare how different formats render")
    print("3. Open debug_2fa_email.html in your browser")
    print("4. If HTML file renders correctly but email doesn't, it's a client issue")

if __name__ == "__main__":
    asyncio.run(main())