FAILED app/tests/test_services.py::TestServiceConfiguration::test_services_have_required_methods - AssertionError: assert False
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_with_pagination - KeyError: 'size'
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_forbidden_regular_user - assert 422 == 403
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_invalid_email - assert 201 == 422
FAILED app/tests/test_users_management.py::TestUsersManagement::test_update_user_invalid_data - assert 200 == 422
FAILED app/tests/test_users_management.py::TestUsersManagement::test_bulk_operations_empty_user_ids - assert 400 == 422
FAILED app/tests/test_users_management.py::TestUsersManagement::test_create_user_with_nonexistent_company - assert 403 == 400
FAILED app/tests/test_users_management.py::TestUsersManagement::test_get_users_with_all_filters - KeyError: 'size'
ERROR scripts/test_local.py::test_fixture_imports