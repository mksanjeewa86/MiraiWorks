# Backend Endpoint Organization Guide

## Overview

This guide shows how to centralize and organize backend API endpoint paths, similar to the frontend's `API_ENDPOINTS` configuration.

## Benefits

✅ **Single Source of Truth** - All endpoint paths defined in one location
✅ **Easy Maintenance** - Update paths in one place
✅ **Type Safety** - Constants prevent typos
✅ **IDE Autocomplete** - Better developer experience
✅ **Documentation** - Clear overview of all available endpoints
✅ **Consistency** - Standardized path format across codebase

---

## Implementation

### 1. **Centralized Configuration File**

File: `backend/app/config/endpoints.py`

```python
class AuthRoutes:
    """Authentication and authorization endpoints."""
    LOGIN = "/login"
    REGISTER = "/register"
    LOGOUT = "/logout"
    ME = "/me"
    # ... more routes

class API_ROUTES:
    """Centralized API route definitions."""
    AUTH = AuthRoutes
    USERS = UserRoutes
    EXAMS = ExamRoutes
    # ... more route groups
```

### 2. **Usage in Endpoint Files**

#### ❌ **BEFORE** (Hardcoded paths):

```python
# backend/app/endpoints/auth.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # ...

@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # ...

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    # ...
```

#### ✅ **AFTER** (Using centralized constants):

```python
# backend/app/endpoints/auth.py
from fastapi import APIRouter
from app.config.endpoints import API_ROUTES

router = APIRouter()

@router.post(API_ROUTES.AUTH.LOGIN, response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # ...

@router.post(API_ROUTES.AUTH.REGISTER, response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # ...

@router.get(API_ROUTES.AUTH.ME, response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    # ...
```

---

## Examples by Category

### **Auth Endpoints**

```python
from app.config.endpoints import API_ROUTES

@router.post(API_ROUTES.AUTH.LOGIN)
async def login(...): pass

@router.post(API_ROUTES.AUTH.REGISTER)
async def register(...): pass

@router.post(API_ROUTES.AUTH.TWO_FA_VERIFY)
async def verify_2fa(...): pass

@router.post(API_ROUTES.AUTH.PASSWORD_RESET_REQUEST)
async def request_password_reset(...): pass
```

### **Exam Endpoints**

```python
from app.config.endpoints import API_ROUTES

@router.get(API_ROUTES.EXAMS.BASE)
async def list_exams(...): pass

@router.post(API_ROUTES.EXAMS.BASE)
async def create_exam(...): pass

@router.get(API_ROUTES.EXAMS.BY_ID)
async def get_exam(exam_id: int, ...): pass

@router.get(API_ROUTES.EXAMS.STATISTICS)
async def get_exam_statistics(exam_id: int, ...): pass

@router.post(API_ROUTES.EXAMS.SESSION_COMPLETE)
async def complete_exam_session(session_id: int, ...): pass
```

### **Dynamic Path Parameters**

FastAPI automatically extracts path parameters from the route:

```python
from app.config.endpoints import API_ROUTES

# Route: "/exam/exams/{exam_id}"
@router.get(API_ROUTES.EXAMS.BY_ID)
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    # exam_id is automatically extracted from the URL
    exam = await crud.exam.get(db, id=exam_id)
    return exam

# Route: "/exam/sessions/{session_id}/answers"
@router.post(API_ROUTES.EXAMS.SESSION_ANSWERS)
async def submit_answer(
    session_id: int,  # Automatically extracted from path
    answer: AnswerCreate,
    db: AsyncSession = Depends(get_db)
):
    # ...
```

---

## Refactoring Strategy

### **Phase 1: Add Configuration File** ✅

1. Create `backend/app/config/endpoints.py` with all route definitions
2. Organize routes by domain (Auth, Users, Exams, etc.)
3. Use descriptive constant names

### **Phase 2: Update Endpoint Files (Gradual)**

Update files one at a time to avoid breaking changes:

```python
# Step 1: Add import
from app.config.endpoints import API_ROUTES

# Step 2: Replace hardcoded strings
# Before: @router.post("/login")
# After:  @router.post(API_ROUTES.AUTH.LOGIN)
```

### **Phase 3: Verify and Test**

1. Run tests after each file update
2. Verify all endpoints still work
3. Check API documentation (OpenAPI/Swagger)

---

## Recommended Update Order

1. **Auth endpoints** - Most critical, low risk
2. **User endpoints** - Common, well-tested
3. **CRUD endpoints** - Positions, Companies, etc.
4. **Complex endpoints** - Exams, Workflows, etc.
5. **Admin endpoints** - Lower traffic, can update last

---

## Benefits Over Time

### **Immediate Benefits**
- Clearer code
- Easier to find endpoint definitions
- Better IDE support

### **Long-term Benefits**
- API versioning becomes easier
- Path changes only need one-line updates
- Reduces merge conflicts on endpoint paths
- Self-documenting codebase

---

## Quick Reference

### **Common Patterns**

```python
from app.config.endpoints import API_ROUTES

# Simple route
@router.get(API_ROUTES.DASHBOARD.STATS)
async def get_dashboard_stats(...): pass

# Route with path parameter
@router.get(API_ROUTES.USERS.BY_ID)  # "/users/{user_id}"
async def get_user(user_id: int, ...): pass

# Nested route with multiple parameters
@router.get(API_ROUTES.TODOS.ATTACHMENT_BY_ID)
# "/todos/{todo_id}/attachments/{attachment_id}"
async def get_attachment(todo_id: int, attachment_id: int, ...): pass
```

### **Router Prefixes**

```python
from fastapi import APIRouter
from app.config.endpoints import API_ROUTES

# If router has prefix, don't duplicate in route definition
router = APIRouter(prefix="/api/auth")

# Good: Route will be /api/auth/login
@router.post(API_ROUTES.AUTH.LOGIN)  # Just "/login"

# Bad: Route will be /api/auth/api/auth/login
@router.post("/api/auth/login")  # Don't include prefix
```

---

## Testing Impact

### **Before Refactoring**

```python
# test_auth.py
async def test_login(client):
    response = await client.post("/api/auth/login", json={...})
    # If endpoint path changes, test breaks
```

### **After Refactoring**

```python
# test_auth.py
from app.config.endpoints import API_ROUTES

async def test_login(client):
    response = await client.post(
        f"/api/auth{API_ROUTES.AUTH.LOGIN}",  # Centralized path
        json={...}
    )
    # Path changes are automatically reflected in tests
```

---

## Migration Checklist

For each endpoint file:

- [ ] Import `API_ROUTES` from config
- [ ] Replace hardcoded path strings with constants
- [ ] Verify path parameters match function signatures
- [ ] Run endpoint-specific tests
- [ ] Check OpenAPI documentation
- [ ] Verify frontend still connects correctly
- [ ] Update any integration tests
- [ ] Commit with clear message

---

## Example: Complete File Migration

### **Before: backend/app/endpoints/auth.py**

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(...): pass

@router.post("/register", response_model=RegisterResponse)
async def register(...): pass

@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
async def verify_2fa(...): pass

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(...): pass
```

### **After: backend/app/endpoints/auth.py**

```python
from fastapi import APIRouter
from app.config.endpoints import API_ROUTES

router = APIRouter()

@router.post(API_ROUTES.AUTH.LOGIN, response_model=LoginResponse)
async def login(...): pass

@router.post(API_ROUTES.AUTH.REGISTER, response_model=RegisterResponse)
async def register(...): pass

@router.post(API_ROUTES.AUTH.TWO_FA_VERIFY, response_model=TwoFAVerifyResponse)
async def verify_2fa(...): pass

@router.get(API_ROUTES.AUTH.ME, response_model=UserInfo)
async def get_current_user_info(...): pass
```

**Changes:**
1. Added import: `from app.config.endpoints import API_ROUTES`
2. Replaced 4 hardcoded strings with constants
3. No functional changes - paths remain identical

---

## Next Steps

1. ✅ **Review** the generated `backend/app/config/endpoints.py`
2. **Test** by updating one small endpoint file (e.g., `auth.py`)
3. **Verify** the updated endpoints still work
4. **Gradually migrate** other endpoint files
5. **Update** tests to use centralized paths
6. **Document** any custom route patterns in your team wiki

---

## Questions?

- **Q: Should I update all files at once?**
  A: No, update gradually to minimize risk. Start with low-traffic endpoints.

- **Q: What about router prefixes?**
  A: Constants are defined without prefixes. The router's prefix is added automatically.

- **Q: How do I handle API versioning?**
  A: Add version prefix to router: `APIRouter(prefix="/api/v2/auth")`

- **Q: Will this break existing API clients?**
  A: No, the actual endpoint URLs remain unchanged. Only the backend code organization changes.

---

**Remember: Clean architecture is maintainable architecture! 🏛️**
