#!/usr/bin/env python3
"""
Simple File Messaging Demo
This demonstrates the complete file messaging workflow.
"""
import asyncio
import aiohttp
import os
from pathlib import Path
import json

API_BASE = "http://localhost:8000"

async def demo_file_messaging():
    """Complete file messaging workflow demonstration."""
    print("FILE MESSAGING WORKFLOW DEMO")
    print("=" * 50)

    print("\nSTEP 1: Authentication")
    print("-" * 30)

    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {"email": "admin@example.com", "password": "admin123"}

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"[ERROR] Login failed: {response.status}")
                return

            data = await response.json()
            token = data.get("access_token")
            print(f"[SUCCESS] Login successful")

        headers = {"Authorization": f"Bearer {token}"}

        print("\nSTEP 2: Get User Information")
        print("-" * 30)

        async with session.get(f"{API_BASE}/api/auth/me", headers=headers) as response:
            if response.status == 200:
                user_data = await response.json()
                current_user_id = user_data.get('id')
                print(f"[SUCCESS] Current user: {user_data.get('email')} (ID: {current_user_id})")
            else:
                print(f"[ERROR] Could not get user info: {response.status}")
                return

        print("\nSTEP 3: Create Test File")
        print("-" * 30)

        # Create a test file for attachment
        test_filename = "message_attachment.txt"
        test_content = b"Hello! This is a test file attachment.\\n\\nThis file demonstrates:\\n- File upload to messaging\\n- File attachment in messages\\n- File download by recipients"

        # Create file path (simulating successful upload)
        from datetime import datetime
        import uuid

        now = datetime.utcnow()
        unique_id = str(uuid.uuid4())
        file_path = f"uploads/message-attachments/{current_user_id}/{now.year}/{now.month:02d}/{unique_id}_{test_filename}"

        # Create the actual file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(test_content)

        file_info = {
            "file_url": f"/api/files/download/{file_path}",
            "file_name": test_filename,
            "file_size": len(test_content),
            "file_type": "text/plain",
            "s3_key": file_path,
            "success": True,
            "storage_type": "local"
        }

        print(f"[SUCCESS] File created: {test_filename}")
        print(f"  Path: {file_path}")
        print(f"  Size: {len(test_content)} bytes")

        print("\nSTEP 4: Check Available Users and Send Message")
        print("-" * 30)

        # First, let's check what users exist
        async with session.get(f"{API_BASE}/api/admin/users", headers=headers) as users_response:
            if users_response.status == 200:
                users_data = await users_response.json()
                users = users_data.get('users', [])
                print(f"Available users: {len(users)}")
                for user in users[:5]:  # Show first 5 users
                    print(f"  - ID: {user.get('id')}, Email: {user.get('email')}, Role: {user.get('role', 'N/A')}")

                # Find a company admin (since super admin can only message company admins)
                recipient_id = None
                for user in users:
                    if user.get('id') != current_user_id and user.get('role') == 'company_admin':
                        recipient_id = user.get('id')
                        print(f"  Found company admin to message: {user.get('email')}")
                        break

                if not recipient_id:
                    # Try to find any user we can message
                    for user in users:
                        if user.get('id') != current_user_id:
                            recipient_id = user.get('id')
                            print(f"  Trying user: {user.get('email')} (Role: {user.get('role')})")
                            break

                if not recipient_id:
                    print(f"  No other users found, skipping message send (would send to self)")
                    recipient_id = None

            else:
                print(f"  Could not get users list")
                recipient_id = None

        if recipient_id:
            message_data = {
                "content": "Please find the attached document!",
                "recipient_id": recipient_id,
                "file_url": file_info["file_url"],
                "file_name": file_info["file_name"],
                "file_size": file_info["file_size"],
                "file_type": file_info["file_type"]
            }

            print(f"\nSending message with attachment to user {recipient_id}...")

            async with session.post(f"{API_BASE}/api/direct-messages/send",
                                   headers=headers,
                                   json=message_data) as response:

                print(f"  Response status: {response.status}")

                if response.status == 201:
                    message_result = await response.json()
                    print(f"[SUCCESS] Message sent!")
                    print(f"  Message ID: {message_result.get('id')}")
                    message_id = message_result.get('id')
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Message sending failed: {error_text}")
                    message_id = None
        else:
            print(f"\n[INFO] Skipping message send - no suitable recipient found")
            message_id = None

        print("\nSTEP 5: Test File Download")
        print("-" * 30)

        # Test file download access
        download_url = f"{API_BASE}/api/files/download/{file_path}"
        print(f"Testing download: {download_url}")

        async with session.get(download_url, headers=headers) as dl_response:
            print(f"  Download status: {dl_response.status}")

            if dl_response.status == 200:
                content_type = dl_response.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    # Presigned URL response
                    download_data = await dl_response.json()
                    print(f"[SUCCESS] Presigned URL generated")
                else:
                    # Direct file download
                    downloaded_content = await dl_response.read()
                    print(f"[SUCCESS] File downloaded!")
                    print(f"  Downloaded size: {len(downloaded_content)} bytes")
                    print(f"  Content matches: {downloaded_content == test_content}")
            else:
                error_text = await dl_response.text()
                print(f"[ERROR] Download failed: {error_text}")

        if message_id and recipient_id:
            print("\nSTEP 6: Verify Message was Received")
            print("-" * 30)

            async with session.get(f"{API_BASE}/api/direct-messages/with/{recipient_id}",
                                 headers=headers) as msg_response:

                if msg_response.status == 200:
                    messages = await msg_response.json()
                    print(f"[SUCCESS] Retrieved {len(messages)} messages")

                    # Find our message
                    for msg in messages:
                        if msg.get('id') == message_id:
                            print(f"  Found message with attachment:")
                            print(f"    Content: {msg.get('content')}")
                            print(f"    File: {msg.get('file_name', 'No file')}")
                            break
                else:
                    print(f"[ERROR] Could not retrieve messages: {msg_response.status}")
        else:
            print(f"\nSTEP 6: Skipping message verification (no message sent)")

    print("\n" + "=" * 50)
    print("DEMO COMPLETE")
    print("=" * 50)
    print("This demo shows the complete file messaging workflow:")
    print("1. User authentication")
    print("2. File creation/upload")
    print("3. Message sending with file attachment")
    print("4. File download verification")
    print("5. Message retrieval confirmation")
    print(f"\nDemo file created: {file_path}")

if __name__ == "__main__":
    asyncio.run(demo_file_messaging())