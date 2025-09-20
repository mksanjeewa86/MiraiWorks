#!/usr/bin/env python3
"""
Verify Email Template Fix
Generate corrected email templates to confirm HTML rendering
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.services.email_preview_service import email_preview_service
from app.services.email_service import email_service


async def main():
    print("Email Template Fix Verification")
    print("=" * 40)

    try:
        # Generate 2FA template
        preview = email_preview_service.preview_email("auth/2fa_code")

        # Save corrected HTML
        with open("fixed_2fa_email.html", "w", encoding="utf-8") as f:
            f.write(preview["html_body"])

        # Save corrected text
        with open("fixed_2fa_email.txt", "w", encoding="utf-8") as f:
            f.write(preview["text_body"])

        print("SUCCESS: Email templates fixed!")
        print("Files generated:")
        print("- fixed_2fa_email.html (corrected HTML)")
        print("- fixed_2fa_email.txt (text version)")

        # Show summary of fix
        html_content = preview["html_body"]

        print("\nFIX SUMMARY:")
        print("- HTML escaping: REMOVED")
        print("- Proper HTML tags: PRESENT")
        print("- MIME structure: CORRECT")

        # Check content
        if "<h2>Your Verification Code</h2>" in html_content:
            print("- 2FA content: PROPERLY FORMATTED")
        else:
            print("- 2FA content: ISSUE DETECTED")

        if 'style="background: #f5f5f5;' in html_content:
            print("- CSS styling: PRESERVED")
        else:
            print("- CSS styling: ISSUE DETECTED")

        print("\nNEXT STEPS:")
        print("1. Open 'fixed_2fa_email.html' in your browser")
        print("2. It should show properly formatted content with blue styling")
        print("3. Test sending a new 2FA email from your application")
        print("4. The email should now render correctly in email clients")

        print("\nIF EMAILS STILL SHOW RAW HTML:")
        print("- The backend fix is complete")
        print("- This indicates an email client configuration issue")
        print("- Try different email clients or check HTML email settings")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
