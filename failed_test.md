FAILED app/tests/test_auth.py::test_login_inactive_user - AssertionError: assert 'Account is deactivated' in 'Invalid email or password'
FAILED app/tests/test_auth.py::test_logout - assert 403 == 200
FAILED app/tests/test_auth.py::test_password_reset_request - sqlalchemy.exc.ArgumentError: Join target, typically a FROM expression, or ORM relationship attribute expected, go...
FAILED app/tests/test_auth.py::test_unauthorized_access - assert 403 == 401
FAILED app/tests/test_auth.py::test_admin_requires_2fa - assert False is True
FAILED app/tests/test_auth.py::test_super_admin_requires_2fa - AssertionError: assert {'company_id': None, 'email': 'superadmin@example.com', 'first_name': 'Super', 'full_name':...
FAILED app/tests/test_auth.py::test_login_with_role_eager_loading - assert False is True
FAILED app/tests/test_auth.py::test_logout_unauthenticated - assert 403 == 401
FAILED app/tests/test_auth.py::test_password_reset_request_with_email_service_failure - sqlalchemy.exc.ArgumentError: Join target, typically a FROM expression, or ORM relationship attribute expected, go...
FAILED app/tests/test_auth_service_only.py::TestAuthService::test_decode_token_success - assert None is not None       
FAILED app/tests/test_auth_service_only.py::TestAuthService::test_token_contains_expected_claims - TypeError: 'NoneType' object is not subscriptable
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_success - assert 403 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_with_pagination - assert 404 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_with_filters - assert 404 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_get_company_by_id_success - assert 404 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_success - assert 403 == 201
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_success - assert 404 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_get_company_admin_status - assert 404 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_unauthorized - assert 403 == 401
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_unauthorized - assert 403 == 401
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_unauthorized - assert 404 == 401
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_unauthorized - assert 404 == 401
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_forbidden_non_super_admin - assert 404 == 403   
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_invalid_email - assert 403 == 422
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_missing_required_fields - assert 403 == 422     
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_duplicate_email - assert 403 == 400
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_invalid_type - assert 403 == 422
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_invalid_data - assert 404 == 422
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_invalid_pagination - assert 404 == 422
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_success - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies.phone
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_with_users_forbidden - assert 404 in [400, 403] 
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_with_long_name - assert 403 in [201, 422]
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_to_duplicate_email - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies.phone
FAILED app/tests/test_companies.py::TestCompanies::test_get_companies_with_complex_search - assert 404 == 200
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_all_valid_types - assert 403 == 201
FAILED app/tests/test_fixture_check.py::test_fixtures_work - assert 403 == 401
FAILED app/tests/test_services.py::TestAuthService::test_decode_token_success - assert None is not None
FAILED app/tests/test_services.py::TestServiceConfiguration::test_services_have_required_methods - AssertionError: assert False
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_success - AttributeError: module 'app.crud.user' has no attribute 'get_users_paginated'
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_with_pagination - assert 404 == 200     
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_with_search - assert 404 == 200
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_success - assert 200 == 201
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_user_by_id_success - assert 404 == 200        
FAILED app/tests/test_users_management.py::TestUsersManagement::test_update_user_success - assert 404 == 200
FAILED app/tests/test_users_management.py::TestUsersManagement::test_suspend_user_success - assert 404 == 200
FAILED app/tests/test_users_management.py::TestUsersManagement::test_unsuspend_user_success - assert 404 == 200        
FAILED app/tests/test_users_management.py::TestUsersManagement::test_reset_password_success - assert 404 == 200        
FAILED app/tests/test_users_management.py::TestUsersManagement::test_resend_activation_success - assert 404 == 200     
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_unauthorized - assert 403 == 401        
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_unauthorized - assert 403 == 401      
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_forbidden_regular_user - assert 422 == 403
FAILED app/tests/test_users_management.py::TestUsersManagement::test_delete_user_unauthorized - assert 404 == 401      
FAILED app/tests/test_users_management.py::TestUsersManagement::test_suspend_user_unauthorized - assert 404 == 401     
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_invalid_email - assert 200 == 422     
FAILED app/tests/test_users_management.py::TestUsersManagement::test_update_user_invalid_data - assert 404 == 422      
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_invalid_pagination - assert 404 == 422  
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_suspend_success - assert 404 == 200
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_unsuspend_success - assert 404 == 200        
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_reset_password_success - assert 404 == 200   
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_delete_success - assert 404 == 200
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_operations_unauthorized - assert 404 == 401  
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_operations_empty_user_ids - assert 404 == 422
FAILED app/tests/test_users_management.py::TestUsersManagement::test_delete_self_forbidden - assert 404 in [403, 400]  
FAILED app/tests/test_users_management.py::TestUsersManagement::test_suspend_self_forbidden - assert 404 in [403, 400] 
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_with_nonexistent_company - assert 403 == 400
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_with_all_filters - assert 404 == 200    
ERROR app/tests/test_services.py::TestMeetingService::test_generate_meeting_id - TypeError: MeetingService.__init__() missing 1 required positional argument: 'db'
ERROR app/tests/test_services.py::TestMeetingService::test_validate_meeting_time_valid - TypeError: MeetingService.__init__() missing 1 required positional argument: 'db'
ERROR app/tests/test_services.py::TestMeetingService::test_validate_meeting_time_past - TypeError: MeetingService.__init__() missing 1 required positional argument: 'db'
ERROR app/tests/test_services.py::TestMeetingService::test_calculate_meeting_duration - TypeError: MeetingService.__init__() missing 1 required positional argument: 'db'
ERROR app/tests/test_services.py::TestMeetingService::test_log_meeting_event - TypeError: MeetingService.__init__() missing 1 required positional argument: 'db'