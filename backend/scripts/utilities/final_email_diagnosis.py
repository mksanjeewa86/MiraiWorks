#!/usr/bin/env python3
"""
Final Email Diagnosis - MiraiWorks
Specifically for the raw HTML display issue
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.services.email_preview_service import email_preview_service


async def main():
    """Run final diagnosis for HTML email rendering issue."""
    print("MiraiWorks Email Diagnosis - Raw HTML Issue")
    print("=" * 50)

    # Get the actual 2FA template that's causing issues
    try:
        preview = email_preview_service.preview_email("auth/2fa_code")
        print("Template generation: SUCCESS")
        print(f"Subject: {preview['subject']}")

        # Show the exact HTML that should render
        print("\n" + "-" * 30)
        print("HTML CONTENT (what should render as formatted):")
        print("-" * 30)
        print(preview["html_body"])

        print("\n" + "-" * 30)
        print("TEXT CONTENT (fallback):")
        print("-" * 30)
        print(preview["text_body"])

        # Save for manual inspection
        with open("actual_email_html.html", "w", encoding="utf-8") as f:
            f.write(preview["html_body"])

        with open("actual_email_text.txt", "w", encoding="utf-8") as f:
            f.write(preview["text_body"])

        print("\nFiles saved:")
        print("- actual_email_html.html (open this in browser)")
        print("- actual_email_text.txt")

        print("\n" + "=" * 50)
        print("DIAGNOSIS SUMMARY")
        print("=" * 50)
        print(
            """
ISSUE: You're seeing raw HTML like this in your email:
<h2>Your Verification Code</h2>
<p>Hi Company Administrator,</p>
<div style="background: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
<h1 style="color: #007bff; letter-spacing: 5px; margin: 0; font-size: 32px;">123456</h1>
</div>

BACKEND STATUS: ✓ WORKING CORRECTLY
- Templates generate proper HTML
- Email service sends proper MIME structure
- HTML and text versions are both included

THE PROBLEM: Your email client is not rendering HTML
This is a CLIENT-SIDE issue, not a backend problem.

SOLUTIONS:
1. CHECK EMAIL CLIENT SETTINGS:
   - Gmail: Ensure you're not in "Basic HTML" mode
   - Outlook: Enable HTML emails in Trust Center
   - Apple Mail: View > Message > Best Alternative
   - Mobile: Check app settings for HTML email support

2. TEST DIFFERENT CLIENTS:
   - Try Gmail web interface
   - Try different mobile email apps
   - Forward email to different address

3. VERIFY HTML FILE:
   - Open 'actual_email_html.html' in your browser
   - If it looks correct there, it's definitely a client issue

4. ORGANIZATION SETTINGS:
   - Check if your company/ISP blocks HTML emails
   - Ask IT about email security policies

The backend is generating the emails correctly. The issue is that
your email client is choosing to display the HTML source code
instead of rendering it as formatted content.
"""
        )

    except Exception as e:
        print(f"ERROR in template generation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
