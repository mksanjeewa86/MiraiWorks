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

**Remember: Clean architecture is maintainable architecture! 🏛️**

*Last updated: [Current Date]*
*Enforced by: Claude Code Assistant*