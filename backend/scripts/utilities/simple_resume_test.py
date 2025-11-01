#!/usr/bin/env python3
"""
Simple Resume Function Test

Test resume functionality without database dependencies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from services.resume_service import ResumeService  # type: ignore[import-not-found]


def test_resume_service_basics():
    """Test basic resume service functionality."""
    print("Testing Resume Service Basics")
    print("-" * 40)

    service = ResumeService()
    passed = 0
    failed = 0

    # Test slugify
    test_cases = [
        ("Software Engineer Resume", "software-engineer-resume"),
        ("Full-Stack Developer", "full-stack-developer"),
        ("Test Title!", "test-title"),
    ]

    for input_text, expected in test_cases:
        result = service._slugify(input_text)
        if result == expected:
            print(f"PASS: Slugify '{input_text}' -> '{result}'")
            passed += 1
        else:
            print(f"FAIL: Slugify '{input_text}' expected '{expected}' got '{result}'")
            failed += 1

    # Test share token generation
    token = service._generate_share_token()
    if len(token) == 32:
        print("PASS: Share token length is 32")
        passed += 1
    else:
        print(f"FAIL: Share token length is {len(token)}, expected 32")
        failed += 1

    if token.isalnum():
        print("PASS: Share token is alphanumeric")
        passed += 1
    else:
        print("FAIL: Share token contains non-alphanumeric characters")
        failed += 1

    # Test data validation
    valid_data = {
        "title": "Software Engineer",
        "full_name": "John Doe",
        "email": "john@example.com",
    }

    if service.validate_resume_data(valid_data):
        print("PASS: Valid data passes validation")
        passed += 1
    else:
        print("FAIL: Valid data failed validation")
        failed += 1

    invalid_data = {
        "title": "Software Engineer",
        "email": "john@example.com",
        # Missing full_name
    }

    if not service.validate_resume_data(invalid_data):
        print("PASS: Invalid data fails validation")
        passed += 1
    else:
        print("FAIL: Invalid data passed validation")
        failed += 1

    # Test password hashing
    password = "test_password"
    hashed = service._hash_password(password)

    if hashed != password:
        print("PASS: Password is hashed")
        passed += 1
    else:
        print("FAIL: Password was not hashed")
        failed += 1

    if service._verify_password(password, hashed):
        print("PASS: Password verification works")
        passed += 1
    else:
        print("FAIL: Password verification failed")
        failed += 1

    if not service._verify_password("wrong_password", hashed):
        print("PASS: Wrong password verification fails correctly")
        passed += 1
    else:
        print("FAIL: Wrong password verification passed incorrectly")
        failed += 1

    print(f"\nSUMMARY: {passed} passed, {failed} failed")
    return failed == 0


def test_constants():
    """Test constants are properly defined."""
    print("\nTesting Constants")
    print("-" * 40)

    try:
        from utils.constants import (  # type: ignore[import-not-found]
            ResumeStatus,
            ResumeVisibility,
        )

        # Test ResumeStatus values
        assert ResumeStatus.DRAFT == "draft"
        assert ResumeStatus.PUBLISHED == "published"
        assert ResumeStatus.ARCHIVED == "archived"
        print("PASS: ResumeStatus constants are correct")

        # Test ResumeVisibility values
        assert ResumeVisibility.PRIVATE == "private"
        assert ResumeVisibility.PUBLIC == "public"
        assert ResumeVisibility.UNLISTED == "unlisted"
        print("PASS: ResumeVisibility constants are correct")

        return True
    except Exception as e:
        print(f"FAIL: Constants test failed: {e}")
        return False


def test_schema_imports():
    """Test that schemas can be imported and used."""
    print("\nTesting Schema Imports")
    print("-" * 40)

    try:
        from schemas.resume import (  # type: ignore[import-not-found]
            ResumeCreate,
            ResumeUpdate,
        )

        # Test ResumeCreate
        resume_data = ResumeCreate(
            title="Test Resume", full_name="Test User", email="test@example.com"
        )
        print(f"PASS: ResumeCreate schema works: {resume_data.title}")

        # Test ResumeUpdate
        update_data = ResumeUpdate(title="Updated Title")
        print(f"PASS: ResumeUpdate schema works: {update_data.title}")

        return True
    except Exception as e:
        print(f"FAIL: Schema import test failed: {e}")
        return False


if __name__ == "__main__":
    print("RESUME FUNCTION TESTING")
    print("=" * 40)

    all_passed = True

    # Run tests
    all_passed &= test_resume_service_basics()
    all_passed &= test_constants()
    all_passed &= test_schema_imports()

    print("\n" + "=" * 40)
    if all_passed:
        print("ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED!")
        sys.exit(1)
