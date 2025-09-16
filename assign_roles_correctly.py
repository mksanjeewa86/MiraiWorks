#!/usr/bin/env python3
"""
Correctly assign roles to users using the proper API format.
Uses the UserUpdate schema with roles array containing UserRole enum values.
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

async def update_user_roles(token, user_id, roles):
    """Update a user's roles using the correct API format."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Use the correct UserUpdate schema format
        update_data = {"roles": roles}

        async with session.put(f"{API_BASE}/api/admin/users/{user_id}",
                              headers=headers, json=update_data) as response:
            if response.status in [200, 204]:
                if response.content_length and response.content_length > 0:
                    return await response.json()
                return True
            else:
                text = await response.text()
                print(f"Failed to update user {user_id}: {response.status} - {text}")
                return None

async def main():
    print("=== CORRECTLY ASSIGNING USER ROLES ===")

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
            roles_text = ", ".join(user.get('roles', [])) if user.get('roles') else "NO ROLES"
            print(f"   - {user['full_name']} ({user['email']}) - ID: {user['id']}")
            print(f"     Roles: [{roles_text}]")
            print(f"     Is Admin: {user.get('is_admin', False)}")

        # Step 4: Assign roles based on email patterns
        print("\n4. Assigning roles...")

        role_assignments = []

        for user in users:
            user_id = user['id']
            email = user['email']
            current_roles = user.get('roles', [])

            print(f"\n   Processing: {user['full_name']} ({email})")

            # Skip if already has roles
            if current_roles:
                print(f"      - Already has roles: {current_roles}")
                continue

            # Determine appropriate role based on email and name patterns
            if email == "admin@example.com" or "superadmin" in email.lower():
                new_roles = ["super_admin"]
                print(f"      -> Assigning super_admin")
            elif "admin" in email.lower() or "Administrator" in user.get('full_name', ''):
                new_roles = ["company_admin"]
                print(f"      -> Assigning company_admin")
            elif "recruiter" in email.lower():
                new_roles = ["recruiter"]
                print(f"      -> Assigning recruiter")
            else:
                print(f"      -> No clear role pattern, assigning company_admin as fallback")
                new_roles = ["company_admin"]

            role_assignments.append((user_id, new_roles))

        # Step 5: Execute role assignments
        print("\n5. Executing role assignments...")

        for user_id, roles in role_assignments:
            print(f"   Updating user {user_id} with roles: {roles}")
            result = await update_user_roles(token, user_id, roles)

            if result:
                print(f"      [OK] Successfully assigned roles: {roles}")
            else:
                print(f"      [FAIL] Failed to assign roles")

        # Step 6: Verify final status
        print("\n6. Final verification...")
        users_after = await get_all_users(token)

        print("   Updated user status:")
        for user in users_after:
            roles_text = ", ".join(user.get('roles', [])) if user.get('roles') else "NO ROLES"
            print(f"   - {user['full_name']} ({user['email']})")
            print(f"     Roles: [{roles_text}]")
            print(f"     Is Admin: {user.get('is_admin', False)}")

        print("\n=== ROLE ASSIGNMENT COMPLETE ===")
        print("You can now test the messaging functionality!")
        print("\nTo test messaging between super_admin and company_admin:")
        print("1. Login as a super_admin user")
        print("2. Try sending message to a company_admin user")
        print("3. Vice versa")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())