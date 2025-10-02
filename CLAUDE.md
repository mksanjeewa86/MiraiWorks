# MiraiWorks Development Guidelines

## Project Architecture Rules

This document defines the **STRICT** architectural rules that must be followed in all future development. These rules ensure code maintainability, separation of concerns, and consistent project structure.

---

## 🏗️ **Core Architecture Pattern**

```
📁 backend/app/
├── 📁 models/          # SQLAlchemy database models ONLY
├── 📁 schemas/         # Pydantic schemas + enums
├── 📁 crud/           # Database operations
├── 📁 endpoints/      # HTTP routing logic ONLY
├── 📁 services/       # Business logic
└── 📁 utils/          # Shared utilities
```

---

## 📋 **STRICT RULES BY LAYER**

### 🔵 **1. MODELS (`app/models/`)**
**Purpose**: Database schema definition ONLY

#### ✅ **ALLOWED**:
- SQLAlchemy table definitions
- Database relationships
- Database constraints and indexes
- Simple computed properties using existing fields
- Basic validation at database level

#### ❌ **FORBIDDEN**:
- **Pydantic schemas** → Move to `app/schemas/`
- **Enums** → Move to `app/schemas/`
- **Business logic** → Move to `app/services/`
- **Database queries** → Move to `app/crud/`
- **API validation** → Move to `app/schemas/`

#### 📝 **Example**:
```python
# ✅ GOOD - models/job.py
from app.schemas.job import JobStatus  # Import from schemas

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")

    @property
    def is_active(self) -> bool:  # Simple computed property - OK
        return self.status == "published"

# ❌ BAD - Don't define enums in models
class JobStatus(str, Enum):  # Move to schemas!
    DRAFT = "draft"
```

---

### 🟢 **2. SCHEMAS (`app/schemas/`)**
**Purpose**: API validation, serialization, and enums

#### ✅ **ALLOWED**:
- **All enums** for the domain
- **Pydantic BaseModel** classes
- **API request/response** schemas
- **Field validation** with validators
- **Data transformation** logic

#### ❌ **FORBIDDEN**:
- **Database queries** → Move to `app/crud/`
- **Business logic** → Move to `app/services/`
- **HTTP handling** → Move to `app/endpoints/`

#### 📝 **Example**:
```python
# ✅ GOOD - schemas/job.py
from enum import Enum
from pydantic import BaseModel, Field, validator

class JobStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    status: JobStatus = JobStatus.DRAFT

    @validator('title')
    def validate_title(cls, v):
        return v.strip()
```

---

### 🟡 **3. CRUD (`app/crud/`)**
**Purpose**: Database operations ONLY

#### ✅ **ALLOWED**:
- **SQLAlchemy queries**
- **Database transactions**
- **Data access methods**
- **Relationship loading**
- **Extending CRUDBase** class

#### ❌ **FORBIDDEN**:
- **HTTP requests/responses** → Move to `app/endpoints/`
- **Business logic** → Move to `app/services/`
- **API validation** → Move to `app/schemas/`

#### 📝 **Example**:
```python
# ✅ GOOD - crud/job.py
from app.crud.base import CRUDBase
from app.models.job import Job

class CRUDJob(CRUDBase[Job, dict, dict]):
    async def get_published_jobs(self, db: AsyncSession) -> List[Job]:
        result = await db.execute(
            select(Job).where(Job.status == "published")
        )
        return result.scalars().all()

job = CRUDJob(Job)

# ❌ BAD - Don't handle HTTP in CRUD
async def create_job_endpoint(request: JobCreate):  # Move to endpoints!
    # HTTP logic doesn't belong in CRUD
```

---

### 🔴 **4. ENDPOINTS (`app/endpoints/`)**
**Purpose**: HTTP routing and request/response handling ONLY

#### ✅ **ALLOWED**:
- **FastAPI route definitions**
- **HTTP request/response** handling
- **Dependency injection**
- **Basic request validation**
- **Calling CRUD/services** methods
- **HTTP status codes**

#### ❌ **FORBIDDEN**:
- **Inline database queries** → Move to `app/crud/`
- **Complex business logic** → Move to `app/services/`
- **Pydantic schema definitions** → Move to `app/schemas/`

#### 📝 **Example**:
```python
# ✅ GOOD - endpoints/jobs.py
from app.crud.job import job as job_crud
from app.schemas.job import JobCreate, JobInfo

@router.post("/jobs", response_model=JobInfo)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new job."""
    return await job_crud.create(db, obj_in=job_data)

# ❌ BAD - Don't write queries in endpoints
@router.get("/jobs")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job))  # Move to CRUD!
    return result.scalars().all()
```

---

### 🟣 **5. SERVICES (`app/services/`)**
**Purpose**: Business logic and orchestration

#### ✅ **ALLOWED**:
- **Complex business rules**
- **Orchestrating multiple CRUD** operations
- **External API** integrations
- **Data processing** and calculations
- **Email/notification** logic

#### ❌ **FORBIDDEN**:
- **Direct database access** → Use `app/crud/`
- **HTTP request handling** → Move to `app/endpoints/`
- **Schema definitions** → Move to `app/schemas/`

#### 📝 **Example**:
```python
# ✅ GOOD - services/job_service.py
from app.crud.job import job as job_crud
from app.crud.user import user as user_crud

class JobService:
    async def publish_job(self, db: AsyncSession, job_id: int, user_id: int):
        # Business logic combining multiple operations
        job = await job_crud.get(db, id=job_id)
        user = await user_crud.get(db, id=user_id)

        if not user.can_publish_jobs:
            raise ValueError("User cannot publish jobs")

        job.status = "published"
        job.published_at = datetime.utcnow()

        await job_crud.update(db, db_obj=job)
        # Send notifications, etc.

job_service = JobService()
```

---

## 🎯 **STRICT REFACTORING RULES**

### **When refactoring ANY code, follow these steps:**

1. **📍 Identify the concern**:
   - Database operation? → `app/crud/`
   - API validation? → `app/schemas/`
   - Business logic? → `app/services/`
   - HTTP routing? → `app/endpoints/`

2. **🔄 Move code to correct layer**:
   - Extract inline queries to CRUD methods
   - Extract inline schemas to schema files
   - Extract business logic to services

3. **🧹 Clean up imports**:
   - Remove unused imports
   - Import from correct layers

4. **✅ Verify separation**:
   - No database queries in endpoints
   - No HTTP logic in CRUD
   - No schema definitions in models

---

## 📊 **ARCHITECTURE VALIDATION**

### **Before committing, verify:**

#### ✅ **Models**:
```bash
# Should NOT contain:
grep -r "class.*Enum" app/models/          # Enums
grep -r "BaseModel" app/models/           # Pydantic schemas
grep -r "select\|execute" app/models/     # Database queries
```

#### ✅ **Endpoints**:
```bash
# Should NOT contain:
grep -r "select\(" app/endpoints/         # Inline queries
grep -r "class.*BaseModel" app/endpoints/ # Inline schemas
```

#### ✅ **CRUD**:
```bash
# Should NOT contain:
grep -r "FastAPI\|router\|@.*\.get\|@.*\.post" app/crud/ # HTTP logic
```

---

## 🚀 **DEVELOPMENT WORKFLOW**

### **When adding new features:**

1. **🎨 Define schemas first** (`app/schemas/`)
   - Create enums
   - Define request/response models
   - Add validation rules

2. **🗄️ Create CRUD operations** (`app/crud/`)
   - Extend CRUDBase
   - Add domain-specific queries
   - Handle relationships

3. **🏗️ Build services** (`app/services/`) *if needed*
   - Complex business logic
   - Multi-step operations
   - External integrations

4. **🌐 Create endpoints** (`app/endpoints/`)
   - HTTP routing only
   - Call CRUD/services
   - Handle responses

5. **🔧 Update models** (`app/models/`) *if needed*
   - Database schema changes
   - New relationships
   - Import new enums from schemas

---

## ⚠️ **COMMON VIOLATIONS TO AVOID**

### ❌ **NEVER DO THIS**:
```python
# DON'T: Define enums in models
class Job(Base):
    class Status(str, Enum):  # Move to schemas!
        DRAFT = "draft"

# DON'T: Write queries in endpoints
@router.get("/jobs")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job))  # Use CRUD!

# DON'T: Put HTTP logic in CRUD
class CRUDJob:
    async def create_job_endpoint(self, request):  # Use endpoints!
        # HTTP logic in CRUD is forbidden
```

### ✅ **DO THIS INSTEAD**:
```python
# ✅ Define enums in schemas
# schemas/job.py
class JobStatus(str, Enum):
    DRAFT = "draft"

# ✅ Use CRUD in endpoints
# endpoints/jobs.py
@router.get("/jobs")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    return await job_crud.get_all(db)

# ✅ Keep CRUD focused on database
# crud/job.py
class CRUDJob:
    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(Job))
        return result.scalars().all()
```

---

## 📚 **IMPORT PATTERNS**

### **Correct import hierarchy:**
```python
# ✅ Models import from schemas (for enums)
from app.schemas.job import JobStatus

# ✅ CRUD imports models + schemas
from app.models.job import Job
from app.schemas.job import JobCreate

# ✅ Services import CRUD + schemas
from app.crud.job import job as job_crud
from app.schemas.job import JobInfo

# ✅ Endpoints import CRUD + schemas + services
from app.crud.job import job as job_crud
from app.schemas.job import JobCreate, JobInfo
from app.services.job_service import job_service
```

---

## 🎯 **ENFORCEMENT**

### **These rules are MANDATORY for:**
- All new features
- All bug fixes
- All refactoring work
- All code reviews

### **Violations will result in:**
- Code review rejection
- Refactoring requirements
- Architecture documentation updates

---

## 📝 **QUICK REFERENCE**

| Layer | Purpose | Contains | Never Contains |
|-------|---------|----------|----------------|
| **Models** | Database schema | Tables, relationships | Enums, Pydantic, queries |
| **Schemas** | API contracts | Pydantic models, enums | Database queries, HTTP logic |
| **CRUD** | Data access | SQLAlchemy queries | HTTP handling, business logic |
| **Endpoints** | HTTP routing | FastAPI routes | Inline queries, schemas |
| **Services** | Business logic | Complex operations | Direct DB access |

---

## 🧪 **TESTING REQUIREMENTS**

### **MANDATORY TESTING RULES**

#### 🎯 **100% Endpoint Coverage Rule**
**EVERY ENDPOINT MUST HAVE COMPREHENSIVE TESTS**

#### ✅ **REQUIRED for ALL endpoints:**

1. **🔐 Authentication Tests**:
   - ✅ Success with valid credentials
   - ❌ Failure with invalid credentials
   - ❌ Failure with missing authentication
   - ❌ Failure with expired tokens
   - ❌ Failure with insufficient permissions

2. **📝 Input Validation Tests**:
   - ✅ Success with valid data
   - ❌ Failure with invalid data types
   - ❌ Failure with missing required fields
   - ❌ Failure with field length violations
   - ❌ Failure with invalid field formats
   - ❌ Failure with boundary value violations

3. **🔄 Business Logic Tests**:
   - ✅ Success scenarios for all workflows
   - ❌ Failure scenarios for business rule violations
   - 🔀 Edge cases and boundary conditions
   - 🎲 Different user roles and permissions
   - 🗂️ Different data states and contexts

4. **💾 Database Operation Tests**:
   - ✅ Successful CRUD operations
   - ❌ Constraint violation handling
   - 🔗 Relationship integrity tests
   - 🔄 Transaction rollback scenarios

5. **🌐 HTTP Response Tests**:
   - ✅ Correct HTTP status codes (200, 201, 404, 400, 401, 403, 500)
   - ✅ Response body structure validation
   - ✅ Response headers verification
   - ✅ Error message format consistency

#### 🧪 **Test File Structure**:
```python
# tests/test_[endpoint_name].py

class TestEndpointName:
    """Comprehensive tests for [endpoint] functionality."""

    # 🟢 SUCCESS SCENARIOS
    async def test_[operation]_success(self):
        """Test successful [operation]."""

    async def test_[operation]_success_with_different_roles(self):
        """Test [operation] with various user roles."""

    # 🔴 ERROR SCENARIOS
    async def test_[operation]_invalid_input(self):
        """Test [operation] with invalid input."""

    async def test_[operation]_unauthorized(self):
        """Test [operation] without authentication."""

    async def test_[operation]_forbidden(self):
        """Test [operation] with insufficient permissions."""

    async def test_[operation]_not_found(self):
        """Test [operation] with non-existent resource."""

    # 🎯 EDGE CASES
    async def test_[operation]_edge_cases(self):
        """Test [operation] edge cases and boundary values."""

    async def test_[operation]_database_constraints(self):
        """Test [operation] database constraint violations."""
```

#### 📊 **Required Test Coverage**:

| Test Type | Minimum Coverage | Description |
|-----------|------------------|-------------|
| **Success Paths** | 100% | All successful workflows |
| **Authentication** | 100% | All auth scenarios |
| **Validation Errors** | 100% | All input validation |
| **Permission Errors** | 100% | All permission checks |
| **Database Errors** | 90% | Constraint violations |
| **Edge Cases** | 80% | Boundary conditions |

#### 🚨 **STRICT ENFORCEMENT**:

##### **BEFORE CREATING/UPDATING ANY ENDPOINT:**
1. ✅ Write tests FIRST (TDD approach)
2. ✅ Cover ALL success scenarios
3. ✅ Cover ALL error scenarios
4. ✅ Test ALL user roles/permissions
5. ✅ Verify ALL response formats
6. ✅ Test ALL edge cases

##### **WHEN UPDATING EXISTING ENDPOINTS:**
1. 🔍 **MANDATORY**: Review existing tests
2. 📝 **MANDATORY**: Update tests for new functionality
3. 🧪 **MANDATORY**: Add tests for new error conditions
4. ✅ **MANDATORY**: Ensure all tests pass
5. 📊 **MANDATORY**: Verify coverage remains 100%

##### **TEST EXECUTION COMMANDS**:
```bash
# Run all endpoint tests
PYTHONPATH=. python -m pytest app/tests/test_*.py -v

# Run specific endpoint tests
PYTHONPATH=. python -m pytest app/tests/test_auth.py -v

# Run with coverage
PYTHONPATH=. python -m pytest --cov=app --cov-report=term-missing

# Coverage must be 100% for endpoints
PYTHONPATH=. python -m pytest --cov=app --cov-fail-under=100
```

#### 🎯 **Test Quality Standards**:

##### ✅ **GOOD TEST EXAMPLES**:
```python
async def test_create_job_success(self, client, auth_headers):
    """Test successful job creation with valid data."""
    job_data = {
        "title": "Software Engineer",
        "description": "Great opportunity",
        "location": "Remote"
    }

    response = await client.post(
        "/api/jobs",
        json=job_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == job_data["title"]
    assert "id" in data
    assert "created_at" in data

async def test_create_job_unauthorized(self, client):
    """Test job creation without authentication fails."""
    response = await client.post("/api/jobs", json={})
    assert response.status_code == 401
    assert "detail" in response.json()

async def test_create_job_invalid_title(self, client, auth_headers):
    """Test job creation with invalid title fails."""
    job_data = {"title": ""}  # Empty title

    response = await client.post(
        "/api/jobs",
        json=job_data,
        headers=auth_headers
    )

    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("title" in str(error).lower() for error in error_detail)
```

##### ❌ **BAD TEST EXAMPLES**:
```python
# DON'T: Test without assertions
async def test_create_job(self, client):
    response = await client.post("/api/jobs", json={})
    # Missing assertions!

# DON'T: Test only success cases
async def test_jobs_endpoint(self, client, auth_headers):
    response = await client.post("/api/jobs", json=valid_data)
    assert response.status_code == 201
    # Missing error scenarios!

# DON'T: Unclear test names
async def test_jobs(self, client):  # Too generic
    # What specific scenario is being tested?
```

#### 🔍 **Test Review Checklist**:

Before merging any code with endpoint changes:

- [ ] ✅ All endpoints have test files
- [ ] ✅ All success paths tested
- [ ] ✅ All authentication scenarios tested
- [ ] ✅ All validation errors tested
- [ ] ✅ All permission errors tested
- [ ] ✅ All edge cases tested
- [ ] ✅ All database constraints tested
- [ ] ✅ All response formats verified
- [ ] ✅ Test coverage is 100%
- [ ] ✅ All tests pass

#### 🚫 **VIOLATIONS RESULT IN**:
- **Code review rejection**
- **Deployment blocking**
- **Refactoring requirements**
- **Additional testing requirements**

#### 📝 **Testing Command Reference**:
```bash
# Create new endpoint test file
touch app/tests/test_[endpoint_name].py

# Run single test
PYTHONPATH=. python -m pytest app/tests/test_auth.py::test_login_success -v

# Run all tests for an endpoint
PYTHONPATH=. python -m pytest app/tests/test_auth.py -v

# Run tests with coverage
PYTHONPATH=. python -m pytest --cov=app.endpoints --cov-report=term-missing

# Debug failing tests
PYTHONPATH=. python -m pytest app/tests/test_auth.py -v -s --tb=long
```

---

## 🚀 **CI/CD & AUTOMATION REQUIREMENTS**

### **MANDATORY CI/CD PIPELINE**

#### 🎯 **GitHub Actions Integration**
**ALL code changes MUST pass automated testing**

#### ✅ **REQUIRED CI/CD Components:**

1. **🧪 Automated Testing**:
   ```yaml
   # .github/workflows/pytest.yml
   - pytest execution on every push/PR
   - Coverage reporting (minimum 75%)
   - Test result artifacts
   - Fixture validation
   ```

2. **🔍 Code Quality Checks**:
   ```yaml
   # .github/workflows/ci.yml
   - Ruff linting and formatting
   - MyPy type checking
   - Security scanning (Bandit)
   - Import sorting
   ```

3. **📊 Coverage Requirements**:
   - **Endpoint coverage**: 100% required
   - **Overall coverage**: 75% minimum
   - **Branch coverage**: Enabled
   - **Coverage reports**: Generated on every run

#### 🛠️ **Local Development Commands**:
```bash
# Quick test validation
make test

# Full test suite with coverage
make test-coverage

# Fix fixtures and test
make test-fix

# CI simulation
make test-ci

# Local validation script
python scripts/test_local.py --verbose --coverage
```

#### 📋 **Pre-commit Requirements**:

##### ✅ **BEFORE every commit:**
- [ ] All tests pass locally
- [ ] Coverage meets minimum requirements
- [ ] Linting passes (ruff check)
- [ ] Formatting applied (ruff format)
- [ ] Type checking passes (mypy)

##### ✅ **BEFORE every push:**
- [ ] `make test-ci` passes locally
- [ ] All new endpoints have comprehensive tests
- [ ] No test fixtures are broken
- [ ] Documentation updated if needed

#### 🚨 **CI/CD Failure Response**:

##### **When CI fails:**
1. **Fix locally first** - Don't push fixes blindly
2. **Run `python scripts/test_local.py --fix-fixtures`**
3. **Validate with `make test-ci`**
4. **Only then push the fix**

##### **Test fixture issues:**
1. **Run fixture diagnosis** - `python scripts/test_local.py --fix-fixtures`
2. **Check async configuration** - Verify pytest-asyncio setup
3. **Validate imports** - Ensure all dependencies are correctly imported
4. **Test collection** - Run `make test-collect` to verify test discovery

#### 📈 **Continuous Improvement**:

##### **Coverage Tracking**:
- Coverage reports uploaded to Codecov
- PR comments with coverage changes
- HTML reports available as artifacts
- Trend monitoring enabled

##### **Performance Monitoring**:
- Test execution time tracking
- Slow test identification
- Resource usage monitoring
- Bottleneck detection

#### 🔒 **Branch Protection**:

##### **Main/Develop branches require:**
- [ ] ✅ All CI checks passing
- [ ] ✅ Code review approval
- [ ] ✅ Up-to-date with base branch
- [ ] ✅ All tests passing
- [ ] ✅ Coverage requirements met

#### 🛠️ **Debugging Failed Tests**:

##### **Local debugging commands:**
```bash
# Diagnose fixture issues
python scripts/test_local.py --fix-fixtures

# Run with maximum verbosity
make test-verbose

# Debug specific test
PYTHONPATH=. python -m pytest app/tests/test_auth.py::test_login_success -v -s --tb=long

# Check test collection
make test-collect

# Full CI simulation
make test-ci
```

##### **Common CI issues:**
1. **Async fixture problems** → Run fixture diagnosis script
2. **Import errors** → Check PYTHONPATH and dependencies
3. **Database issues** → Verify test environment setup
4. **Coverage failures** → Add missing test scenarios

---

**Remember: Comprehensive testing ensures reliable, maintainable code! 🧪**

**⚠️ NO ENDPOINT WITHOUT TESTS! ⚠️**

**🚀 ALL CHANGES MUST PASS CI/CD! 🚀**

---

**Remember: Clean architecture is maintainable architecture! 🏛️**

---

# 🎨 **FRONTEND ARCHITECTURE RULES**

## **Core Frontend Architecture Pattern**

```
📁 frontend/src/
├── 📁 api/              # API client functions ONLY
├── 📁 components/       # React components
├── 📁 contexts/         # React contexts
├── 📁 hooks/            # Custom React hooks
├── 📁 types/            # TypeScript type definitions ONLY
├── 📁 app/              # Next.js app router pages
├── 📁 lib/              # Utility functions
└── 📁 styles/           # Global styles
```

---

## 📋 **STRICT FRONTEND RULES BY LAYER**

### 🟦 **1. TYPES (`src/types/`)**
**Purpose**: TypeScript type definitions and interfaces ONLY

#### ✅ **ALLOWED**:
- **All TypeScript interfaces**
- **All TypeScript type definitions**
- **Enums and const objects**
- **Type utilities and helpers**
- **Domain model types**

#### ❌ **FORBIDDEN**:
- **React components** → Move to `src/components/`
- **API calls** → Move to `src/api/`
- **Business logic** → Move to `src/hooks/` or `src/lib/`
- **React hooks** → Move to `src/hooks/`
- **Inline type definitions in other files** → Centralize in `src/types/`

#### 📝 **Example**:
```typescript
// ✅ GOOD - types/user.ts
export interface User {
  id: number;
  email: string;
  full_name: string;
  roles: UserRole[];
}

export interface UserRole {
  role: Role;
}

export interface Role {
  name: string;
  permissions: string[];
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
}

// ❌ BAD - Don't define types inline in components
// components/UserCard.tsx
interface User {  // Move to types/user.ts!
  id: number;
  name: string;
}
```

#### 🗂️ **Type File Organization**:
```
📁 types/
├── index.ts              # Common types, ApiResponse, etc.
├── user.ts              # User, UserRole, UserFilters
├── todo.ts              # Todo, TodoFormData, TodoStatus
├── interview.ts         # Interview, InterviewFormData
├── workflow.ts          # RecruitmentProcess, ProcessNode
├── admin.ts             # Admin-specific types
├── hooks.ts             # Hook return types
└── components.ts        # Shared component prop types
```

---

### 🟩 **2. API (`src/api/`)**
**Purpose**: API client functions and HTTP requests ONLY

#### ✅ **ALLOWED**:
- **HTTP request functions** (GET, POST, PUT, DELETE)
- **API endpoint definitions**
- **Request/response handling**
- **API client configuration**
- **Error handling for API calls**

#### ❌ **FORBIDDEN**:
- **React components** → Move to `src/components/`
- **Type definitions** → Move to `src/types/`
- **React hooks** → Move to `src/hooks/`
- **UI logic** → Move to `src/components/`
- **State management** → Move to `src/contexts/` or `src/hooks/`

#### 📝 **Example**:
```typescript
// ✅ GOOD - api/users.ts
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { User, UserFilters } from '@/types/user';

export const usersApi = {
  async getUsers(filters?: UserFilters): Promise<ApiResponse<User[]>> {
    const response = await apiClient.get<User[]>('/api/users', { params: filters });
    return { data: response.data, success: true };
  },

  async createUser(userData: CreateUserData): Promise<ApiResponse<User>> {
    const response = await apiClient.post<User>('/api/users', userData);
    return { data: response.data, success: true };
  },
};

// ❌ BAD - Don't define types in API files
export interface User {  // Move to types/user.ts!
  id: number;
  name: string;
}

// ❌ BAD - Don't create hooks in API files
export function useUsers() {  // Move to hooks/useUsers.ts!
  const [users, setUsers] = useState([]);
  // ...
}
```

---

### 🟨 **3. HOOKS (`src/hooks/`)**
**Purpose**: Custom React hooks for shared logic

#### ✅ **ALLOWED**:
- **Custom React hooks**
- **State management logic**
- **Side effect handling**
- **API call orchestration**
- **Data fetching and caching**

#### ❌ **FORBIDDEN**:
- **Type definitions** → Move to `src/types/`
- **API client functions** → Move to `src/api/`
- **React components** → Move to `src/components/`
- **Inline type definitions** → Move to `src/types/`

#### 📝 **Example**:
```typescript
// ✅ GOOD - hooks/useUsers.ts
import { useState, useEffect } from 'react';
import { usersApi } from '@/api/users';
import type { User, UserFilters } from '@/types/user';

export function useUsers(filters?: UserFilters) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const response = await usersApi.getUsers(filters);
        setUsers(response.data || []);
      } catch (err) {
        setError('Failed to load users');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [filters]);

  return { users, loading, error };
}

// ❌ BAD - Don't define types in hooks
interface User {  // Move to types/user.ts!
  id: number;
  name: string;
}

// ❌ BAD - Don't make API calls directly
export function useUsers() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch('/api/users')  // Use API client from api/!
      .then(res => res.json())
      .then(setUsers);
  }, []);
}
```

---

### 🟧 **4. COMPONENTS (`src/components/`)**
**Purpose**: React components ONLY

#### ✅ **ALLOWED**:
- **React functional components**
- **Component-specific prop interfaces** (with "Props" suffix, kept inline in the component file)
- **JSX/TSX markup**
- **Component styling**
- **Event handlers (local to component)**
- **Context value interfaces** (for React Context, kept inline)

#### ❌ **FORBIDDEN**:
- **Shared type definitions** → Move to `src/types/`
- **Domain model types** → Move to `src/types/`
- **API response/request types** → Move to `src/types/`
- **API calls** → Move to `src/api/` and use via hooks
- **Complex business logic** → Move to `src/hooks/` or `src/lib/`
- **Global state management** → Move to `src/contexts/`

#### 📌 **IMPORTANT CLARIFICATION**:
**Component Props interfaces MUST stay inline** in the component file. They should NOT be moved to types/ folder because:
- They are component-specific
- They improve component readability
- They are tightly coupled to the component implementation
- Moving them would make components harder to understand

**Examples of interfaces that SHOULD stay inline:**
- `UserCardProps` - Component props
- `DialogContextValue` - React Context value type
- `ButtonProps extends HTMLAttributes<HTMLButtonElement>` - Component props extending HTML attributes

#### 📝 **Example**:
```typescript
// ✅ GOOD - components/UserCard.tsx
import type { User } from '@/types/user';

interface UserCardProps {  // Component-specific props - OK
  user: User;
  onEdit: (user: User) => void;
  onDelete: (id: number) => void;
}

export default function UserCard({ user, onEdit, onDelete }: UserCardProps) {
  return (
    <div>
      <h3>{user.full_name}</h3>
      <p>{user.email}</p>
      <button onClick={() => onEdit(user)}>Edit</button>
      <button onClick={() => onDelete(user.id)}>Delete</button>
    </div>
  );
}

// ❌ BAD - Don't make API calls directly in components
export default function UserCard({ userId }: { userId: number }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)  // Use hooks and API client!
      .then(res => res.json())
      .then(setUser);
  }, [userId]);
}

// ❌ BAD - Don't define shared types in components
interface User {  // Move to types/user.ts!
  id: number;
  name: string;
}
```

---

### 🟪 **5. PAGES (`src/app/`)**
**Purpose**: Next.js page components and routing

#### ✅ **ALLOWED**:
- **Page components**
- **Layout components**
- **Route-specific logic**
- **Server components** (when using Next.js 13+)
- **Page-specific state management**

#### ❌ **FORBIDDEN**:
- **Shared type definitions** → Move to `src/types/`
- **Reusable components** → Move to `src/components/`
- **API client functions** → Move to `src/api/`
- **Shared hooks** → Move to `src/hooks/`

---

## 🎯 **STRICT TYPE MANAGEMENT RULES**

### **Type Definition Rules:**

1. **📍 ALL types MUST be in `src/types/` folder**
   - No inline interfaces in components (except Props)
   - No inline types in API files
   - No inline types in hooks
   - No inline types in pages

2. **🗂️ Group related types in domain files**:
   - `types/user.ts` - All user-related types
   - `types/todo.ts` - All todo-related types
   - `types/interview.ts` - All interview-related types
   - `types/workflow.ts` - All workflow-related types

3. **📤 Export all types properly**:
   ```typescript
   // types/user.ts
   export interface User { ... }
   export interface UserRole { ... }
   export type UserFilters = { ... };
   ```

4. **📥 Import types from centralized location**:
   ```typescript
   // components/UserCard.tsx
   import type { User } from '@/types/user';

   // api/users.ts
   import type { User, UserFilters } from '@/types/user';

   // hooks/useUsers.ts
   import type { User } from '@/types/user';
   ```

---

## 🚫 **COMMON FRONTEND VIOLATIONS**

### ❌ **NEVER DO THIS**:

```typescript
// ❌ DON'T: Define types inline in components
// components/UserList.tsx
interface User {  // Move to types/user.ts!
  id: number;
  name: string;
}

// ❌ DON'T: Define types inline in API files
// api/users.ts
interface UserResponse {  // Move to types/user.ts!
  users: User[];
  total: number;
}

// ❌ DON'T: Make API calls directly in components
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch('/api/users')  // Use hooks and API client!
      .then(res => res.json())
      .then(setUsers);
  }, []);
}

// ❌ DON'T: Put business logic in components
function UserCard({ user }) {
  const handleSubmit = async () => {
    // Complex validation logic
    // API calls
    // Error handling
    // All should be in hooks or API layer!
  };
}
```

### ✅ **DO THIS INSTEAD**:

```typescript
// ✅ Define types centrally
// types/user.ts
export interface User {
  id: number;
  name: string;
  email: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
}

// ✅ Create API client functions
// api/users.ts
import type { User, UserListResponse } from '@/types/user';

export const usersApi = {
  async getUsers(): Promise<ApiResponse<UserListResponse>> {
    const response = await apiClient.get<UserListResponse>('/api/users');
    return { data: response.data, success: true };
  },
};

// ✅ Create custom hooks for data fetching
// hooks/useUsers.ts
import { usersApi } from '@/api/users';
import type { User } from '@/types/user';

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      const response = await usersApi.getUsers();
      setUsers(response.data?.users || []);
      setLoading(false);
    };
    fetchUsers();
  }, []);

  return { users, loading };
}

// ✅ Keep components clean and simple
// components/UserList.tsx
import { useUsers } from '@/hooks/useUsers';
import type { User } from '@/types/user';

export default function UserList() {
  const { users, loading } = useUsers();

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {users.map(user => <UserCard key={user.id} user={user} />)}
    </div>
  );
}
```

---

## 📊 **FRONTEND ARCHITECTURE VALIDATION**

### **Before committing, verify:**

```bash
# Check for inline type definitions in components
grep -r "^interface\|^type " src/components/ src/app/ | grep -v "Props"

# Check for API calls in components
grep -r "fetch\|axios\|apiClient" src/components/ src/app/

# Check for types outside types/ folder
grep -r "^export interface\|^export type" src/ --exclude-dir=types

# Verify all types are exported
ls src/types/*.ts | xargs grep "^export"
```

---

## 🎯 **FRONTEND DEVELOPMENT WORKFLOW**

### **When adding new features:**

1. **🎨 Define types first** (`src/types/`)
   - Create or update type files
   - Define interfaces and types
   - Export all types

2. **🌐 Create API functions** (`src/api/`)
   - Create API client functions
   - Import types from `src/types/`
   - Handle requests/responses

3. **🔧 Create custom hooks** (`src/hooks/`) *if needed*
   - Data fetching hooks
   - State management hooks
   - Import types and API functions

4. **🎨 Build components** (`src/components/`)
   - Import types from `src/types/`
   - Use hooks for data
   - Keep components clean

5. **📄 Create pages** (`src/app/`)
   - Use components and hooks
   - Handle routing
   - Page-specific logic

---

## 📝 **FRONTEND QUICK REFERENCE**

| Layer | Purpose | Contains | Never Contains |
|-------|---------|----------|----------------|
| **types/** | Type definitions | Interfaces, types, enums | Components, API calls, hooks |
| **api/** | API clients | HTTP requests, endpoints | Types, hooks, components |
| **hooks/** | Custom hooks | State logic, data fetching | Types, components |
| **components/** | UI components | JSX, component logic | Shared types, API calls |
| **app/** | Pages/routes | Page components, routing | Shared types, API functions |

---

## ✅ **FRONTEND PRE-COMMIT CHECKLIST**

Before committing frontend code:

- [ ] ✅ All types are in `src/types/` folder
- [ ] ✅ No inline type definitions (except component Props)
- [ ] ✅ All API calls use `src/api/` functions
- [ ] ✅ Components use hooks for data fetching
- [ ] ✅ No business logic in components
- [ ] ✅ Proper type imports from `@/types/`
- [ ] ✅ Build passes without TypeScript errors
- [ ] ✅ No duplicate type definitions
- [ ] ✅ All types are properly exported

---

## 🚨 **FRONTEND VIOLATIONS RESULT IN**:
- **PR rejection**
- **Refactoring requirements**
- **Type consolidation**
- **Architecture review**

---

**Remember: Clean type organization leads to maintainable code! 📐**

**⚠️ ALL TYPES IN types/ FOLDER! ⚠️**

**🎯 NO INLINE TYPE DEFINITIONS! 🎯**

---

*Last updated: January 2025*
*Enforced by: Claude Code Assistant & CI/CD Pipeline*