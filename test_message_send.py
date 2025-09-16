#!/usr/bin/env python3
"""
Test script to verify the direct message sending functionality.
"""
import asyncio
import json
import aiohttp

API_BASE = "http://localhost:8000"

async def login_and_get_token():
    """Login and get authentication token."""
    async with aiohttp.ClientSession() as session:
        # Try to login with a test user from the backend tests
        login_data = {
            "email": "admin@example.com",     # Admin email from test fixtures
            "password": "admin123"            # From create_working_admin.py
        }

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("access_token")
            else:
                print(f"Login failed with status {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return None

async def get_participants(token):
    """Get available message participants."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}

        async with session.get(f"{API_BASE}/api/direct-messages/participants", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("participants", [])
            else:
                print(f"Failed to get participants: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return []

async def send_message(token, recipient_id, content):
    """Send a test message."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        message_data = {
            "recipient_id": recipient_id,
            "content": content,
            "type": "text"
        }

        async with session.post(f"{API_BASE}/api/direct-messages/send",
                               headers=headers,
                               json=message_data) as response:
            print(f"Send message response status: {response.status}")
            text = await response.text()
            print(f"Response body: {text}")

            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None

async def main():
    print("Testing Direct Message Sending...")

    # Step 1: Login and get token
    print("\n1. Logging in...")
    token = await login_and_get_token()
    if not token:
        print("[FAIL] Login failed - cannot proceed")
        return
    print(f"[OK] Login successful, token: {token[:20]}...")

    # Step 2: Get participants
    print("\n2. Getting participants...")
    participants = await get_participants(token)
    print(f"[OK] Found {len(participants)} participants")
    for p in participants[:3]:  # Show first 3
        print(f"  - {p['full_name']} ({p['email']}) - ID: {p['id']}")

    if not participants:
        print("[FAIL] No participants found - cannot send message")
        return

    # Step 3: Send test message to first participant
    recipient = participants[0]
    print(f"\n3. Sending test message to {recipient['full_name']}...")

    result = await send_message(token, recipient['id'], "Hello! This is a test message from the API.")

    if result:
        print("[OK] Message sent successfully!")
        print(f"Message ID: {result.get('id')}")
        print(f"Content: {result.get('content')}")
    else:
        print("[FAIL] Failed to send message")

if __name__ == "__main__":
    asyncio.run(main())