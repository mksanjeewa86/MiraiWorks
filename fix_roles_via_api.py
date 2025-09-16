#!/usr/bin/env python3
"""
Fix user roles via API calls to enable messaging functionality.
Uses the admin endpoints to assign proper roles to users.
"""
import asyncio
import aiohttp

API_BASE = "http://localhost:8000"

async def login_as_admin():
    """Login as admin and return the token."""
    async with aiohttp.ClientSession() as session:
        login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"Login failed: {response.status} - {text}")

            data = await response.json()
            return data.get("access_token")

async def get_all_users(token):
    """Get all users from the system."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}

        async with session.get(f"{API_BASE}/api/admin/users?page=1&size=100", headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"Failed to get users: {response.status} - {text}")

            data = await response.json()
            return data.get("users", [])

async def check_available_roles(token):
    """Check what roles are available in the system."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get roles endpoint if it exists
        async with session.get(f"{API_BASE}/api/admin/roles", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Roles endpoint not available: {response.status}")
                return None

async def update_user_role(token, user_id, role_data):
    """Update a user's role via API."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Try updating user with role information
        async with session.put(f"{API_BASE}/api/admin/users/{user_id}",
                              headers=headers, json=role_data) as response:
            if response.status in [200, 204]:
                return True
            else:
                text = await response.text()
                print(f"Failed to update user {user_id}: {response.status} - {text}")
                return False

async def main():
    print("=== FIXING USER ROLES VIA API ===")

    try:
        # Step 1: Login as admin
        print("\n1. Logging in as admin...")
        token = await login_as_admin()
        print("   [OK] Successfully logged in")

        # Step 2: Get all users
        print("\n2. Getting all users...")
        users = await get_all_users(token)
        print(f"   [OK] Found {len(users)} users")

        # Step 3: Show current user status
        print("\n3. Current user status:")
        for user in users:
            print(f"   - {user['full_name']} ({user['email']}) - ID: {user['id']}")
            print(f"     Role: {user.get('role', 'NO ROLE')}")
            print(f"     Is Admin: {user.get('is_admin', False)}")

        # Step 4: Check available roles
        print("\n4. Checking available roles...")
        roles = await check_available_roles(token)
        if roles:
            print(f"   [OK] Available roles: {roles}")
        else:
            print("   - Roles endpoint not available, will try direct assignment")

        # Step 5: Try to assign roles
        print("\n5. Attempting role assignments...")

        for user in users:
            user_id = user['id']
            email = user['email']

            print(f"\n   Processing: {user['full_name']} ({email})")

            # Determine appropriate role
            if email == "admin@example.com" or "superadmin" in email.lower():
                role_assignment = "super_admin"
                print(f"      → Should be super_admin")
            elif "admin" in email.lower():
                role_assignment = "company_admin"
                print(f"      → Should be company_admin")
            else:
                print(f"      → No clear role pattern, skipping")
                continue

            # Try different approaches to assign role
            update_data = {"role": role_assignment}
            success = await update_user_role(token, user_id, update_data)

            if success:
                print(f"      [OK] Successfully assigned {role_assignment}")
            else:
                # Try alternative format
                update_data = {"is_admin": True} if "admin" in role_assignment else {}
                success = await update_user_role(token, user_id, update_data)
                if success:
                    print(f"      [OK] Set admin flag")
                else:
                    print(f"      [FAIL] Failed to assign role")

        # Step 6: Verify final status
        print("\n6. Final verification...")
        users_after = await get_all_users(token)

        print("   Final user status:")
        for user in users_after:
            print(f"   - {user['full_name']} ({user['email']})")
            print(f"     Role: {user.get('role', 'NO ROLE')}")
            print(f"     Is Admin: {user.get('is_admin', False)}")

        print("\n=== ROLE ASSIGNMENT COMPLETE ===")
        print("\nYou can now test the messaging functionality!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())