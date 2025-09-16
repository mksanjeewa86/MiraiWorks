#!/usr/bin/env python3
"""
Debug script for file upload functionality
"""
import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8000"

async def test_file_upload_debug():
    print("=== FILE UPLOAD DEBUG TEST ===")

    async with aiohttp.ClientSession() as session:
        # Step 1: Login
        print("\n1. Logging in...")
        login_data = {"email": "admin@example.com", "password": "admin123"}

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"   [ERROR] Login failed: {response.status}")
                return

            data = await response.json()
            token = data.get("access_token")
            print(f"   [OK] Login successful, token: {token[:20]}...")

        # Step 2: Test auth endpoint access
        print("\n2. Testing authenticated access...")
        headers = {"Authorization": f"Bearer {token}"}

        async with session.get(f"{API_BASE}/api/auth/me", headers=headers) as response:
            if response.status == 200:
                user_data = await response.json()
                print(f"   [OK] Auth working, user ID: {user_data.get('id')}")
            else:
                print(f"   [ERROR] Auth check failed: {response.status}")
                return

        # Step 3: Test file upload with minimal data
        print("\n3. Testing file upload...")

        # Create the simplest possible test file
        test_content = b"Hello World"

        # Create form data
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_content, filename='hello.txt', content_type='text/plain')

        print(f"   Uploading file: hello.txt ({len(test_content)} bytes)")
        print(f"   Content-Type: text/plain")
        print(f"   Using headers: Authorization: Bearer {token[:10]}...")

        try:
            async with session.post(f"{API_BASE}/api/files/upload",
                                  headers=headers,
                                  data=form_data) as response:

                print(f"   Response status: {response.status}")
                print(f"   Response headers: {dict(response.headers)}")

                if response.status == 200:
                    data = await response.json()
                    print(f"   [SUCCESS] Upload successful!")
                    print(f"   Response data:")
                    for key, value in data.items():
                        print(f"     {key}: {value}")
                else:
                    # Get detailed error information
                    try:
                        error_data = await response.json()
                        print(f"   [ERROR] Upload failed with JSON error:")
                        print(f"   {json.dumps(error_data, indent=2)}")
                    except:
                        text = await response.text()
                        print(f"   [ERROR] Upload failed with text error:")
                        print(f"   {text}")

        except Exception as e:
            print(f"   [EXCEPTION] Upload request failed: {e}")

        # Step 4: Check if uploads directory was created
        print("\n4. Checking local file system...")
        import os
        from pathlib import Path

        uploads_path = Path("backend/uploads")
        print(f"   Checking path: {uploads_path.absolute()}")
        print(f"   Path exists: {uploads_path.exists()}")

        if uploads_path.exists():
            print(f"   Contents: {list(uploads_path.rglob('*'))}")

if __name__ == "__main__":
    asyncio.run(test_file_upload_debug())