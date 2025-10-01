● 1. Run all tests:
  cd backend
  PYTHONPATH=. python -m pytest app/tests/ -v

  2. Run tests with coverage:
  cd backend
  PYTHONPATH=. python -m pytest --cov=app --cov-report=term-missing app/tests/

  3. Run specific test file:
  cd backend
  PYTHONPATH=. python -m pytest app/tests/test_permission_matrix_user_management.py -v

  4. Run specific test function:
  cd backend
  PYTHONPATH=. python -m pytest app/tests/test_permission_matrix_user_management.py::TestUserManagementPermissionM    
  atrix::test_super_admin_can_create_users_any_company -v

  5. Run tests in parallel (faster):
  cd backend
  PYTHONPATH=. python -m pytest app/tests/ -n auto

  6. Run only the new permission matrix tests:
  cd backend
  PYTHONPATH=. python -m pytest app/tests/test_permission_matrix_*.py -v

  7. Run tests and stop on first failure:
  cd backend
  PYTHONPATH=. python -m pytest app/tests/ -x

  8. Run tests with detailed output:
  cd backend
  PYTHONPATH=. python -m pytest app/tests/ -v -s

  For your new permission matrix tests specifically:

  # Run all permission matrix tests
  cd backend && PYTHONPATH=. python -m pytest app/tests/test_permission_matrix_*.py -v