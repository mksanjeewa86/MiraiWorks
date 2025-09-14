FAILED app/tests/test_companies.py::TestCompanies::test_get_company_by_id_success - AttributeError: module 'app.crud.company' has no attribute 'get_with_counts'
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_success - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_success - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_get_company_admin_status - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_invalid_email - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_duplicate_email - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_invalid_data - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_get_company_not_found - AttributeError: module 'app.crud.company' has no attribute 'get_with_counts'
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_not_found - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_not_found - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_get_admin_status_not_found - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_success - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...
FAILED app/tests/test_companies.py::TestCompanies::test_delete_company_with_users_forbidden - AttributeError: module 'app.crud.company' has no attribute 'get'
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_creates_admin_user - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...        
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_with_long_name - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...
FAILED app/tests/test_companies.py::TestCompanies::test_update_company_to_duplicate_email - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...        
FAILED app/tests/test_companies.py::TestCompanies::test_create_company_all_valid_types - sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: companies...
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