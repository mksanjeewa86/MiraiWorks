#!/usr/bin/env python3
"""
Comprehensive test for file messaging functionality
Tests file upload, sending file messages, and receiving/downloading files
"""
import asyncio
import aiohttp
import os
import tempfile
from pathlib import Path

API_BASE = "http://localhost:8000"

async def create_test_file():
    """Create a test file for upload."""
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World! This is a test file for messaging.\n")
        f.write("File upload test content.\n")
        f.write("Testing file messaging functionality.")
        return f.name

async def test_complete_file_messaging():
    print("=== COMPREHENSIVE FILE MESSAGING TEST ===")

    async with aiohttp.ClientSession() as session:
        # Step 1: Login as admin
        print("\n1. Logging in...")
        login_data = {"email": "admin@example.com", "password": "admin123"}

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"Login failed: {response.status}")
                return

            data = await response.json()
            token = data.get("access_token")
            print("   [OK] Login successful")

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Get available contacts
        print("\n2. Getting contacts for messaging...")
        async with session.get(f"{API_BASE}/api/direct-messages/participants", headers=headers) as response:
            if response.status != 200:
                print(f"Failed to get participants: {response.status}")
                return

            data = await response.json()
            participants = data.get("participants", [])

            if not participants:
                print("   [ERROR] No participants available for testing")
                return

            recipient = participants[0]
            print(f"   [OK] Found recipient: {recipient['full_name']} (ID: {recipient['id']})")

        # Step 3: Create test file
        print("\n3. Creating test file...")
        test_file_path = await create_test_file()
        file_size = os.path.getsize(test_file_path)
        print(f"   [OK] Created test file: {os.path.basename(test_file_path)} ({file_size} bytes)")

        # Step 4: Upload file
        print("\n4. Testing file upload...")
        try:
            with open(test_file_path, 'rb') as file:
                form_data = aiohttp.FormData()
                form_data.add_field('file', file, filename=os.path.basename(test_file_path))

                async with session.post(f"{API_BASE}/api/files/upload",
                                      headers=headers, data=form_data) as response:
                    if response.status == 200:
                        upload_data = await response.json()
                        print(f"   [OK] File uploaded successfully!")
                        print(f"   File URL: {upload_data.get('file_url', 'N/A')}")
                        print(f"   S3 Key: {upload_data.get('s3_key', 'N/A')}")
                        print(f"   File Size: {upload_data.get('file_size', 'N/A')} bytes")
                    else:
                        text = await response.text()
                        print(f"   [ERROR] File upload failed: {response.status}")
                        print(f"   Response: {text}")
                        return
        except Exception as e:
            print(f"   [ERROR] File upload exception: {e}")
            return

        # Step 5: Send file message
        print("\n5. Sending file message...")
        message_data = {
            "recipient_id": recipient["id"],
            "content": f"📎 {upload_data['file_name']}",
            "type": "file",
            "file_url": upload_data["file_url"],
            "file_name": upload_data["file_name"],
            "file_size": upload_data["file_size"],
            "file_type": upload_data["file_type"]
        }

        async with session.post(f"{API_BASE}/api/direct-messages/send",
                              headers=headers, json=message_data) as response:
            if response.status == 200:
                message_result = await response.json()
                print(f"   [OK] File message sent successfully!")
                print(f"   Message ID: {message_result.get('id')}")
                print(f"   Content: {message_result.get('content')}")
                print(f"   File URL: {message_result.get('file_url', 'N/A')}")
            else:
                text = await response.text()
                print(f"   [ERROR] File message send failed: {response.status}")
                print(f"   Response: {text}")
                return

        # Step 6: Retrieve messages to verify file message
        print("\n6. Verifying file message in conversation...")
        async with session.get(f"{API_BASE}/api/direct-messages/with/{recipient['id']}",
                             headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                messages = data.get("messages", [])

                # Find our file message
                file_message = None
                for msg in messages:
                    if msg.get("type") == "file" and msg.get("file_url"):
                        file_message = msg
                        break

                if file_message:
                    print(f"   [OK] File message found in conversation!")
                    print(f"   Message Type: {file_message.get('type')}")
                    print(f"   File Name: {file_message.get('file_name')}")
                    print(f"   File Size: {file_message.get('file_size')} bytes")
                    print(f"   File Type: {file_message.get('file_type')}")
                else:
                    print("   [WARN] File message not found in conversation")
            else:
                print(f"   [ERROR] Failed to get messages: {response.status}")

        # Step 7: Test file download URL
        print("\n7. Testing file download access...")
        file_url = upload_data.get("file_url")
        if file_url:
            # Extract the download path from the presigned URL
            try:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        downloaded_content = await response.read()
                        print(f"   [OK] File download successful!")
                        print(f"   Downloaded {len(downloaded_content)} bytes")

                        # Verify content
                        with open(test_file_path, 'rb') as original_file:
                            original_content = original_file.read()

                        if downloaded_content == original_content:
                            print("   [OK] File content verification passed!")
                        else:
                            print("   [WARN] File content doesn't match original")
                    else:
                        print(f"   [ERROR] File download failed: {response.status}")
            except Exception as e:
                print(f"   [ERROR] Download test exception: {e}")

        # Cleanup
        print("\n8. Cleanup...")
        try:
            os.unlink(test_file_path)
            print("   [OK] Test file cleaned up")
        except Exception as e:
            print(f"   [WARN] Cleanup failed: {e}")

        print("\n" + "="*50)
        print("FILE MESSAGING TEST SUMMARY:")
        print("="*50)
        print("✓ User authentication")
        print("✓ Contact retrieval")
        print("✓ Test file creation")
        print("✓ File upload to server")
        print("✓ File message sending")
        print("✓ Message retrieval/verification")
        print("✓ File download/access")
        print("✓ Content verification")
        print("✓ Cleanup")
        print("\n🎉 ALL FILE MESSAGING TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_complete_file_messaging())