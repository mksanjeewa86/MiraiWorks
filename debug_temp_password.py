#!/usr/bin/env python3
"""
Debug script to test temporary password generation and validation
"""

import asyncio
import sys
sys.path.insert(0, './backend')

from app.services.auth_service import auth_service

def debug_password_operations():
    """Test password hashing and verification."""

    print("🔍 Debugging Temporary Password Operations")
    print("=" * 50)

    # Test 1: Simple password generation and verification
    test_password = "TempPass123"
    print(f"Test Password: '{test_password}'")

    # Hash the password
    hashed = auth_service.get_password_hash(test_password)
    print(f"Hashed Password: {hashed}")

    # Verify the password
    is_valid = auth_service.verify_password(test_password, hashed)
    print(f"Verification Result: {is_valid}")

    # Test 2: Test with different cases
    print("\n" + "-" * 30)
    print("Testing Case Sensitivity:")

    test_cases = [
        test_password,          # Exact match
        test_password.lower(),  # Lowercase
        test_password.upper(),  # Uppercase
        " " + test_password,    # With leading space
        test_password + " ",    # With trailing space
        test_password + "x",    # Wrong password
    ]

    for test_case in test_cases:
        result = auth_service.verify_password(test_case, hashed)
        status = "✅ VALID" if result else "❌ INVALID"
        print(f"'{test_case}' -> {status}")

    # Test 3: Generate password like the system does
    print("\n" + "-" * 30)
    print("Testing System Password Generation:")

    import secrets
    import string

    # This is exactly how the system generates temporary passwords
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    print(f"Generated Temp Password: '{temp_password}'")

    temp_hashed = auth_service.get_password_hash(temp_password)
    print(f"Temp Password Hashed: {temp_hashed}")

    temp_verified = auth_service.verify_password(temp_password, temp_hashed)
    print(f"Temp Password Verification: {'✅ VALID' if temp_verified else '❌ INVALID'}")

    print("\n" + "=" * 50)
    print("🎯 DEBUGGING TIPS:")
    print("1. Check email for exact temporary password (copy carefully)")
    print("2. Ensure no extra spaces or characters")
    print("3. Password is case-sensitive")
    print("4. Check if user was created recently (password should be fresh)")

if __name__ == "__main__":
    debug_password_operations()