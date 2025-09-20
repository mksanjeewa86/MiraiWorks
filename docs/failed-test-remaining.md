app\tests\test_activation_comprehensive.py (trapped) error reading bcrypt version 
┌───────────────────── Traceback (most recent call last) ─────────────────────┐   
│ C:\Users\mksan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_ │   
│ qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\passlib\han │   
│ dlers\bcrypt.py:620 in _load_backend_mixin                                  │   
│                                                                             │   
│    617 │   │   except ImportError: # pragma: no cover                       │   
│    618 │   │   │   return False                                             │   
│    619 │   │   try:                                                         │   
│ >  620 │   │   │   version = _bcrypt.__about__.__version__                  │   
│    621 │   │   except:                                                      │   
│    622 │   │   │   log.warning("(trapped) error reading bcrypt version", ex │   
│    623 │   │   │   version = '<unknown>'                                    │   
│                                                                             │   
│ ┌───── locals ──────┐                                                       │   
│ │ dryrun = False    │                                                       │   
│ │   name = 'bcrypt' │                                                       │   
│ └───────────────────┘                                                       │   
└─────────────────────────────────────────────────────────────────────────────┘   
AttributeError: module 'bcrypt' has no attribute '__about__'

FAILED app/tests/test_candidate_workflows.py::test_candidate_application_workflow - assert 405 == 200
FAILED app/tests/test_candidate_workflows.py::test_candidate_pipeline_management - AttributeError: 'str' object has no attribute 'get'


FAILED app/tests/test_fixture_check.py::test_auth_headers_work - AssertionError: assert 'employer@example.com' == 'test@example.com'


FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_create_interview_success - assert 403 == 201
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_create_interview_validation_errors - assert False
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_get_interviews_success - pydantic_core._pydantic_core.ValidationError: 44 validation errors for Interv...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_get_single_interview_success - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_get_single_interview_not_found - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_update_interview_success - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_create_proposal_success - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_respond_to_proposal_accept - AttributeError: 'dict' object has no attribute 'id'    
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_cancel_interview_success - fastapi.exceptions.ResponseValidationError: 22 validation errors:
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_reschedule_interview_success - fastapi.exceptions.ResponseValidationError: 21 validation errors:
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_get_interview_stats_success - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_get_calendar_events_success - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_get_calendar_integration_status_success - AttributeError: <app.services.interview_service.InterviewService object at 0x...
FAILED app/tests/test_interviews_comprehensive.py::TestInterviewEndpoints::test_validation_edge_cases - pydantic_core._pydantic_core.ValidationError: 1 validation error for Intervie...


FAILED app/tests/test_notifications.py::TestNotifications::test_get_notifications_success - assert 0 == 2
FAILED app/tests/test_notifications.py::TestNotifications::test_get_notifications_with_limit - assert 0 == 3
FAILED app/tests/test_notifications.py::TestNotifications::test_get_notifications_unread_only - assert 0 == 1
FAILED app/tests/test_notifications.py::TestNotifications::test_get_unread_count_success - assert 0 == 1
FAILED app/tests/test_notifications.py::TestNotifications::test_mark_notifications_read_success - AssertionError: assert '2 notifications' in 'Marked 0 notifications as read'
FAILED app/tests/test_notifications.py::TestNotifications::test_mark_all_notifications_read_success - AssertionError: assert '3 notifications' in 'No unread notifications'
FAILED app/tests/test_notifications.py::TestNotifications::test_notifications_user_isolation - assert 0 == 1
FAILED app/tests/test_notifications.py::TestNotifications::test_notifications_ordering - assert 0 == 2
FAILED app/tests/test_notifications.py::TestNotifications::test_notifications_with_null_payload - assert 0 == 1
FAILED app/tests/test_notifications.py::TestNotifications::test_mark_read_with_duplicate_ids - AssertionError: assert '1 notifications' in 'Marked 0 notifications as read'
FAILED app/tests/test_notifications.py::TestNotifications::test_notification_read_timestamp - AssertionError: assert False is True


FAILED app/tests/test_recruitment_scenario.py::test_basic_recruitment_flow - assert 405 == 200
FAILED app/tests/test_recruitment_scenario.py::test_multi_job_workflow - TypeError: string indices must be integers, not 'str'
FAILED app/tests/test_recruitment_scenario.py::test_interview_management_workflow - assert 405 == 200


FAILED app/tests/test_recruitment_workflows.py::test_complete_recruitment_workflow - assert 400 == 201
FAILED app/tests/test_recruitment_workflows.py::test_multi_position_recruitment_workflow - AttributeError: 'str' object has no attribute 'get'
FAILED app/tests/test_recruitment_workflows.py::test_interview_workflow_scenarios - assert 405 == 200


FAILED app/tests/test_user_settings.py::TestUserSettings::test_get_user_settings_success - AssertionError: assert None == 'Software Engineer'
FAILED app/tests/test_user_settings.py::TestUserSettings::test_update_user_settings_sms_with_phone - assert 400 == 200
FAILED app/tests/test_user_settings.py::TestUserSettings::test_get_user_profile_success - AssertionError: assert 1 == 2
FAILED app/tests/test_user_settings.py::TestUserSettings::test_get_user_profile_without_settings - AssertionError: assert 1 == 2
FAILED app/tests/test_user_settings.py::TestUserSettings::test_update_user_profile_partial - AssertionError: assert 'employer@example.com' == 'test@example.com'    


