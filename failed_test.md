FAILED app/tests/test_auth.py::test_refresh_token_cycle - assert 401 == 200  
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_success - sqlalchemy.exc.ProgrammingError: (asyncmy.errors.ProgrammingError) (1146...
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_creates_admin_user - assert False is True
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_with_long_name - sqlalchemy.exc.DataError: (asyncmy.errors.DataError) (1406, "Data too lo...
FAILED app/tests/test_dashboard.py::TestDashboard::test_get_dashboard_stats_success - assert 0 >= 2
FAILED app/tests/test_files.py::TestFiles::test_file_download_permission_sender_access - fastapi.exceptions.HTTPException
FAILED app/tests/test_files.py::TestFiles::test_file_download_permission_check - fastapi.exceptions.HTTPException
FAILED app/tests/test_files.py::TestFiles::test_file_download_permission_between_different_users - fastapi.exceptions.HTTPException
FAILED app/tests/test_mbti_endpoints.py::TestMBTIEndpoints::test_start_mbti_test_success - assert 0 == 60
FAILED app/tests/test_mbti_endpoints.py::TestMBTIEndpoints::test_bulk_create_questions_success - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
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
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_super_admin_can_delete_companies - sqlalchemy.exc.ProgrammingError: (asyncmy.errors.ProgrammingError) (1146...
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_company_admin_can_view_own_company_only - assert 403 == 200
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_company_admin_can_update_own_company_only - assert 403 == 200
FAILED app/tests/test_permission_matrix_company_management.py::TestCompanyManagementPermissionMatrix::test_company_admin_can_view_own_admin_status - assert 403 == 200
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_super_admin_can_upload_files - AssertionError: assert 'file_path' in {'file_name': 'test.txt', 'file_si...
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_super_admin_can_download_any_file - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_super_admin_can_delete_any_file - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_can_upload_files - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_can_download_own_files - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_can_delete_own_files - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_cannot_download_other_users_files - KeyError: 'file_path'        
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_user_cannot_delete_other_users_files - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_company_admin_can_access_company_permitted_files - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_company_admin_cannot_access_other_company_files - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_cross_company_file_access_restrictions - KeyError: 'file_path'        
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_public_file_access_permissions - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_file_sharing_with_specific_users - KeyError: 'file_path'
FAILED app/tests/test_permission_matrix_file_access.py::TestFileAccessControl::test_unauthenticated_file_access - assert 405 == 401
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_create_interviews_any_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_view_any_interview - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...        
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_update_any_interview - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...      
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_cancel_any_interview - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...      
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_super_admin_can_delete_any_interview - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...      
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_can_create_interviews_own_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_cannot_create_interviews_other_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_can_view_company_interviews_only - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_company_admin_can_update_company_interviews_only - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_recruiter_can_create_interviews_own_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_recruiter_cannot_create_interviews_other_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_recruiter_can_manage_own_company_interviews - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_employer_can_create_interviews_own_company - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_employer_can_manage_own_company_interviews - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_cannot_create_interviews - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...        
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_can_view_own_interviews_only - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...    
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_can_update_own_interviews_only - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...  
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_can_cancel_own_interviews_only - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...  
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_cannot_delete_interviews - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...        
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_interview_proposals_company_scoping - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...       
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_interview_calendar_company_scoping - assert 422 == 200
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_interview_statistics_company_scoping - assert 422 == 200
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_candidate_cannot_view_interview_statistics - assert 422 == 403
FAILED app/tests/test_permission_matrix_interview_management.py::TestInterviewManagementPermissionMatrix::test_unauthenticated_interview_access - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_can_message_company_admins - assert 404 == 200      
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_cannot_message_recruiters - AssertionError: assert 'messaging restrictions' in 'super admin can only...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_cannot_message_employers - AssertionError: assert 'messaging restrictions' in 'super admin can only...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_super_admin_cannot_message_candidates - AssertionError: assert 'messaging restrictions' in 'super admin can only...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_can_message_super_admins - assert 404 == 200      
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_recruiters - AssertionError: assert 'messaging restrictions' in 'company admins can o...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_employers - AssertionError: assert 'messaging restrictions' in 'company admins can o...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_candidates - AssertionError: assert 'messaging restrictions' in 'company admins can o...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_company_admin_cannot_message_other_company_admins - AssertionError: assert 'messaging restrictions' in 'company admins can o...
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_recruiter_can_message_employers - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_recruiter_can_message_candidates - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_recruiter_can_message_other_recruiters - assert 404 == 200      
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_employer_can_message_recruiters - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_employer_can_message_candidates - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_can_message_recruiters - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_can_message_employers - assert 404 == 200
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_can_message_other_candidates - assert 404 == 200      
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_candidate_cannot_message_super_admins - assert 404 == 403       
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_cross_company_messaging_restrictions - assert 404 == 403        
FAILED app/tests/test_permission_matrix_messaging.py::TestMessagingPermissionMatrix::test_restricted_users_list_excludes_forbidden_recipients - ImportError: cannot import name 'UserRole' from 'app.models.user' (C:\Us...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_super_admin_can_view_all_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_super_admin_can_update_any_job - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_super_admin_can_delete_any_job - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_cannot_create_jobs_other_company - assert 201 == 403
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_can_update_own_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...   
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_cannot_update_other_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_can_delete_own_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...   
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_admin_cannot_delete_other_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_recruiter_cannot_create_jobs_other_company - AssertionError: assert 'other company' in 'can only create positions for...  
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_recruiter_can_update_own_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...       
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_recruiter_cannot_update_other_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...  
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_employer_cannot_create_jobs_other_company - AssertionError: assert 'other company' in 'can only create positions for...   
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_employer_can_update_own_company_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...        
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_create_jobs - assert 201 == 403
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_update_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_delete_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_can_view_public_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_candidate_cannot_view_draft_jobs - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_company_positions_access_restrictions - AssertionError: assert 'other company' in 'can only view positions for y...       
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_bulk_operations_company_scoping - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_position_management.py::TestPositionManagementPermissionMatrix::test_unauthenticated_position_access - sqlalchemy.exc.IntegrityError: (asyncmy.errors.IntegrityError) (1048, "C...
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_create_resume - assert 307 == 201
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_update_own_resume - AttributeError: type object 'Resume' has no attribute 'slug'
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_view_own_resumes - assert 307 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_cannot_view_other_candidate_resumes - assert 404 == 403 
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_cannot_update_other_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_cannot_delete_other_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_cannot_create_resumes - assert 307 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_cannot_create_resumes - assert 307 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_recruiter_cannot_create_resumes - assert 307 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_employer_cannot_create_resumes - assert 307 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_can_view_any_resume - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_cannot_update_candidate_resumes - assert 404 == 403   
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_super_admin_cannot_delete_candidate_resumes - assert 404 == 403   
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_can_view_applied_candidate_resumes_own_company - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_cannot_view_non_applied_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_company_admin_cannot_view_other_company_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_recruiter_can_view_applied_candidate_resumes_own_company - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_recruiter_cannot_view_non_applied_candidate_resumes - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_employer_can_view_applied_candidate_resumes_own_company - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_cross_company_resume_access_restrictions - assert 404 == 403      
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_create_share_link - AssertionError: assert 'share_url' in {'allow_download': True, 'created_...
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_non_owner_cannot_create_share_link - assert 404 == 403
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_candidate_can_generate_pdf - assert 404 == 200
FAILED app/tests/test_permission_matrix_resume_access.py::TestResumeAccessControl::test_unauthenticated_cannot_access_resumes - AssertionError: Failed for GET /api/resumes
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_all_authenticated_users_can_create_todos - KeyError: 'creator_id'
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_super_admin_can_assign_todos_to_anyone - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_company_admin_can_assign_todos_to_company_users_only - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_recruiter_can_assign_todos_to_company_users_only - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_employer_can_assign_todos_to_company_users_only - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_candidate_cannot_assign_todos_to_others - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_users_can_view_own_and_assigned_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_users_cannot_view_unrelated_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_super_admin_can_view_any_todo - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_owner_and_assignee_can_update_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_non_related_users_cannot_update_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_only_owner_can_delete_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_super_admin_can_delete_any_todo - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_assigned_user_can_complete_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_non_assigned_user_cannot_complete_todos - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_related_users_can_manage_attachments - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_assigned_user_can_request_extensions - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_non_assigned_user_cannot_request_extensions - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_todo_management.py::TestTodoManagementPermissionMatrix::test_unauthenticated_todo_access - TypeError: 'creator_id' is an invalid keyword argument for Todo
FAILED app/tests/test_permission_matrix_user_management.py::TestUserManagementPermissionMatrix::test_company_admin_can_view_own_company_users_only - assert 200 == 403
FAILED app/tests/test_permission_matrix_user_management.py::TestUserManagementPermissionMatrix::test_company_admin_bulk_operations_own_company_only - assert 200 == 403
FAILED app/tests/test_recruitment_basic.py::test_basic_recruitment_process - sqlalchemy.exc.ProgrammingError: (asyncmy.errors.ProgrammingError) (1146...  
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_create_recruitment_process_success - assert 401 == 201     
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_create_recruitment_process_unauthorized - assert 401 == 403
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_create_recruitment_process_invalid_data - assert 401 == 422
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_list_recruitment_processes_success - assert 401 == 200     
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_get_recruitment_process_success - assert 401 == 200        
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_get_recruitment_process_not_found - assert 401 == 404      
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_get_recruitment_process_access_denied - assert 401 == 403  
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_update_recruitment_process_success - assert 401 == 200     
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_update_active_process_requires_force - assert 401 == 409   
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_activate_recruitment_process_success - assert 401 == 200   
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_activate_recruitment_process_validation_failed - assert 401 == 422
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_force_activate_recruitment_process - assert 401 == 200     
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_archive_recruitment_process_success - assert 401 == 200    
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_clone_recruitment_process_success - assert 401 == 200      
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_delete_recruitment_process_success - assert 401 == 204     
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_delete_active_process_fails - assert 401 == 409
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_validate_recruitment_process - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_get_process_analytics - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_get_company_statistics - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_list_process_templates - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_apply_process_template - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_apply_nonexistent_template - assert 401 == 404
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_create_process_node_interview - assert 401 == 201
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestRecruitmentProcessEndpoints::test_create_process_node_with_todo_integration - assert 401 == 201
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_assign_candidate_to_process_success - assert 401 == 201      
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_assign_candidate_with_immediate_start - assert 401 == 201    
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_assign_duplicate_candidate_fails - assert 401 == 409
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_bulk_assign_candidates_success - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_bulk_assign_invalid_data - assert 401 == 422
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_list_process_candidates - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_get_candidate_process_success - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_candidate_can_view_own_process - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_candidate_cannot_view_other_process - assert 401 == 403      
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_start_candidate_process_success - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_start_already_started_process_fails - assert 401 == 409      
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_update_candidate_process_status_complete - assert 401 == 200 
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_update_candidate_process_status_fail - assert 401 == 200     
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_complete_without_final_result_fails - assert 401 == 422      
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_get_candidate_timeline - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_get_my_candidate_processes_as_candidate - assert 401 == 200  
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_get_my_candidate_processes_as_recruiter - assert 401 == 200  
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_get_recruiter_workload - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_recruiter_can_view_own_workload - assert 401 == 200
FAILED app/tests/test_recruitment_workflow_endpoints.py::TestCandidateProcessEndpoints::test_recruiter_cannot_view_other_workload - assert 401 == 403     
FAILED app/tests/test_recruitment_workflow_models.py::TestRecruitmentProcess::test_create_recruitment_process - AssertionError: assert None == 'draft'    
FAILED app/tests/test_recruitment_workflow_models.py::TestRecruitmentProcess::test_activate_process - ValueError: Only draft processes can be activated   
FAILED app/tests/test_recruitment_workflow_models.py::TestProcessNode::test_create_process_node - AssertionError: assert None == 'draft'
FAILED app/tests/test_recruitment_workflow_models.py::TestProcessNode::test_node_properties - AssertionError: assert not True
FAILED app/tests/test_recruitment_workflow_models.py::TestCandidateProcess::test_create_candidate_process - AssertionError: assert None == 'not_started'  
FAILED app/tests/test_recruitment_workflow_models.py::TestCandidateProcess::test_start_candidate_process - ValueError: Process has already been started   
FAILED app/tests/test_recruitment_workflow_models.py::TestNodeExecution::test_create_node_execution - AssertionError: assert None == 'pending'
FAILED app/tests/test_recruitment_workflow_scenarios.py::TestRecruitmentWorkflowScenarios::test_complete_recruitment_workflow_success_path - sqlalchemy.exc.ProgrammingError: (asyncmy.errors.ProgrammingError) (1146...
FAILED app/tests/test_todo_attachment_endpoints.py::TestTodoAttachmentEndpoints::test_get_attachment_stats - assert 422 == 200
FAILED app/tests/test_video_call_crud.py::TestVideoCallCRUD::test_concurrent_call_limit - KeyError: 'other_candidate'
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_schedule_video_call_success - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_schedule_video_call_invalid_candidate - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_get_video_call_not_found - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_list_video_calls_success - assert 401 == 200
FAILED app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_concurrent_calls_prevention - KeyError: 'other_candidate'
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
ERROR app/tests/test_positions.py::TestPositionEndpoints::test_get_statistics_forbidden
ERROR app/tests/test_positions.py::TestPositionEndpoints::test_delete_position_forbidden
ERROR app/tests/test_positions.py::TestPositionEndpoints::test_company_positions_permission_check
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
= 208 failed, 441 passed, 57 skipped, 74 warnings, 109 errors in 1891.96s (0:31:31) =