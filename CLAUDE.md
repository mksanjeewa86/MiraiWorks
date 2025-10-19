# MiraiWorks Architecture Rules

> See `.github/copilot-instructions.md` for testing guidelines.

## CRITICAL RULES

### DateTime Handling
**ALWAYS use `get_utc_now()` from `app.utils.datetime_utils`**
```python
from app.utils.datetime_utils import get_utc_now
user.created_at = get_utc_now()  # ✅ CORRECT
```
❌ Never: `datetime.utcnow()` or `datetime.now(UTC)`

### Timezone Architecture
- **Backend**: Store UTC, serialize with timezone (`@field_serializer`)
- **Frontend**: Display in user timezone, send UTC ISO strings
- **Data Flow**: User input (local) → UTC storage → UTC response → Local display

### Pydantic v2
Use `@field_validator` (not deprecated `@validator`)
```python
@field_validator('title')
@classmethod
def validate_title(cls, v): return v.strip()
```

## Backend Architecture

### Layer Responsibilities
```
models/    → Database schema ONLY (SQLAlchemy)
schemas/   → API validation (Pydantic + enums)
crud/      → Database queries (extends CRUDBase)
endpoints/ → HTTP routing (FastAPI, use API_ROUTES)
services/  → Business logic (orchestration)
utils/     → Shared utilities (datetime_utils, security)
```

### Models (`app/models/`)
**✅ Use BaseModel** for standard models (provides id, created_at, updated_at)
```python
from app.models.base import BaseModel
class User(BaseModel):
    __tablename__ = "users"
    email = Column(String(255), unique=True)
```
**❌ Never**: Pydantic schemas, enums, queries, business logic in models

### Schemas (`app/schemas/`)
**✅ All enums**, Pydantic models, `@field_validator`
**❌ Never**: Database queries, HTTP logic

### CRUD (`app/crud/`)
**✅ SQLAlchemy queries**, extends CRUDBase
**❌ Never**: HTTP logic, business logic

### Endpoints (`app/endpoints/`)
**✅ FastAPI routes**, call CRUD/services, use `API_ROUTES`
**❌ Never**: Inline queries, inline schemas
```python
from app.config.endpoints import API_ROUTES
@router.post(API_ROUTES.JOBS.CREATE)  # Use centralized routes
```

### Endpoint Centralization (`app/config/endpoints.py`)
**MANDATORY**: All routes in `API_ROUTES`, alphabetically ordered
1. Route classes (A-Z)
2. API_ROUTES properties (A-Z)
3. `__all__` exports (A-Z)

### Services (`app/services/`)
**✅ Complex business logic**, orchestrate CRUD
**❌ Never**: Direct DB access, HTTP handling

### Utils (`app/utils/`)
**Required**: `datetime_utils.get_utc_now()`, security, validators

## Frontend Architecture

### Layer Responsibilities
```
types/      → TypeScript types ONLY (interfaces, enums)
api/        → API client functions (HTTP requests)
hooks/      → Custom React hooks (state, data fetching)
components/ → React components (Props interfaces OK inline)
app/        → Next.js pages (routing)
lib/        → Utility functions
```

### Types (`src/types/`)
**✅ All interfaces/types** (centralized)
**❌ Never**: Components, API calls, hooks
- Group by domain: `user.ts`, `todo.ts`, `interview.ts`
- Export all types properly

### API (`src/api/`)
**✅ HTTP requests**, endpoint definitions
**❌ Never**: Types, hooks, components
- **API_ENDPOINTS** must be alphabetically ordered (top-level + nested)
```typescript
export const API_ENDPOINTS = {
  ADMIN: { /* A-Z */ },
  AUTH: { /* A-Z */ },
  CALENDAR: { /* A-Z */ },
} as const;
```

### Hooks (`src/hooks/`)
**✅ Custom hooks**, state management, API orchestration
**❌ Never**: Types, API client functions, components

### Components (`src/components/`)
**✅ React components**, component Props interfaces (inline)
**❌ Never**: Shared types, API calls, complex business logic
```typescript
import type { User } from '@/types/user';
interface UserCardProps { user: User; } // Props stay inline
```

## Import Hierarchy

**Backend**:
```python
models → schemas (enums)
crud → models + schemas
services → crud + schemas
endpoints → crud + schemas + services
```

**Frontend**:
```typescript
api → types
hooks → api + types
components → types + hooks
```

## Development Workflow

**Backend**: schemas → crud → services (if needed) → endpoints → models (if schema changes)
**Frontend**: types → api → hooks (if needed) → components → pages

## Pre-Commit Checks

**Backend**:
```bash
# No enums/Pydantic in models
grep -r "class.*Enum\|BaseModel" app/models/
# No queries in endpoints
grep -r "select\(" app/endpoints/
# No HTTP in CRUD
grep -r "@.*\.get\|@.*\.post" app/crud/
```

**Frontend**:
```bash
# No inline types (except Props)
grep -r "^interface\|^type " src/components/ src/app/ | grep -v "Props"
# No API calls in components
grep -r "fetch\|axios" src/components/
# API_ENDPOINTS alphabetically ordered (manual check)
```

## Common Violations

**❌ Backend**:
- Enums in models → Move to schemas
- Queries in endpoints → Use CRUD
- `datetime.utcnow()` → Use `get_utc_now()`
- `@validator` → Use `@field_validator`
- Hardcoded endpoint strings → Use `API_ROUTES`

**❌ Frontend**:
- Inline types → Move to types/
- API calls in components → Use hooks + api/
- Unordered API_ENDPOINTS → Alphabetize

## Enforcement

These rules are **MANDATORY**. Violations result in PR rejection.

---
*Last updated: January 2025*
