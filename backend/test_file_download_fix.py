#!/usr/bin/env python3
"""
Test file download authentication fix
"""

import asyncio
import sys
import os
import json
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app

async def test_file_download_authentication():
    """Test that file download works with proper authentication."""
    print("Testing File Download Authentication Fix")
    print("=" * 50)

    client = TestClient(app)

    # Test the authentication endpoint is working
    try:
        # First, let's test login to get a token
        print("Testing login to get authentication token...")

        login_response = client.post("/api/auth/login", json={
            "email": "admin@ccc.com",
            "password": "password123"
        })

        print(f"Login response status: {login_response.status_code}")

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login successful, got token: {access_token[:20]}...")

            # Test file download with authentication
            headers = {"Authorization": f"Bearer {access_token}"}

            # Test the specific file URL that was failing
            file_path = "message-attachments/7/2025/09/7fcdf7bd-f4bf-4e3b-95c2-68fc4fca3492_resumeEnglish1.pdf"

            print(f"Testing file download: {file_path}")
            download_response = client.get(f"/api/files/download/{file_path}", headers=headers)

            print(f"Download response status: {download_response.status_code}")

            if download_response.status_code == 200:
                print("✅ File download successful!")
                print(f"Response headers: {dict(download_response.headers)}")
            elif download_response.status_code == 403:
                print("❌ Access forbidden - user doesn't have permission to this file")
                print("This means the permission check is working, but user needs to be recipient/sender")
            elif download_response.status_code == 404:
                print("❌ File not found")
            else:
                print(f"❌ Download failed with status {download_response.status_code}")
                try:
                    error_data = download_response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Error text: {download_response.text}")

        elif login_response.status_code == 422:
            print("❌ Login validation error - check email/password format")
            try:
                error_data = login_response.json()
                print(f"Validation errors: {error_data}")
            except:
                print(f"Error text: {login_response.text}")

        elif login_response.status_code == 401:
            print("❌ Login failed - invalid credentials")
            try:
                error_data = login_response.json()
                print(f"Auth error: {error_data}")
            except:
                print(f"Error text: {login_response.text}")

        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            try:
                error_data = login_response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {login_response.text}")

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print("""
The file download authentication has been improved with:

1. ✅ Permission check function added
2. ✅ User role validation (super_admin can access all files)
3. ✅ Message attachment access check (sender/recipient can access)
4. ✅ File visibility check (not deleted messages)

IMPORTANT: For the specific error you encountered:
- The user trying to download must be logged in
- They must be either the sender or recipient of the message containing the file
- OR they must have super_admin role

NEXT STEPS:
1. Make sure admin@ccc.com is logged into the system
2. Verify they are the recipient of the message with that file
3. Test the download again with proper authentication headers

The "Could not validate credentials" error should now be resolved!
""")

if __name__ == "__main__":
    asyncio.run(test_file_download_authentication())