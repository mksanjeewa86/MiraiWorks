#!/usr/bin/env python3
"""
Debug script to check user roles in the database.
"""
import asyncio
import aiohttp

API_BASE = "http://localhost:8000"

async def debug_user_roles():
    """Check what users exist and their role assignments."""
    async with aiohttp.ClientSession() as session:
        # Login as admin
        login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"Login failed: {response.status}")
                return

            data = await response.json()
            token = data.get("access_token")

        print(f"[OK] Logged in successfully")

        # Get users
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{API_BASE}/api/admin/users?page=1&size=50", headers=headers) as response:
            if response.status != 200:
                print(f"Failed to get users: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return

            data = await response.json()
            users = data.get("users", [])

        print(f"\n=== USERS IN SYSTEM ({len(users)}) ===")
        for user in users:
            print(f"\nUser ID: {user['id']}")
            print(f"  Name: {user['full_name']}")
            print(f"  Email: {user['email']}")
            print(f"  Is Admin: {user.get('is_admin', False)}")
            print(f"  Role: {user.get('role', 'NO ROLE')}")
            print(f"  Company ID: {user.get('company_id', 'NO COMPANY')}")
            print(f"  Active: {user.get('is_active', False)}")

        # Now try to get participants to see what the messaging API returns
        print(f"\n=== PARTICIPANTS FOR MESSAGING ===")
        async with session.get(f"{API_BASE}/api/direct-messages/participants", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                participants = data.get("participants", [])
                print(f"Found {len(participants)} participants:")
                for p in participants:
                    print(f"  - {p['full_name']} ({p['email']}) - ID: {p['id']}")
            else:
                print(f"Failed to get participants: {response.status}")
                text = await response.text()
                print(f"Response: {text}")

if __name__ == "__main__":
    asyncio.run(debug_user_roles())