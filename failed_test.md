FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_include_deleted_true - assert 0 >= 1
FAILED app/tests/test_dashboard.py::TestDashboard::test_get_dashboard_stats_success - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: ...     
FAILED app/tests/test_dashboard.py::TestDashboard::test_get_recent_activity_success - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: ...     
FAILED app/tests/test_dashboard.py::TestDashboard::test_get_recent_activity_interview_metadata - AttributeError: 'Interview' object has no attribute 'scheduled_at'
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_conversations_success - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_conversations_with_search - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_conversations_unauthorized - assert 404 == 401
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_messages_with_user_success - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_messages_with_pagination - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_messages_unauthorized - assert 404 == 401
ead_success - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_mark_conversation_as_read_unauthorized - assert 404 == 401
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_message_participants_success - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_message_participants_with_query - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_message_participants_with_limit - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_get_message_participants_unauthorized - assert 404 == 401
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_message_with_reply_to - assert 404 == 200
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_message_validation_empty_content - assert 404 == 422
FAILED app/tests/test_direct_messages.py::TestDirectMessages::test_search_messages_pagination - assert 404 == 200
FAILED app/tests/test_files.py::TestFiles::test_upload_file_success - AssertionError: assert 1024 == 17
FAILED app/tests/test_files.py::TestFiles::test_upload_file_no_filename - assert 422 == 400
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_include_deleted_true - assert 0 >= 1
ERROR app/tests/test_direct_messages.py::TestDirectMessages::test_send_message_role_permission_forbidden - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: ro...
