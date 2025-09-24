#!/usr/bin/env python3
"""
Standalone Resume Function Tests

This script tests the resume functionality without requiring database setup,
using pure Python testing to validate the business logic and service methods.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

# Import the service classes
from services.resume_service import ResumeService
from schemas.resume import ResumeCreate, ResumeUpdate, WorkExperienceCreate
from utils.constants import ResumeStatus, ResumeVisibility


class TestRunner:
    """Simple test runner for standalone tests."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def assert_equal(self, actual, expected, message=""):
        if actual == expected:
            self.passed += 1
            print(f"✅ PASS: {message}")
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {message} - Expected: {expected}, Got: {actual}"
            print(error_msg)
            self.failures.append(error_msg)

    def assert_true(self, condition, message=""):
        self.assert_equal(condition, True, message)

    def assert_false(self, condition, message=""):
        self.assert_equal(condition, False, message)

    def assert_not_none(self, value, message=""):
        if value is not None:
            self.passed += 1
            print(f"✅ PASS: {message}")
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {message} - Expected non-None value"
            print(error_msg)
            self.failures.append(error_msg)

    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {(self.passed/total*100):.1f}%" if total > 0 else "0%")

        if self.failures:
            print(f"\nFAILURES:")
            for failure in self.failures:
                print(f"  {failure}")


def test_resume_service_utility_methods():
    """Test utility methods that don't require database."""
    test = TestRunner()
    service = ResumeService()

    print("Testing Resume Service Utility Methods")
    print("-" * 40)

    # Test slugify
    test_cases = [
        ("Software Engineer Resume", "software-engineer-resume"),
        ("Full-Stack Developer @ TechCorp!", "full-stack-developer-techcorp"),
        ("Resume with Special Characters #$%", "resume-with-special-characters"),
        ("", ""),
        ("UPPERCASE TITLE", "uppercase-title")
    ]

    for input_text, expected in test_cases:
        result = service._slugify(input_text)
        test.assert_equal(result, expected, f"Slugify '{input_text}'")

    # Test share token generation
    token1 = service._generate_share_token()
    token2 = service._generate_share_token()

    test.assert_equal(len(token1), 32, "Share token length is 32")
    test.assert_true(token1.isalnum(), "Share token is alphanumeric")
    test.assert_true(token1 != token2, "Share tokens are unique")

    # Test password hashing
    password = "test_password_123"
    hashed = service._hash_password(password)

    test.assert_true(hashed != password, "Password is hashed")
    test.assert_true(len(hashed) > 20, "Hash is reasonable length")
    test.assert_true(service._verify_password(password, hashed), "Password verification works")
    test.assert_false(service._verify_password("wrong", hashed), "Wrong password fails")

    # Test data validation
    valid_data = {
        "title": "Software Engineer",
        "full_name": "John Doe",
        "email": "john@example.com"
    }
    invalid_data = {
        "title": "Software Engineer",
        "email": "john@example.com"
        # Missing full_name
    }

    test.assert_true(service.validate_resume_data(valid_data), "Valid data passes validation")
    test.assert_false(service.validate_resume_data(invalid_data), "Invalid data fails validation")

    return test


async def test_resume_service_methods_with_mocks():
    """Test service methods using mocks."""
    test = TestRunner()
    service = ResumeService()

    print("\nTesting Resume Service Methods (Mocked)")
    print("-" * 40)

    # Mock database
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.rollback = AsyncMock()

    # Test create resume with mocked dependencies
    with patch('services.resume_service.Resume') as MockResume:
        with patch.object(service, '_generate_unique_slug', return_value='test-slug'):
            mock_resume = MagicMock()
            mock_resume.id = 1
            mock_resume.title = "Test Resume"
            MockResume.return_value = mock_resume

            resume_data = ResumeCreate(
                title="Test Resume",
                full_name="Test User",
                email="test@example.com"
            )

            try:
                result = await service.create_resume(mock_db, resume_data, 1)
                test.assert_not_none(result, "Resume creation returns result")
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                test.assert_true(True, "Create resume calls database methods")
            except Exception as e:
                test.assert_true(False, f"Create resume failed: {e}")

    # Test CRUD operations with mocks
    with patch('services.resume_service.resume_crud') as mock_crud:
        mock_resume = MagicMock()
        mock_resume.id = 1
        mock_crud.get_with_details.return_value = mock_resume

        result = await service.get_resume(mock_db, 1, 1)
        test.assert_equal(result, mock_resume, "Get resume returns expected result")
        mock_crud.get_with_details.assert_called_once_with(mock_db, id=1, user_id=1)

    # Test public settings update
    with patch('services.resume_service.resume_crud') as mock_crud:
        mock_resume = MagicMock()
        mock_crud.update_public_settings.return_value = mock_resume

        result = await service.update_public_settings(mock_db, 1, 1, True, "custom-slug")
        test.assert_equal(result, mock_resume, "Update public settings returns result")
        mock_crud.update_public_settings.assert_called_once()

    # Test download count increment
    with patch('services.resume_service.resume_crud') as mock_crud:
        mock_crud.increment_download.return_value = True

        result = await service.increment_download_count(mock_db, 1)
        test.assert_true(result, "Increment download count succeeds")
        mock_crud.increment_download.assert_called_once_with(mock_db, resume_id=1)

    # Test email sending (mock implementation)
    mock_resume = MagicMock()
    mock_resume.id = 1

    result = await service.send_resume_email(
        mock_db, mock_resume, ["test@example.com"], "Subject", "Message"
    )
    test.assert_true(result, "Send resume email returns success")

    return test


def test_resume_schemas():
    """Test resume schema validation."""
    test = TestRunner()

    print("\nTesting Resume Schemas")
    print("-" * 40)

    # Test valid resume creation data
    try:
        valid_data = ResumeCreate(
            title="Software Engineer Resume",
            full_name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            location="San Francisco, CA"
        )
        test.assert_equal(valid_data.title, "Software Engineer Resume", "Resume title set correctly")
        test.assert_equal(valid_data.full_name, "John Doe", "Full name set correctly")
        test.assert_equal(valid_data.email, "john.doe@example.com", "Email set correctly")
    except Exception as e:
        test.assert_true(False, f"Valid ResumeCreate failed: {e}")

    # Test resume update data
    try:
        update_data = ResumeUpdate(
            title="Updated Resume Title",
            status=ResumeStatus.PUBLISHED
        )
        test.assert_equal(update_data.title, "Updated Resume Title", "Update title set correctly")
        test.assert_equal(update_data.status, ResumeStatus.PUBLISHED, "Status set correctly")
    except Exception as e:
        test.assert_true(False, f"Valid ResumeUpdate failed: {e}")

    # Test work experience creation
    try:
        work_exp = WorkExperienceCreate(
            company_name="TechCorp Inc.",
            position_title="Software Engineer",
            start_date=datetime(2020, 1, 1),
            is_current=True,
            description="Full-stack development"
        )
        test.assert_equal(work_exp.company_name, "TechCorp Inc.", "Company name set correctly")
        test.assert_equal(work_exp.position_title, "Software Engineer", "Position title set correctly")
        test.assert_true(work_exp.is_current, "Current position flag set correctly")
    except Exception as e:
        test.assert_true(False, f"Valid WorkExperienceCreate failed: {e}")

    return test


def test_constants_and_enums():
    """Test constants and enum values."""
    test = TestRunner()

    print("\nTesting Constants and Enums")
    print("-" * 40)

    # Test ResumeStatus enum
    test.assert_equal(ResumeStatus.DRAFT, "draft", "Draft status value")
    test.assert_equal(ResumeStatus.PUBLISHED, "published", "Published status value")
    test.assert_equal(ResumeStatus.ARCHIVED, "archived", "Archived status value")

    # Test ResumeVisibility enum
    test.assert_equal(ResumeVisibility.PRIVATE, "private", "Private visibility value")
    test.assert_equal(ResumeVisibility.PUBLIC, "public", "Public visibility value")
    test.assert_equal(ResumeVisibility.UNLISTED, "unlisted", "Unlisted visibility value")

    return test


def test_business_logic_scenarios():
    """Test business logic scenarios."""
    test = TestRunner()

    print("\nTesting Business Logic Scenarios")
    print("-" * 40)

    # Test resume creation workflow
    service = ResumeService()

    # Test slug generation for various titles
    test_titles = [
        "Software Engineer Resume",
        "Full-Stack Developer Position",
        "Data Science & Analytics Role",
        "Project Manager at StartupCorp"
    ]

    for title in test_titles:
        slug = service._slugify(title)
        test.assert_true(len(slug) > 0, f"Slug generated for '{title}'")
        test.assert_true(slug.islower(), f"Slug is lowercase for '{title}'")
        test.assert_false(' ' in slug, f"Slug has no spaces for '{title}'")

    # Test validation scenarios
    validation_cases = [
        ({"title": "Test", "full_name": "User", "email": "test@example.com"}, True),
        ({"title": "", "full_name": "User", "email": "test@example.com"}, False),
        ({"full_name": "User", "email": "test@example.com"}, False),  # No title
        ({"title": "Test", "email": "test@example.com"}, False),  # No full_name
        ({"title": "Test", "full_name": "User"}, False),  # No email
    ]

    for data, expected in validation_cases:
        result = service.validate_resume_data(data)
        test.assert_equal(result, expected, f"Validation for {list(data.keys())}")

    return test


async def main():
    """Run all tests."""
    print("🧪 RESUME FUNCTION COMPREHENSIVE TESTING")
    print("=" * 60)

    # Run all test suites
    tests = []

    # Utility methods test
    tests.append(test_resume_service_utility_methods())

    # Service methods with mocks test
    tests.append(await test_resume_service_methods_with_mocks())

    # Schema tests
    tests.append(test_resume_schemas())

    # Constants tests
    tests.append(test_constants_and_enums())

    # Business logic tests
    tests.append(test_business_logic_scenarios())

    # Aggregate results
    total_passed = sum(t.passed for t in tests)
    total_failed = sum(t.failed for t in tests)

    print(f"\n{'='*60}")
    print(f"OVERALL TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total tests run: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")

    if total_failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"💥 {total_failed} TESTS FAILED")
        print("\nFailure details:")
        for i, test in enumerate(tests, 1):
            if test.failures:
                print(f"\nTest Suite {i} failures:")
                for failure in test.failures:
                    print(f"  {failure}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)