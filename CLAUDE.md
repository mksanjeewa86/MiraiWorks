# MiraiWorks Development Guidelines

## Project Architecture Rules

This document defines the **STRICT** architectural rules that must be followed in all future development. These rules ensure code maintainability, separation of concerns, and consistent project structure.

> **Note**: For additional development guidelines and testing requirements, see [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

---

## ⚡ **CRITICAL RULES - ALWAYS FOLLOW**

### 🕐 **DateTime Handling**
**ALWAYS use `get_utc_now()` from `app.utils.datetime_utils`**

```python
# ✅ CORRECT
from app.utils.datetime_utils import get_utc_now

user.created_at = get_utc_now()
user.updated_at = get_utc_now()

# ❌ WRONG - NEVER use these
from datetime import datetime, UTC
user.created_at = datetime.utcnow()  # Deprecated!
user.created_at = datetime.now(UTC)  # Don't use directly!
```

**Why this matters:**
- ✅ Consistent timezone handling across the entire application
- ✅ Better testability - can mock `get_utc_now()` easily
- ✅ Future-proofing - easy to change datetime behavior globally
- ✅ Timezone safety - prevents timezone-related bugs

---

### ✅ **Pydantic Validation**
**ALWAYS use `@field_validator` instead of deprecated `@validator`**

```python
# ✅ CORRECT - Pydantic v2
from pydantic import BaseModel, field_validator

class JobCreate(BaseModel):
    title: str

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        return v.strip()

# ❌ WRONG - Deprecated in Pydantic v2
from pydantic import validator

class JobCreate(BaseModel):
    title: str

    @validator('title')  # Don't use this!
    def validate_title(cls, v):
        return v.strip()
```

**Why this matters:**
- ✅ Pydantic v2 compatibility
- ✅ Better type checking and IDE support
- ✅ More explicit validation rules
- ✅ `@classmethod` decorator requirement makes the pattern clearer

---

## 🏗️ **Core Architecture Pattern**

```
📁 backend/app/
├── 📁 models/          # SQLAlchemy database models ONLY
├── 📁 schemas/         # Pydantic schemas + enums
├── 📁 crud/           # Database operations
├── 📁 endpoints/      # HTTP routing logic ONLY
├── 📁 services/       # Business logic
└── 📁 utils/          # Shared utilities (datetime_utils, security, validators)
```

> **⚠️ CRITICAL**: Always use `get_utc_now()` from `app.utils.datetime_utils` instead of `datetime.utcnow()`

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

### 🗄️ **BaseModel Pattern - ALWAYS USE FOR STANDARD MODELS**

**ALL standard models MUST inherit from `BaseModel` instead of `Base`**

#### ✅ **BaseModel provides:**
- `id` - Auto-incrementing primary key (Integer)
- `created_at` - Timestamp when record was created (UTC, server_default)
- `updated_at` - Timestamp when record was last updated (UTC, auto-updated)

#### 📝 **CORRECT USAGE**:
```python
# ✅ GOOD - models/user.py
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    # id, created_at, updated_at are inherited from BaseModel
```

#### ❌ **WRONG - Don't duplicate base fields**:
```python
# ❌ BAD - Duplicating fields that BaseModel provides
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # DUPLICATE!
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # DUPLICATE!
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # DUPLICATE!
    email = Column(String(255), unique=True, nullable=False)
```

#### ⚠️ **WHEN NOT TO USE BaseModel:**

Some models don't need all three fields (id, created_at, updated_at). In these cases, inherit from `Base` directly:

```python
# ✅ GOOD - Models that only need id and created_at
from app.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # No updated_at - refresh tokens don't get updated
```

#### 📊 **Migration Status: ✅ COMPLETE**

**Total Models Using BaseModel: 66 models**

All models with standard `id + created_at + updated_at` pattern have been successfully migrated:

✅ **Core Models**: User, Company, OauthAccount
✅ **Profile Models**: RecruiterProfile, Project, Skill, Education, WorkExperience, Certification, JobPreference
✅ **Workflow Models**: Workflow, WorkflowNode, WorkflowNodeExecution, CandidateWorkflow
✅ **Interview Models**: Interview, InterviewProposal, InterviewNote
✅ **Meeting Models**: Meeting, MeetingRecording, MeetingTranscript, MeetingSummary
✅ **Position Models**: Position, PositionApplication, CompanyProfile
✅ **Exam Models**: Exam, ExamQuestion, ExamSession, ExamAssignment, ExamTemplate
✅ **Message Models**: Message, Notification, Attachment
✅ **Todo Models**: Todo, TodoExtensionRequest
✅ **Calendar Models**: CalendarEvent, CalendarConnection, ExternalCalendarAccount, SyncedEvent
✅ **Video Models**: VideoCall, CallParticipant
✅ **Subscription Models**: SubscriptionPlan, CompanySubscription, Feature, PlanChangeRequest
✅ **Question Bank Models**: QuestionBank, QuestionBankItem
✅ **Connection Models**: CompanyConnection
✅ **Settings Models**: UserSettings, PrivacySettings
✅ **Other Models**: Holiday, SystemUpdate, MBTITest, MBTIQuestion, Resume (+ 10 resume-related models)

**Code Reduction Achieved**: ~1,980 lines removed (66 models × 30 lines average)

#### ⚠️ **Models Correctly NOT Using BaseModel (18 models)**

These models **intentionally use `Base`** because they have different timestamp requirements:

**Immutable Records (write-once, never updated):**
- `AuditLog` - Audit trail (only `created_at`)
- `RefreshToken` - Auth tokens (only `created_at`)
- `PasswordResetRequest` - Reset requests (only `created_at`)
- `PlanFeature` - Junction table (only `added_at`)
- `ProfileView` - View tracking (only `viewed_at`)
- `RecordingConsent` - Legal consent (only `created_at`)
- `CallTranscription` - Transcripts (only `created_at`, `processed_at`)
- `TranscriptionSegment` - Speech segments (only `created_at`)
- `ConnectionInvitation` - Invitations (only `sent_at`, `responded_at`)
- `UserConnection` - Connections (only `created_at`)
- `WorkflowNodeConnection` - Workflow edges (only `created_at`)
- `TodoViewer` - Todo viewers (only `added_at`)
- `WorkflowViewer` - Workflow viewers (only `added_at`)
- `ExamAnswer` - Exam answers (only `created_at`)
- `ExamMonitoringEvent` - Monitoring events (only `created_at`)

**Custom Timestamp Fields:**
- `TodoAttachment` - Uses `uploaded_at` instead of `created_at`

**Static/Junction Tables:**
- `Role` - Permission definitions
- `UserRole` - User-role assignments

#### 🎯 **Benefits of BaseModel:**
- ✅ **DRY principle** - No field duplication across models
- ✅ **Consistency** - All models have the same base fields
- ✅ **Maintainability** - Single source of truth for common fields
- ✅ **Type safety** - Inherited fields are type-checked
- ✅ **Database migrations** - Easier to manage schema changes

---

### 🟢 **2. SCHEMAS (`app/schemas/`)**
**Purpose**: API validation, serialization, and enums

#### ✅ **ALLOWED**:
- **All enums** for the domain
- **Pydantic BaseModel** classes
- **API request/response** schemas
- **Field validation** with `@field_validator`
- **Data transformation** logic

#### ❌ **FORBIDDEN**:
- **Database queries** → Move to `app/crud/`
- **Business logic** → Move to `app/services/`
- **HTTP handling** → Move to `app/endpoints/`
- **`@validator` decorator** → Use `@field_validator` instead (Pydantic v2)

#### 📝 **Example**:
```python
# ✅ GOOD - schemas/job.py
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class JobStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    status: JobStatus = JobStatus.DRAFT

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        return v.strip()

# ❌ BAD - Don't use deprecated @validator
from pydantic import validator  # Don't import this!

@validator('title')  # Use @field_validator instead
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

### 📍 **ENDPOINT CENTRALIZATION - `app/config/endpoints.py`**
**MANDATORY: NO HARDCODED ENDPOINTS**

#### 🎯 **CRITICAL RULE:**
**ALL endpoint paths MUST be defined in `app/config/endpoints.py`**
- ❌ **NEVER** hardcode endpoint strings in `@router` decorators
- ✅ **ALWAYS** use centralized route definitions from `API_ROUTES`

#### 🔤 **ALPHABETICAL ORDERING REQUIREMENT**

**File**: `backend/app/config/endpoints.py`

**MANDATORY: All definitions MUST be in strict alphabetical order (A-Z)**

#### **3-Tier Alphabetical Structure:**

1. **Route Class Definitions** - All route classes alphabetically ordered
2. **API_ROUTES Properties** - All properties alphabetically ordered
3. **__all__ Exports** - All exports alphabetically ordered

#### ✅ **CORRECT Example**:
```python
# ✅ GOOD - config/endpoints.py (alphabetically ordered)

# 1. Route Classes (A-Z)
class AdminRoutes:
    """Administrative endpoints."""
    AUDIT_LOGS = "/admin/audit-logs"
    BULK_DELETE = "/admin/bulk/delete"
    SYSTEM_HEALTH = "/admin/system/health"

class AuthRoutes:
    """Authentication endpoints."""
    ACTIVATE_ACCOUNT = "/activate"
    LOGIN = "/login"
    LOGOUT = "/logout"
    ME = "/me"

class CompanyRoutes:
    """Company management endpoints."""
    BASE = "/companies"
    BY_ID = "/companies/{company_id}"
    CREATE = "/companies"

# 2. API_ROUTES Class (properties A-Z)
class API_ROUTES:
    ADMIN = AdminRoutes
    AUTH = AuthRoutes
    COMPANIES = CompanyRoutes
    # ... (all properties alphabetically ordered)

# 3. __all__ Exports (A-Z)
__all__ = [
    "API_ROUTES",
    "AdminRoutes",
    "AuthRoutes",
    "CompanyRoutes",
    # ... (all exports alphabetically ordered)
]
```

#### ❌ **INCORRECT Example**:
```python
# ❌ BAD - Not alphabetically ordered

# Route classes out of order
class CompanyRoutes:  # Should come after AuthRoutes
    ...

class AuthRoutes:     # Wrong position!
    ...

class AdminRoutes:    # Should be first!
    ...

# API_ROUTES properties out of order
class API_ROUTES:
    COMPANIES = CompanyRoutes  # Wrong order!
    AUTH = AuthRoutes
    ADMIN = AdminRoutes        # Should be first!
```

#### 📝 **Using Centralized Routes in Endpoints**:
```python
# ✅ GOOD - endpoints/jobs.py
from app.config.endpoints import API_ROUTES
from app.crud.job import job as job_crud
from app.schemas.job import JobCreate, JobInfo

router = APIRouter()

@router.post(API_ROUTES.JOBS.CREATE, response_model=JobInfo)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new job."""
    return await job_crud.create(db, obj_in=job_data)

@router.get(API_ROUTES.JOBS.BY_ID, response_model=JobInfo)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get job by ID."""
    return await job_crud.get(db, id=job_id)

# ❌ BAD - Hardcoded endpoint strings
@router.post("/jobs", response_model=JobInfo)  # Don't hardcode!
async def create_job(...):
    ...

@router.get("/jobs/{job_id}", response_model=JobInfo)  # Don't hardcode!
async def get_job(...):
    ...
```

#### ⚠️ **When Adding New Endpoints:**

1. **Find correct alphabetical position** for your route class
2. **Add route class** with properties in alphabetical order
3. **Add to API_ROUTES** at correct alphabetical position
4. **Add to __all__** at correct alphabetical position
5. **Use in endpoint files** via `API_ROUTES.YOUR_ROUTE.CONSTANT`

#### 🎯 **Benefits of Centralization & Alphabetical Ordering:**

- ✅ **Single source of truth** for all endpoint paths
- ✅ **Easy to find routes** - alphabetical navigation
- ✅ **Prevents duplicates** - clear at-a-glance organization
- ✅ **Refactoring safety** - change route in one place
- ✅ **Better git diffs** - ordered structure shows changes clearly
- ✅ **Consistent codebase** - all endpoints follow same pattern
- ✅ **Quick code reviews** - easy to spot mistakes

#### 🔍 **Validation Commands:**
```bash
# Check for hardcoded endpoints in endpoint files
grep -r "@router\.\(get\|post\|put\|delete\|patch\)(\"/\|\"{\)" app/endpoints/

# Verify alphabetical order (manual review required)
# Open backend/app/config/endpoints.py and verify:
# - Route classes: A-Z order
# - API_ROUTES properties: A-Z order
# - __all__ exports: A-Z order
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
from app.utils.datetime_utils import get_utc_now

class JobService:
    async def publish_job(self, db: AsyncSession, job_id: int, user_id: int):
        # Business logic combining multiple operations
        job = await job_crud.get(db, id=job_id)
        user = await user_crud.get(db, id=user_id)

        if not user.can_publish_jobs:
            raise ValueError("User cannot publish jobs")

        job.status = "published"
        job.published_at = get_utc_now()  # Use utility function

        await job_crud.update(db, db_obj=job)
        # Send notifications, etc.

job_service = JobService()
```

---

### 🟤 **6. UTILS (`app/utils/`)**
**Purpose**: Shared utility functions and helpers

#### ✅ **REQUIRED UTILITIES**:

##### **⏰ DateTime Utilities**:
**ALWAYS use `get_utc_now()` from `app.utils.datetime_utils`**

```python
# ✅ GOOD - Always use get_utc_now()
from app.utils.datetime_utils import get_utc_now

user.created_at = get_utc_now()
user.updated_at = get_utc_now()

# ❌ BAD - NEVER use datetime.utcnow()
from datetime import datetime

user.created_at = datetime.utcnow()  # DON'T DO THIS!
```

**Why this matters:**
- ✅ **Consistent timezone handling** across the entire application
- ✅ **Testability** - Utilities can be mocked for testing
- ✅ **Future-proofing** - Easy to modify datetime behavior globally
- ✅ **Timezone safety** - Prevents timezone-related bugs

#### 📝 **Utility Import Patterns**:
```python
# ✅ All datetime operations
from app.utils.datetime_utils import get_utc_now

# ✅ Import other utilities as needed
from app.utils.security import hash_password
from app.utils.validators import validate_email
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

# DON'T: Use datetime.utcnow() directly
from datetime import datetime
user.created_at = datetime.utcnow()  # Use get_utc_now() from utils!
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

# ✅ Use get_utc_now() from utils
from app.utils.datetime_utils import get_utc_now
user.created_at = get_utc_now()
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
| **Utils** | Shared utilities | Helper functions, datetime utils | Business logic, HTTP logic |

### **Critical Utility Functions:**
- 🕐 **DateTime**: Always use `get_utc_now()` from `app.utils.datetime_utils`
- 🔒 **Security**: Use utilities from `app.utils.security`
- ✅ **Validation**: Use utilities from `app.utils.validators`

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

#### 🔤 **IMPORTANT: API Config Alphabetical Ordering Rules**

**File**: `src/api/config.ts`

**MANDATORY RULES FOR `API_ENDPOINTS` OBJECT:**

1. **Top-level keys MUST be alphabetically ordered** (A-Z)
   - Example: `ADMIN`, `ASSIGNMENTS`, `AUTH`, `CALENDAR`, etc.

2. **All nested keys MUST also be alphabetically ordered**
   - Within `AUTH`: `ACTIVATE`, `FORGOT_PASSWORD`, `LOGIN`, `LOGOUT`, etc.
   - Within nested objects like `CALENDAR.ACCOUNTS`: `BASE`, `BY_ID`, `SYNC`

3. **Benefits of alphabetical ordering:**
   - ✅ Quick navigation and endpoint discovery
   - ✅ Prevents duplicate definitions
   - ✅ Easier code reviews and diffs
   - ✅ Consistent codebase structure

#### 📝 **Correct Example**:
```typescript
// ✅ GOOD - api/config.ts
export const API_ENDPOINTS = {
  // Keys are alphabetically ordered
  ADMIN: {
    USER_BY_ID: (id: string | number) => `/api/admin/users/${id}`,
    USERS: '/api/admin/users',
  },

  AUTH: {
    ACTIVATE: '/api/auth/activate',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    ME: '/api/auth/me',
  },

  CALENDAR: {
    ACCOUNTS: {
      BASE: '/api/calendar/accounts',
      BY_ID: (id: number) => `/api/calendar/accounts/${id}`,
      SYNC: (id: number) => `/api/calendar/accounts/${id}/sync`,
    },
    BASE: '/api/calendar',
    EVENTS: '/api/calendar/events',
  },
} as const;
```

#### ❌ **Incorrect Example**:
```typescript
// ❌ BAD - Not alphabetically ordered
export const API_ENDPOINTS = {
  AUTH: { ... },        // Should come after ADMIN
  CALENDAR: { ... },
  ADMIN: { ... },       // Wrong position!

  AUTH: {
    LOGIN: '/api/auth/login',
    ME: '/api/auth/me',
    ACTIVATE: '/api/auth/activate',  // Wrong! Should come before LOGIN
    LOGOUT: '/api/auth/logout',
  },
} as const;
```

#### ⚠️ **When Adding New Endpoints:**
1. Find the correct alphabetical position
2. Insert the new key at that position
3. If adding to nested object, maintain alphabetical order there too
4. Keep section comments for clarity

#### 🔍 **Quick Validation Check:**
```bash
# Check if keys are ordered (manual review)
# Open frontend/src/api/config.ts and verify:
# - Top-level keys: A-Z order
# - Each nested object: keys in A-Z order
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