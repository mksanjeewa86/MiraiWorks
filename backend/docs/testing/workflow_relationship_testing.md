# Workflow Relationship Testing Documentation

## Overview

This document describes the comprehensive test suite for workflow relationships between recruitment processes, interviews, and todos, including permission-based access control.

## Test Structure

### 📁 Test Files

1. **`test_workflow_permissions_comprehensive.py`** - Core permission and relationship tests
2. **`test_workflow_api_permissions.py`** - API endpoint permission tests  
3. **`test_workflow_relationships.py`** - Basic relationship functionality tests
4. **`scripts/run_workflow_tests.py`** - Test runner with coverage
5. **`scripts/verify_workflow_schema.py`** - Database schema verification
6. **`scripts/test_schemas_only.py`** - Schema validation tests

## Test Coverage

### 🎯 Core Functionality Tests

#### Workflow Creation with Relationships
- ✅ Admin creates workflow with interviews and todos
- ✅ Employer creates company workflows
- ✅ Recruiter creates interviews/todos for existing workflows
- ✅ Cross-company workflow restrictions

#### Permission Matrix Testing
```python
@pytest.mark.parametrize("user_type,can_create_workflow,can_create_interview,can_create_todo", [
    ("admin", True, True, True),
    ("employer", True, True, True), 
    ("recruiter", False, True, True),
    ("candidate", False, False, False),
])
```

#### Cascading Operations
- ✅ Soft delete workflow cascades to interviews and todos
- ✅ Preserves data integrity during cascade
- ✅ Only affects related records
- ✅ Works with mixed creators

### 🔐 Permission-Based Tests

#### User Roles and Permissions
```python
# Admin Role
permissions = [
    "workflow:create", "workflow:read", "workflow:update", "workflow:delete",
    "interview:create", "interview:read", "interview:update", "interview:delete", 
    "todo:create", "todo:read", "todo:update", "todo:delete",
    "user:manage", "company:manage"
]

# Employer Role  
permissions = [
    "workflow:create", "workflow:read", "workflow:update",
    "interview:create", "interview:read", "interview:update",
    "todo:create", "todo:read", "todo:update",
    "candidate:review"
]

# Recruiter Role
permissions = [
    "workflow:read",
    "interview:create", "interview:read", "interview:update", 
    "todo:create", "todo:read", "todo:update",
    "candidate:manage"
]

# Candidate Role
permissions = [
    "interview:read",
    "todo:read", 
    "profile:update"
]
```

### 🌐 API Endpoint Tests

#### Workflow Operations
- `POST /api/recruitment-workflows/` - Create workflow
- `GET /api/recruitment-workflows/` - List workflows
- `GET /api/recruitment-workflows/{id}` - Get workflow
- `PUT /api/recruitment-workflows/{id}` - Update workflow
- `DELETE /api/recruitment-workflows/{id}` - Soft delete workflow

#### Interview Operations with Workflow Links
- `POST /api/interviews/` with `workflow_id`
- `GET /api/interviews/?workflow_id={id}` - Filter by workflow
- `PUT /api/interviews/{id}` - Update workflow relationship

#### Todo Operations with Workflow Links  
- `POST /api/todos/` with `workflow_id`
- `GET /api/todos/?workflow_id={id}` - Filter by workflow
- `PUT /api/todos/{id}` - Update workflow relationship

### 🧪 Edge Cases and Error Handling

#### Invalid Data Handling
- ✅ Non-existent workflow_id in interviews/todos
- ✅ Non-existent company_id in workflows
- ✅ Cross-company access attempts
- ✅ Unauthorized access attempts
- ✅ Invalid permission combinations

#### Concurrency and Bulk Operations
- ✅ Concurrent workflow creation
- ✅ Bulk interview/todo creation
- ✅ Bulk soft delete operations
- ✅ Race condition handling

## Test Fixtures

### User Fixtures
```python
@pytest.fixture
async def admin_user(db: AsyncSession, admin_role: Role) -> User:
    """Admin user with full permissions"""

@pytest.fixture  
async def employer_user(db: AsyncSession, employer_role: Role) -> User:
    """Employer user with hiring permissions"""

@pytest.fixture
async def recruiter_user(db: AsyncSession, recruiter_role: Role) -> User:
    """Recruiter user with limited permissions"""

@pytest.fixture
async def candidate_user(db: AsyncSession, candidate_role: Role) -> User:
    """Candidate user with minimal permissions"""
```

### Company Fixtures
```python
@pytest.fixture
async def test_company(db: AsyncSession) -> Company:
    """Primary test company"""

@pytest.fixture  
async def second_company(db: AsyncSession) -> Company:
    """Secondary company for cross-company tests"""
```

## Running Tests

### Quick Test Run
```bash
# Run basic schema verification
python3 scripts/verify_workflow_schema.py

# Run schema validation tests
python3 scripts/test_schemas_only.py

# Run specific test file
python3 -m pytest app/tests/test_workflow_permissions_comprehensive.py -v
```

### Comprehensive Test Suite
```bash
# Run all workflow tests with coverage
python3 scripts/run_workflow_tests.py

# Run with detailed output
python3 -m pytest app/tests/ -k 'workflow' -v --tb=long

# Run with coverage report
python3 -m pytest app/tests/test_workflow_*.py --cov=app --cov-report=html
```

### Database Setup for Testing
```bash
# Ensure test database exists
mysql -u hrms -phrms -e "CREATE DATABASE IF NOT EXISTS miraiworks_test;"

# Run with test database
ENVIRONMENT=test python3 -m pytest app/tests/test_workflow_*.py
```

## Test Scenarios

### 1. Admin Full Access Scenario
```python
async def test_admin_can_create_workflow_with_interviews_and_todos():
    # Admin creates workflow
    workflow = await recruitment_process.create(db, workflow_data, created_by=admin_user.id)
    
    # Admin creates interviews linked to workflow
    interview = Interview(workflow_id=workflow.id, ...)
    
    # Admin creates todos linked to workflow  
    todo = Todo(workflow_id=workflow.id, ...)
    
    # Verify relationships exist
    assert interview.workflow_id == workflow.id
    assert todo.workflow_id == workflow.id
```

### 2. Recruiter Limited Access Scenario
```python
async def test_recruiter_cannot_create_workflow_but_can_create_interviews_todos():
    # Employer creates workflow first
    workflow = await recruitment_process.create(db, workflow_data, created_by=employer_user.id)
    
    # Recruiter can create interview for existing workflow
    interview = Interview(workflow_id=workflow.id, created_by=recruiter_user.id, ...)
    
    # Recruiter can create todo for existing workflow
    todo = Todo(workflow_id=workflow.id, created_by=recruiter_user.id, ...)
    
    # Verify recruiter cannot create new workflows (API level)
```

### 3. Cascading Soft Delete Scenario
```python
async def test_cascading_soft_delete():
    # Create workflow with interviews and todos
    workflow = create_workflow()
    interviews = create_interviews(workflow_id=workflow.id)
    todos = create_todos(workflow_id=workflow.id)
    
    # Soft delete workflow
    await recruitment_process.soft_delete(db, id=workflow.id)
    
    # Verify cascade
    assert workflow.is_deleted == True
    assert all(interview.is_deleted == True for interview in interviews)
    assert all(todo.is_deleted == True for todo in todos)
```

### 4. Permission Validation Scenario
```python
async def test_candidate_cannot_create_content_api():
    # Candidate attempts to create workflow
    response = await client.post("/api/recruitment-workflows/", ...)
    assert response.status_code == 403  # Forbidden
    
    # Candidate attempts to create interview
    response = await client.post("/api/interviews/", ...)
    assert response.status_code == 403  # Forbidden
    
    # Candidate attempts to create todo
    response = await client.post("/api/todos/", ...)
    assert response.status_code == 403  # Forbidden
```

## Expected Test Results

### Database Schema Tests
- ✅ `workflow_id` columns exist in interviews and todos tables
- ✅ Foreign key constraints properly configured
- ✅ Indexes created for performance
- ✅ Migration version is correct

### Model Relationship Tests
- ✅ SQLAlchemy relationships properly defined
- ✅ Cascading soft delete functionality works
- ✅ Data integrity maintained during operations

### Schema Validation Tests
- ✅ Pydantic schemas accept `workflow_id` parameter
- ✅ `workflow_id` is optional in all schemas  
- ✅ Validation works for create/update operations

### Permission Tests
- ✅ Each user role has appropriate access levels
- ✅ API endpoints enforce permission requirements
- ✅ Cross-company access is properly restricted

### API Integration Tests
- ✅ CRUD operations work through API endpoints
- ✅ Filtering by `workflow_id` functions correctly
- ✅ Error handling returns appropriate status codes

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Ensure MySQL is running
brew services start mysql@8.4

# Check database exists
mysql -u hrms -phrms -e "SHOW DATABASES;"
```

#### Permission Denied Errors
```bash
# Ensure proper environment setup
export ENVIRONMENT=test
export PYTHONPATH=.
```

#### Import Errors
```bash
# Check all model imports are available
python3 -c "from app.models import recruitment_process, interview, todo"
```

### Test Data Cleanup
Tests use pytest fixtures with automatic cleanup, but manual cleanup can be done:
```sql
-- Clean test data
DELETE FROM interviews WHERE title LIKE '%Test%';
DELETE FROM todos WHERE title LIKE '%Test%'; 
DELETE FROM recruitment_processes WHERE name LIKE '%Test%';
```

## Continuous Integration

### GitHub Actions Integration
```yaml
# .github/workflows/test-workflows.yml
name: Workflow Relationship Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.4
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: miraiworks_test
        ports:
          - 3306:3306
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run workflow tests
        run: python3 scripts/run_workflow_tests.py
```

## Coverage Goals

- **Database Operations**: 100% coverage of CRUD operations
- **API Endpoints**: 100% coverage of workflow-related endpoints  
- **Permission Matrix**: 100% coverage of all user role combinations
- **Edge Cases**: 90% coverage of error scenarios
- **Integration**: 95% coverage of end-to-end workflows

## Maintenance

### Adding New Tests
1. Add test methods to appropriate test class
2. Update permission matrix if new roles added
3. Add API endpoint tests if new endpoints created
4. Update documentation with new test scenarios

### Updating Permissions
1. Update role fixtures with new permissions
2. Update permission matrix test parameters
3. Add specific tests for new permission combinations
4. Verify API endpoints enforce new permissions

---

This comprehensive test suite ensures that the workflow relationship feature is robust, secure, and functions correctly across all user roles and scenarios.