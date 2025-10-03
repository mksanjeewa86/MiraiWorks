========================================================== short test summary info ==========================================================
FAILED app/tests/test_auth.py::test_refresh_token_cycle - assert 401 == 200
FAILED app/tests/test_candidate_workflows.py::test_admin_can_list_candidates - assert False
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_creates_admin_user - assert False is True
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_with_long_name - sqlalchemy.exc.DataError: (asyncmy.errors.DataError) (1406, "Data too long for column 'name' at row 1")
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_filter_by_search_name - assert False is True
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_filter_by_search_email - assert False is True
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_search_case_insensitive - assert False is True
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_filter_by_is_active_false - assert 0 >= 1
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_filter_by_is_demo_true - assert 0 >= 1
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_filter_by_multiple_types - assert 0 >= 1
FAILED app/tests/test_dashboard.py::TestDashboard::test_get_dashboard_stats_success - assert 0 >= 2
FAILED app/tests/test_files.py::TestFiles::test_file_download_permission_sender_access - fastapi.exceptions.HTTPException
FAILED app/tests/test_files.py::TestFiles::test_file_download_permission_check - fastapi.exceptions.HTTPException
FAILED app/tests/test_files.py::TestFiles::test_file_download_permission_between_different_users - fastapi.exceptions.HTTPException
FAILED app/tests/test_mbti_endpoints.py::TestMBTIEndpoints::test_start_mbti_test_success - assert 0 == 60
FAILED app/tests/test_mbti_scenario.py::TestMBTIScenarios::test_complete_mbti_test_workflow - assert 0 == 60
FAILED app/tests/test_messages.py::test_send_message_creates_record - assert 404 == 200
FAILED app/tests/test_messages.py::test_get_conversations_returns_latest - fastapi.exceptions.HTTPException
FAILED app/tests/test_messages.py::test_get_messages_with_user_returns_thread - fastapi.exceptions.HTTPException
FAILED app/tests/test_messages.py::test_mark_messages_as_read - fastapi.exceptions.HTTPException
FAILED app/tests/test_messages.py::test_search_messages_finds_matches - fastapi.exceptions.HTTPException
FAILED app/tests/test_notifications.py::test_unread_only_filter_returns_unread_notifications - AssertionError: assert 1 in []
FAILED app/tests/test_notifications.py::test_unread_count_endpoint - assert 0 == 1
FAILED app/tests/test_notifications.py::test_mark_notifications_read_endpoint - AssertionError: assert False is True
FAILED app/tests/test_notifications.py::test_mark_all_notifications_read_endpoint - AssertionError: assert (False)
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_company_admin_can_view_own_company_only - assert 403 == 200
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_company_admin_can_update_own_company_only - assert 403 == 200
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_company_admin_can_view_own_admin_status - assert 403 == 200
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_super_admin_can_download_any_file - assert 405 == 200
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_super_admin_can_delete_any_file - assert 500 == 200
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_can_download_own_files - sqlalchemy.exc.OperationalError: (asyncmy.errors.OperationalError) (1412, 'Table definition has changed, please retry transaction')
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_can_delete_own_files - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_cannot_download_other_users_files - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_cannot_delete_other_users_files - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_company_admin_can_access_company_permitted_files - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_company_admin_cannot_access_other_company_files - assert 405 == 403
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_cross_company_file_access_restrictions - assert 405 == 403
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_public_file_access_permissions - assert 405 in [200, 401, 403]
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_file_sharing_with_specific_users - assert 405 == 403
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_unauthenticated_file_access - assert 405 == 401
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_create_interviews_any_company - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_view_any_interview - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_update_any_interview - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_cancel_any_interview - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_delete_any_interview - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_can_create_interviews_own_company - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_cannot_create_interviews_other_company - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_can_view_company_interviews_only - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_can_update_company_interviews_only - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_recruiter_can_create_interviews_own_company - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_recruiter_cannot_create_interviews_other_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_recruiter_can_manage_own_company_interviews - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_employer_can_create_interviews_own_company - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_employer_can_manage_own_company_interviews - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_cannot_create_interviews - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_can_view_own_interviews_only - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_can_update_own_interviews_only - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_can_cancel_own_interviews_only - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_cannot_delete_interviews - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_interview_proposals_company_scoping - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_interview_calendar_company_scoping - sqlalchemy.exc.OperationalError: (asyncmy.errors.OperationalError) (1412, 'Table definition has changed, please retry transaction')
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_interview_statistics_company_scoping - assert 422 == 200
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_cannot_view_interview_statistics - assert 422 == 403
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_unauthenticated_interview_access - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_can_message_company_admins - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_cannot_message_recruiters - AssertionError: assert 'messaging restrictions' in 'super admin can only message company admins'
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_cannot_message_employers - AssertionError: assert 'messaging restrictions' in 'super admin can only message company admins'
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_cannot_message_candidates - AssertionError: assert 'messaging restrictions' in 'super admin can only message company admins'
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_can_message_super_admins - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_recruiters - AssertionError: assert 'messaging restrictions' in 'company admins can only message super admins'
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_employers - AssertionError: assert 'messaging restrictions' in 'company admins can only message super admins'
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_candidates - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_recruiter_can_message_employers - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_recruiter_can_message_candidates - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_recruiter_can_message_other_recruiters - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_employer_can_message_recruiters - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_employer_can_message_candidates - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_can_message_recruiters - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_can_message_employers - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_can_message_other_candidates - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_cannot_message_super_admins - assert 404 == 403
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_cross_company_messaging_restrictions - assert 404 == 403
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_restricted_users_list_excludes_forbidden_recipients - AssertionError: assert 'user_ids' in {'restricted_user_ids': []}
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_super_admin_can_view_all_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_super_admin_can_update_any_job - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_super_admin_can_delete_any_job - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_cannot_create_jobs_other_company - assert 201 == 403
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_can_update_own_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_cannot_update_other_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_can_delete_own_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_cannot_delete_other_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_recruiter_cannot_create_jobs_other_company - AssertionError: assert 'other company' in 'can only create positions for your own company'
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_recruiter_can_update_own_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_recruiter_cannot_update_other_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_employer_cannot_create_jobs_other_company - AssertionError: assert 'other company' in 'can only create positions for your own company'
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_employer_can_update_own_company_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_create_jobs - assert 201 == 403
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_update_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_delete_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_can_view_public_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_view_draft_jobs - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_positions_access_restrictions - AssertionError: assert 'other company' in 'can only view positions for your own company'
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_bulk_operations_company_scoping - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_unauthenticated_position_access - TypeError: 'password_hash' is an invalid keyword argument for User
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_create_resume - assert 500 == 201
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_update_own_resume - AttributeError: type object 'Resume' has no attribute 'slug'
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_view_own_resumes - assert 500 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_cannot_view_other_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_cannot_update_other_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_cannot_delete_other_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_cannot_create_resumes - assert 500 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_cannot_create_resumes - assert 500 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_recruiter_cannot_create_resumes - assert 500 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_employer_cannot_create_resumes - assert 500 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_can_view_any_resume - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_cannot_update_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_cannot_delete_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_can_view_applied_candidate_resumes_own_company - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_cannot_view_non_applied_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_cannot_view_other_company_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_recruiter_can_view_applied_candidate_resumes_own_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_employer_can_view_applied_candidate_resumes_own_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_cross_company_resume_access_restrictions - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_create_share_link - AssertionError: assert 'share_url' in {'allow_download': True, 'created_at': '2025-10-03T05:48:58.609670', 'expires_at': None, 'last_vie...
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_non_owner_cannot_create_share_link - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_generate_pdf - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_unauthenticated_cannot_access_resumes - AssertionError: Failed for GET /api/resumes/1/pdf
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_super_admin_can_assign_todos_to_anyone - assert 404 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_company_admin_can_assign_todos_to_company_users_only - assert 400 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_recruiter_can_assign_todos_to_company_users_only - assert 400 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_employer_can_assign_todos_to_company_users_only - assert 400 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_candidate_cannot_assign_todos_to_others - assert 400 == 403
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_users_can_view_own_and_assigned_todos - assert 405 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_users_cannot_view_unrelated_todos - assert 405 == 403
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_super_admin_can_view_any_todo - assert 405 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_owner_and_assignee_can_update_todos - assert 405 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_non_related_users_cannot_update_todos - assert 405 == 403
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_only_owner_can_delete_todos - assert 404 == 403
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_super_admin_can_delete_any_todo - assert 404 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_assigned_user_can_complete_todos - assert 404 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_non_assigned_user_cannot_complete_todos - assert 404 == 403
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_related_users_can_manage_attachments - assert 403 == 200
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_assigned_user_can_request_extensions - assert 404 == 201
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_non_assigned_user_cannot_request_extensions - assert 404 == 403
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_unauthenticated_todo_access - AssertionError: Failed for GET /api/todos/1
FAILED app/tests/test_permission_matrix_user_management.py::TestUserManagementPermissionMatrix::test_company_admin_can_view_own_company_users_only - assert 200 == 403
FAILED app/tests/test_permission_matrix_user_management.py::TestUserManagementPermissionMatrix::test_company_admin_bulk_operations_own_company_only - assert 200 == 403
FAILED app/tests/test_recruitment_workflow_models.py::TestRecruitmentProcess::test_create_recruitment_process - AssertionError: assert None == 'draft'
FAILED app/tests/test_recruitment_workflow_models.py::TestRecruitmentProcess::test_activate_process - ValueError: Only draft processes can be activated
FAILED app/tests/test_recruitment_workflow_models.py::TestProcessNode::test_create_process_node - AssertionError: assert None == 'draft'
FAILED app/tests/test_recruitment_workflow_models.py::TestProcessNode::test_node_properties - AssertionError: assert not True
FAILED app/tests/test_recruitment_workflow_models.py::TestCandidateProcess::test_create_candidate_process - AssertionError: assert None == 'not_started'
FAILED app/tests/test_recruitment_workflow_models.py::TestCandidateProcess::test_start_candidate_process - ValueError: Process has already been started
FAILED app/tests/test_recruitment_workflow_models.py::TestNodeExecution::test_create_node_execution - AssertionError: assert None == 'pending'
FAILED app/tests/test_recruitment_workflow_scenarios.py::TestRecruitmentWorkflowScenarios::test_complete_recruitment_workflow_success_path - assert 422 == 200
FAILED app/tests/test_todo_attachment_endpoints.py::TestTodoAttachmentEndpoints::test_get_attachment_stats - assert 422 == 200
FAILED app/tests/test_todos.py::test_todo_crud_flow - assert False
FAILED app/tests/test_todos.py::test_overdue_todos_mark_expired - assert False
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_filter_by_is_suspended_true - assert 0 >= 1
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_search_by_first_name - assert False is True
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_search_by_last_name - assert False is True
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_search_by_email - assert False is True
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_search_case_insensitive - assert False is True
FAILED app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_concurrent_call_limit - KeyError: 'other_candidate'
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_schedule_video_call_invalid_candidate - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_video_call_not_found - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_list_video_calls_success - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_concurrent_calls_prevention - KeyError: 'other_candidate'
FAILED app/tests/test_workflow_relationships.py::TestWorkflowRelationships::test_cascading_soft_delete - NameError: name 'db' is not defined
FAILED app/tests/test_workflow_relationships.py::TestWorkflowRelationships::test_soft_delete_only_affects_related_records - NameError: name 'db' is not defined
ERROR test_workflow_db_simple.py::test_database_connection
ERROR test_workflow_working.py::test_workflow_relationships_working
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_company_admin_cannot_access_other_company_users
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_company_admin_cannot_create_users_in_other_companies
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_recruiter_cannot_access_other_company_positions
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_employer_cannot_access_other_company_interviews
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_messaging_restrictions
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_file_access_prevention
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_resume_access_prevention
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_todo_assignment_prevention
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_recruitment_process_isolation
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_candidate_process_isolation
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_bulk_operations_prevention
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_search_isolation
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_statistics_isolation
ERROR app/tests/test_permission_matrix_cross_company.py::TestCrossCompanyAccessPrevention::test_cross_company_export_isolation
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_expired_token_access_denied
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_malformed_token_access_denied
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_inactive_user_access_denied
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_unverified_user_access_restrictions
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_role_change_permission_update
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_company_deactivation_access_denied
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_concurrent_permission_checks
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_permission_boundary_at_resource_limits
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_cross_functional_permission_validation
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_permission_inheritance_edge_cases
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_nested_resource_permission_validation
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_api_rate_limiting_permission_interaction
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_session_invalidation_edge_cases
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_permission_matrix_boundary_transitions
ERROR app/tests/test_permission_matrix_edge_cases.py::TestPermissionMatrixEdgeCases::test_permission_matrix_data_consistency
ERROR app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_other_company_admins - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1062, "Duplicate entry 'super_admin' for key 'roles.ix_roles_name'")
ERROR app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_recruiter_cannot_view_non_applied_candidate_resumes - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1062, "Duplicate entry 'super_admin' for key 'roles.ix_roles_name'")
ERROR app/tests/test_positions.py::TestPositionEndpoints::test_get_statistics_forbidden
ERROR app/tests/test_positions.py::TestPositionEndpoints::test_delete_position_forbidden
ERROR app/tests/test_positions.py::TestPositionEndpoints::test_company_positions_permission_check
ERROR app/tests/test_recruitment_scenario.py::test_admin_updates_job_status - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
ERROR app/tests/test_recruitment_scenario.py::test_interview_created_for_job_candidate - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
ERROR app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_create_recruitment_process_success - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_create_resume_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_get_resume_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_update_resume_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_delete_resume_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_add_work_experience_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_duplicate_resume_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_get_resume_unauthorized
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_update_resume_not_found
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_delete_resume_not_found
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_add_work_experience_invalid_resume
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_resume_status_transitions
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_resume_visibility_settings
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_japanese_resume_format
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_create_share_link_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_get_shared_resume_success
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_public_resume_access
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_resume_with_empty_sections
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_resume_with_maximum_data
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_bulk_resume_operations
ERROR app/tests/test_resume_comprehensive.py::TestResumeComprehensive::test_resume_with_all_sections
ERROR app/tests/test_resume_comprehensive.py::TestResumeEndpoints::test_create_resume_endpoint
ERROR app/tests/test_resume_comprehensive.py::TestResumeEndpoints::test_get_resume_endpoint
ERROR app/tests/test_resume_comprehensive.py::TestResumeEndpoints::test_update_resume_endpoint
ERROR app/tests/test_resume_comprehensive.py::TestResumeEndpoints::test_delete_resume_endpoint
ERROR app/tests/test_resume_comprehensive.py::TestResumeIntegrationScenarios::test_complete_resume_lifecycle
ERROR app/tests/test_resume_comprehensive.py::TestResumeIntegrationScenarios::test_multi_user_resume_isolation
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsAuthentication::test_update_resume_unauthorized
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsAuthentication::test_delete_resume_unauthorized
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsValidAuthentication::test_get_resumes_success
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsValidAuthentication::test_create_resume_success
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsValidAuthentication::test_get_resume_by_id_success
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsValidAuthentication::test_update_resume_success
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestResumeEndpointsValidAuthentication::test_delete_resume_success
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestEnumValidation::test_valid_status_values
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestEnumValidation::test_invalid_status_values
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestEnumValidation::test_valid_visibility_values
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestEnumValidation::test_invalid_visibility_values
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestEnumValidation::test_valid_format_values
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestEnumValidation::test_valid_language_values
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestStatusTransitions::test_draft_to_published
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestStatusTransitions::test_published_to_archived
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestVisibilityAndPublicAccess::test_toggle_public_visibility
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestVisibilityAndPublicAccess::test_update_public_settings
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestErrorHandling::test_get_nonexistent_resume
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestErrorHandling::test_update_nonexistent_resume
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestErrorHandling::test_delete_nonexistent_resume
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestErrorHandling::test_create_resume_missing_required_fields
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestErrorHandling::test_create_resume_invalid_data_types
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestPagination::test_resumes_pagination
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestPagination::test_resumes_filtering
ERROR app/tests/test_resumes_endpoints_comprehensive.py::TestConcurrency::test_concurrent_resume_updates
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_get_video_call_by_room_id
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_get_video_call_by_interview_id
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_get_user_video_calls
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_update_call_status
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_add_participant
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_update_participant_left
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_save_recording_consent
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_save_recording_consent_update
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_get_call_consents
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_save_transcription_segment
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_get_call_transcription
ERROR app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_update_transcription_status
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_schedule_video_call_success - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails ...
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_video_call_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_video_call_forbidden
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_join_video_call_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_join_video_call_invalid_participant
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_end_video_call_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_end_video_call_only_interviewer
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_record_consent_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_record_consent_decline
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_video_token_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_save_transcript_segment_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_save_transcript_segment_call_not_active
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_transcript_success
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_transcript_not_available
ERROR app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_download_transcript_success
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_admin_create_workflow_with_interviews_todos_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_employer_create_workflow_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_recruiter_cannot_create_workflow_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_recruiter_create_interview_with_workflow_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_candidate_cannot_create_content_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_filter_interviews_by_workflow_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_filter_todos_by_workflow_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_soft_delete_workflow_cascades_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_unauthorized_access_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIPermissions::test_invalid_workflow_id_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIEdgeCases::test_create_workflow_with_invalid_company_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIEdgeCases::test_update_workflow_remove_relationships_api
ERROR app/tests/test_workflow_api_permissions.py::TestWorkflowAPIEdgeCases::test_concurrent_workflow_operations_api
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCreationPermissions::test_admin_can_create_workflow_with_interviews_and_todos
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCreationPermissions::test_employer_can_create_workflow_in_own_company
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCreationPermissions::test_recruiter_cannot_create_workflow_but_can_create_interviews_todos
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCreationPermissions::test_candidate_cannot_create_workflow_interviews_todos
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCreationPermissions::test_cross_company_workflow_access_restrictions
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCascadingOperationsWithPermissions::test_admin_soft_delete_workflow_cascades_all
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowCascadingOperationsWithPermissions::test_workflow_with_scheduled_interviews_cascade_behavior
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowEdgeCasesAndErrorHandling::test_create_interview_with_invalid_workflow_id
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowEdgeCasesAndErrorHandling::test_create_todo_with_invalid_workflow_id
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowEdgeCasesAndErrorHandling::test_soft_delete_nonexistent_workflow
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowEdgeCasesAndErrorHandling::test_workflow_with_mixed_company_relationships
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowPermissionMatrix::test_permission_matrix[admin-True-True-True]
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowPermissionMatrix::test_permission_matrix[employer-True-True-True]
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowPermissionMatrix::test_permission_matrix[recruiter-False-True-True]
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowPermissionMatrix::test_permission_matrix[candidate-False-False-False]
ERROR app/tests/test_workflow_permissions_comprehensive.py::TestWorkflowPermissionMatrix::test_bulk_operations_with_permissions
============================ 170 failed, 457 passed, 58 skipped, 2328 warnings, 146 errors in 518.37s (0:08:38) =============================