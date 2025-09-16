#!/usr/bin/env python3
"""
Complete test to understand and fix the admin contacts issue.
Expected: 2 admins should show in contacts/participants, but only 1 shows.
"""
import asyncio
import aiohttp

API_BASE = "http://localhost:8000"

async def comprehensive_admin_test():
    print("=== COMPREHENSIVE ADMIN CONTACTS TEST ===")

    async with aiohttp.ClientSession() as session:
        # Login as admin
        login_data = {"email": "admin@example.com", "password": "admin123"}

        async with session.post(f"{API_BASE}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print("LOGIN FAILED")
                return
            data = await response.json()
            token = data.get("access_token")

        headers = {"Authorization": f"Bearer {token}"}

        print("\n1. CURRENT USER ANALYSIS")
        print("-" * 40)
        async with session.get(f"{API_BASE}/api/auth/me", headers=headers) as response:
            current_user = await response.json()
            print(f"Logged in as: {current_user.get('full_name')} (ID: {current_user.get('id')})")
            print(f"Email: {current_user.get('email')}")
            # Check if current user has proper role structure
            user_roles = current_user.get('roles', [])
            if isinstance(user_roles, list) and len(user_roles) > 0:
                if isinstance(user_roles[0], dict):
                    role_names = [role['role']['name'] for role in user_roles]
                    print(f"Role names: {role_names}")
                else:
                    print(f"Roles: {user_roles}")
            else:
                print(f"Roles: {user_roles}")

        print("\n2. ALL USERS IN DATABASE")
        print("-" * 40)
        async with session.get(f"{API_BASE}/api/admin/users?page=1&size=100", headers=headers) as response:
            if response.status != 200:
                print(f"Failed to get users: {response.status}")
                return

            data = await response.json()
            users = data.get("users", [])

            admin_users = []
            for user in users:
                roles = user.get('roles', [])
                is_active = user.get('is_active', False)
                is_admin_role = any(role in ['super_admin', 'company_admin'] for role in roles)

                print(f"ID {user['id']:2d}: {user['full_name']:<20} ({user['email']:<20}) Active:{is_active} Roles:{roles}")

                if is_admin_role and is_active:
                    admin_users.append(user)

            print(f"\nActive admin users found: {len(admin_users)}")
            for admin in admin_users:
                print(f"  - {admin['full_name']} (ID: {admin['id']}) - Roles: {admin['roles']}")

        print("\n3. PARTICIPANTS ENDPOINT TEST")
        print("-" * 40)
        async with session.get(f"{API_BASE}/api/direct-messages/participants", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                participants = data.get("participants", [])
                print(f"Participants returned: {len(participants)}")
                for p in participants:
                    print(f"  - {p['full_name']} ({p['email']}) - ID: {p['id']}")
            else:
                text = await response.text()
                print(f"FAILED: {response.status} - {text}")

        print("\n4. MESSAGING LOGIC ANALYSIS")
        print("-" * 40)
        current_user_id = current_user.get('id')
        print(f"Current user ID: {current_user_id}")
        print(f"Current user roles: {role_names if 'role_names' in locals() else 'Unknown'}")
        print("\nMessaging rules:")
        print("- super_admin can message: company_admin users only")
        print("- company_admin can message: super_admin users only")
        print("- other roles can message: anyone (except company_admin)")
        print("\nParticipants logic:")
        print("- Excludes current user")
        print("- Only shows active users")
        print("- Filters by role compatibility")

        print("\n5. EXPECTED VS ACTUAL")
        print("-" * 40)
        print("EXPECTED: 2 admins in contacts")
        print("ACTUAL: 1 admin in contacts")
        print("\nPOSSIBLE ISSUES:")
        print("1. Not enough company_admin users active")
        print("2. Role assignments incorrect")
        print("3. Some users not active")
        print("4. Current user role filtering logic")

        print("\n6. PROPOSED FIX")
        print("-" * 40)

        # Count active company_admins (these should appear for super_admin)
        active_company_admins = [u for u in users if u.get('is_active') and 'company_admin' in u.get('roles', [])]
        active_super_admins = [u for u in users if u.get('is_active') and 'super_admin' in u.get('roles', [])]

        print(f"Active company_admins: {len(active_company_admins)}")
        print(f"Active super_admins: {len(active_super_admins)}")

        if len(active_company_admins) < 2:
            print("\nFIX NEEDED: Create or activate more company_admin users")
            print("Suggestion: Convert one super_admin to company_admin or activate more users")

        if len(participants) < 2:
            print(f"\nCURRENT ISSUE: Only {len(participants)} participant(s) showing")
            print("This suggests we need more active company_admin users")

if __name__ == "__main__":
    asyncio.run(comprehensive_admin_test())