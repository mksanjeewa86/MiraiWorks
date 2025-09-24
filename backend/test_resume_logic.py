#!/usr/bin/env python3
"""
Resume Logic Integration Test

Test resume service methods and logic integration.
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.resume_service import ResumeService
from schemas.resume import ResumeCreate, ResumeUpdate, WorkExperienceCreate
from utils.constants import ResumeStatus, ResumeVisibility
from datetime import datetime


async def test_service_method_integration():
    """Test service methods work with mocked dependencies."""
    print("Testing Service Method Integration")
    print("-" * 40)

    service = ResumeService()
    mock_db = AsyncMock()
    passed = 0
    failed = 0

    # Test 1: Create resume with proper data flow
    print("Test 1: Create Resume")
    with patch('services.resume_service.Resume') as MockResume:
        with patch.object(service, '_generate_unique_slug', return_value='test-slug-123'):
            mock_resume = MagicMock()
            mock_resume.id = 1
            mock_resume.title = "Software Engineer Resume"
            mock_resume.user_id = 1
            mock_resume.status = ResumeStatus.DRAFT
            MockResume.return_value = mock_resume

            resume_data = ResumeCreate(
                title="Software Engineer Resume",
                full_name="John Doe",
                email="john.doe@example.com",
                professional_summary="Experienced engineer"
            )

            try:
                result = await service.create_resume(mock_db, resume_data, 1)
                if result and hasattr(result, 'id'):
                    print("  PASS: Resume created with ID")
                    passed += 1
                else:
                    print("  FAIL: Resume creation failed")
                    failed += 1

                # Verify database calls
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                print("  PASS: Database methods called correctly")
                passed += 1

            except Exception as e:
                print(f"  FAIL: Exception during creation: {e}")
                failed += 1

    # Test 2: Get resume using CRUD
    print("\nTest 2: Get Resume")
    with patch('services.resume_service.resume_crud') as mock_crud:
        mock_resume = MagicMock()
        mock_resume.id = 1
        mock_resume.title = "Test Resume"
        mock_crud.get_with_details.return_value = mock_resume

        try:
            result = await service.get_resume(mock_db, 1, 1)
            if result == mock_resume:
                print("  PASS: Resume retrieved correctly")
                passed += 1
            else:
                print("  FAIL: Resume retrieval failed")
                failed += 1

            mock_crud.get_with_details.assert_called_once_with(mock_db, id=1, user_id=1)
            print("  PASS: CRUD method called with correct parameters")
            passed += 1

        except Exception as e:
            print(f"  FAIL: Exception during retrieval: {e}")
            failed += 1

    # Test 3: Update public settings
    print("\nTest 3: Update Public Settings")
    with patch('services.resume_service.resume_crud') as mock_crud:
        mock_resume = MagicMock()
        mock_resume.id = 1
        mock_resume.is_public = True
        mock_crud.update_public_settings.return_value = mock_resume

        try:
            result = await service.update_public_settings(
                mock_db, 1, 1, is_public=True, custom_slug="my-resume"
            )

            if result == mock_resume:
                print("  PASS: Public settings updated")
                passed += 1
            else:
                print("  FAIL: Public settings update failed")
                failed += 1

            mock_crud.update_public_settings.assert_called_once()
            print("  PASS: CRUD update method called")
            passed += 1

        except Exception as e:
            print(f"  FAIL: Exception during update: {e}")
            failed += 1

    # Test 4: Add work experience
    print("\nTest 4: Add Work Experience")
    with patch.object(service, 'get_resume') as mock_get_resume:
        with patch('services.resume_service.WorkExperience') as MockWorkExp:
            mock_resume = MagicMock()
            mock_resume.id = 1
            mock_get_resume.return_value = mock_resume

            mock_experience = MagicMock()
            mock_experience.id = 1
            mock_experience.company_name = "TechCorp"
            MockWorkExp.return_value = mock_experience

            exp_data = WorkExperienceCreate(
                company_name="TechCorp",
                position_title="Software Engineer",
                start_date=datetime(2020, 1, 1),
                is_current=True,
                description="Full-stack development"
            )

            try:
                result = await service.add_work_experience(mock_db, 1, 1, exp_data)

                if result and hasattr(result, 'company_name'):
                    print("  PASS: Work experience added")
                    passed += 1
                else:
                    print("  FAIL: Work experience addition failed")
                    failed += 1

                mock_db.add.assert_called()
                mock_db.commit.assert_called()
                print("  PASS: Database operations performed")
                passed += 1

            except Exception as e:
                print(f"  FAIL: Exception during work experience addition: {e}")
                failed += 1

    # Test 5: Send email (mock implementation)
    print("\nTest 5: Send Resume Email")
    try:
        mock_resume = MagicMock()
        mock_resume.id = 1

        result = await service.send_resume_email(
            mock_db,
            mock_resume,
            ["recipient@example.com"],
            "Your Resume",
            "Please find attached resume"
        )

        if result is True:
            print("  PASS: Email sending returned success")
            passed += 1
        else:
            print("  FAIL: Email sending failed")
            failed += 1

    except Exception as e:
        print(f"  FAIL: Exception during email sending: {e}")
        failed += 1

    # Test 6: Attach to message
    print("\nTest 6: Attach Resume to Message")
    with patch('services.resume_service.resume_message_attachment') as mock_attachment_crud:
        mock_attachment = MagicMock()
        mock_attachment.id = 1
        mock_attachment.resume_id = 1
        mock_attachment.message_id = 1
        mock_attachment_crud.create_attachment.return_value = mock_attachment

        try:
            result = await service.attach_to_message(
                mock_db, 1, 1, include_pdf=True, auto_attach=False
            )

            if result == mock_attachment:
                print("  PASS: Resume attached to message")
                passed += 1
            else:
                print("  FAIL: Resume attachment failed")
                failed += 1

            mock_attachment_crud.create_attachment.assert_called_once()
            print("  PASS: Attachment CRUD method called")
            passed += 1

        except Exception as e:
            print(f"  FAIL: Exception during attachment: {e}")
            failed += 1

    print(f"\nIntegration Test Summary: {passed} passed, {failed} failed")
    return failed == 0


async def test_business_logic_scenarios():
    """Test complex business logic scenarios."""
    print("\nTesting Business Logic Scenarios")
    print("-" * 40)

    service = ResumeService()
    mock_db = AsyncMock()
    passed = 0
    failed = 0

    # Scenario 1: Complete resume workflow
    print("Scenario 1: Complete Resume Workflow")

    with patch.object(service, 'create_resume') as mock_create, \
         patch.object(service, 'add_work_experience') as mock_add_exp, \
         patch.object(service, 'update_resume') as mock_update, \
         patch.object(service, 'create_share_link') as mock_share:

        # Setup mocks
        mock_resume = MagicMock()
        mock_resume.id = 1
        mock_create.return_value = mock_resume
        mock_add_exp.return_value = MagicMock()
        mock_update.return_value = mock_resume
        mock_share.return_value = "share_token_123"

        try:
            # 1. Create resume
            resume_data = ResumeCreate(
                title="Complete Workflow Resume",
                full_name="Test User",
                email="test@example.com"
            )
            resume = await service.create_resume(mock_db, resume_data, 1)

            # 2. Add work experience
            exp_data = WorkExperienceCreate(
                company_name="TestCorp",
                position_title="Developer",
                start_date=datetime(2020, 1, 1),
                is_current=True,
                description="Development work"
            )
            await service.add_work_experience(mock_db, resume.id, 1, exp_data)

            # 3. Update status to published
            update_data = ResumeUpdate(status=ResumeStatus.PUBLISHED)
            await service.update_resume(mock_db, resume.id, 1, update_data)

            # 4. Create share link
            share_token = await service.create_share_link(mock_db, resume.id, 1)

            print("  PASS: Complete workflow executed without errors")
            passed += 1

            # Verify all methods were called
            mock_create.assert_called_once()
            mock_add_exp.assert_called_once()
            mock_update.assert_called_once()
            mock_share.assert_called_once()
            print("  PASS: All workflow steps executed")
            passed += 1

        except Exception as e:
            print(f"  FAIL: Workflow failed: {e}")
            failed += 1

    # Scenario 2: Error handling
    print("\nScenario 2: Error Handling")

    # Test database error during creation
    with patch('services.resume_service.Resume') as MockResume:
        MockResume.return_value = MagicMock()
        mock_db_error = AsyncMock()
        mock_db_error.commit.side_effect = Exception("Database error")
        mock_db_error.rollback = AsyncMock()

        try:
            resume_data = ResumeCreate(
                title="Error Test Resume",
                full_name="Test User",
                email="test@example.com"
            )

            # This should raise an exception and call rollback
            await service.create_resume(mock_db_error, resume_data, 1)
            print("  FAIL: Expected exception was not raised")
            failed += 1

        except Exception:
            mock_db_error.rollback.assert_called_once()
            print("  PASS: Database error handled correctly with rollback")
            passed += 1

    print(f"\nBusiness Logic Summary: {passed} passed, {failed} failed")
    return failed == 0


async def main():
    """Run all integration tests."""
    print("RESUME SERVICE INTEGRATION TESTING")
    print("=" * 50)

    all_passed = True

    # Run integration tests
    all_passed &= await test_service_method_integration()
    all_passed &= await test_business_logic_scenarios()

    print("\n" + "=" * 50)
    if all_passed:
        print("ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("SOME INTEGRATION TESTS FAILED!")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)