#!/usr/bin/env python3
"""
Complete test of message sending functionality.
1. Create test users
2. Login as admin
3. Send actual message
4. Verify message was sent
"""
import asyncio
import json
import aiohttp

API_BASE = "http://localhost:8000"

async def create_test_company_admin():
    """Create a test company admin user to send messages to."""
    async with aiohttp.ClientSession() as session:
        # First login as super admin to create users
        admin_login = {
            "email": "admin@example.com",
            "password": "admin123"
        }

        async with session.post(f"{API_BASE}/api/auth/login", json=admin_login) as response:
            if response.status != 200:
                print(f"Admin login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return None

            admin_data = await response.json()
            admin_token = admin_data.get("access_token")
            print(f"[OK] Admin logged in successfully")

        # Check if test company admin already exists
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Try to get existing users
        async with session.get(f"{API_BASE}/api/admin/users?page=1&size=20", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                users = data.get("users", [])

                # Look for a company admin
                for user in users:
                    if user.get("email") == "companyadmin@testco.com":
                        print(f"[OK] Found existing test company admin: {user['id']}")
                        return user["id"], admin_token

        print("[INFO] Test company admin not found, would need to create one")
        print("[INFO] For now, let's see what users exist...")

        if users:
            print(f"[INFO] Found {len(users)} users:")
            for user in users[:5]:  # Show first 5
                print(f"  - {user['full_name']} ({user['email']}) - ID: {user['id']}")
                if user.get("is_admin") or user.get("role") == "company_admin":
                    return user["id"], admin_token

        return None, admin_token

async def send_test_message(sender_token, recipient_id):
    """Send a test message from sender to recipient."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {sender_token}", "Content-Type": "application/json"}

        message_data = {
            "recipient_id": recipient_id,
            "content": "Hello! This is a test message from the API test script.",
            "type": "text"
        }

        print(f"[INFO] Sending message to user ID: {recipient_id}")
        print(f"[INFO] Message content: {message_data['content']}")

        async with session.post(f"{API_BASE}/api/direct-messages/send",
                               headers=headers,
                               json=message_data) as response:
            print(f"[INFO] Send message response status: {response.status}")
            text = await response.text()
            print(f"[INFO] Response body: {text}")

            if response.status == 200:
                data = await response.json()
                return data
            elif response.status == 403:
                print("[ERROR] Permission denied - role restrictions may apply")
                return None
            elif response.status == 404:
                print("[ERROR] Recipient not found")
                return None
            else:
                print(f"[ERROR] Unexpected status: {response.status}")
                return None

async def get_conversations(token):
    """Get conversations to verify message was sent."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}

        async with session.get(f"{API_BASE}/api/direct-messages/conversations", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("conversations", [])
            else:
                print(f"[ERROR] Failed to get conversations: {response.status}")
                return []

async def main():
    print("=== COMPLETE MESSAGE SENDING TEST ===")
    print()

    # Step 1: Create/find test users
    print("1. Setting up test users...")
    recipient_id, admin_token = await create_test_company_admin()

    if not recipient_id:
        print("[FAIL] Could not create or find a suitable recipient")
        return

    print(f"[OK] Using recipient ID: {recipient_id}")
    print()

    # Step 2: Send message
    print("2. Sending test message...")
    result = await send_test_message(admin_token, recipient_id)

    if result:
        print("[OK] Message sent successfully!")
        print(f"[INFO] Message ID: {result.get('id')}")
        print(f"[INFO] Sender: {result.get('sender_name')}")
        print(f"[INFO] Recipient: {result.get('recipient_name')}")
        print(f"[INFO] Content: {result.get('content')}")
    else:
        print("[FAIL] Message sending failed")
        return
    print()

    # Step 3: Verify message appears in conversations
    print("3. Verifying message in conversations...")
    conversations = await get_conversations(admin_token)

    if conversations:
        print(f"[OK] Found {len(conversations)} conversation(s)")
        for conv in conversations:
            if conv.get("other_user_id") == recipient_id:
                print(f"[OK] Found conversation with recipient!")
                print(f"[INFO] Last message: {conv.get('last_message', {}).get('content', 'N/A')}")
                break
        else:
            print("[WARN] Conversation with recipient not found in list")
    else:
        print("[WARN] No conversations found")

    print()
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())