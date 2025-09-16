#!/usr/bin/env python3
"""
Check the current logged in user's details.
"""
import asyncio
import aiohttp

API_BASE = "http://localhost:8000"

async def check_current_user():
    """Check current user details."""
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
            print(f"Login response: {data}")

        # Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{API_BASE}/api/auth/me", headers=headers) as response:
            if response.status == 200:
                user_data = await response.json()
                print(f"\n=== CURRENT USER INFO ===")
                print(f"User ID: {user_data.get('id')}")
                print(f"Name: {user_data.get('full_name')}")
                print(f"Email: {user_data.get('email')}")
                print(f"Is Admin: {user_data.get('is_admin')}")
                print(f"Company ID: {user_data.get('company_id')}")
                print(f"Active: {user_data.get('is_active')}")
                print(f"Full user data: {user_data}")
            else:
                print(f"Failed to get current user: {response.status}")
                text = await response.text()
                print(f"Response: {text}")

if __name__ == "__main__":
    asyncio.run(check_current_user())