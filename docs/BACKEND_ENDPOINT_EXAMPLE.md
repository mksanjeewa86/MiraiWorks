# Backend Endpoint Refactoring Example

## Complete Example: Auth Endpoints

This shows how to refactor `backend/app/endpoints/auth.py` to use centralized endpoint paths.

---

## BEFORE (Current - Hardcoded Paths)

```python
# backend/app/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password."""
    user = await auth_service.authenticate_user(
        db, login_data.email, login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    tokens = await auth_service.create_tokens(user)
    return LoginResponse(**tokens, user=user)


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Implementation...
    pass


@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
async def verify_2fa(
    request: TwoFAVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify 2FA code."""
    # Implementation...
    pass


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information."""
    return UserInfo.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout current user."""
    # Implementation...
    pass


@router.post("/password-reset/request")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    # Implementation...
    pass
```

---

## AFTER (Using Centralized Constants)

```python
# backend/app/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES  # ← NEW IMPORT
from app.database import get_db
from app.dependencies import get_current_active_user
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(API_ROUTES.AUTH.LOGIN, response_model=LoginResponse)  # ← CHANGED
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password."""
    user = await auth_service.authenticate_user(
        db, login_data.email, login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    tokens = await auth_service.create_tokens(user)
    return LoginResponse(**tokens, user=user)


@router.post(API_ROUTES.AUTH.REGISTER, response_model=RegisterResponse)  # ← CHANGED
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Implementation...
    pass


@router.post(API_ROUTES.AUTH.TWO_FA_VERIFY, response_model=TwoFAVerifyResponse)  # ← CHANGED
async def verify_2fa(
    request: TwoFAVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify 2FA code."""
    # Implementation...
    pass


@router.get(API_ROUTES.AUTH.ME, response_model=UserInfo)  # ← CHANGED
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information."""
    return UserInfo.model_validate(current_user)


@router.post(API_ROUTES.AUTH.LOGOUT)  # ← CHANGED
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout current user."""
    # Implementation...
    pass


@router.post(API_ROUTES.AUTH.PASSWORD_RESET_REQUEST)  # ← CHANGED
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    # Implementation...
    pass
```

---

## Summary of Changes

### ✅ What Changed:
1. **Added import**: `from app.config.endpoints import API_ROUTES`
2. **Replaced 6 hardcoded strings** with constants:
   - `"/login"` → `API_ROUTES.AUTH.LOGIN`
   - `"/register"` → `API_ROUTES.AUTH.REGISTER`
   - `"/2fa/verify"` → `API_ROUTES.AUTH.TWO_FA_VERIFY`
   - `"/me"` → `API_ROUTES.AUTH.ME`
   - `"/logout"` → `API_ROUTES.AUTH.LOGOUT`
   - `"/password-reset/request"` → `API_ROUTES.AUTH.PASSWORD_RESET_REQUEST`

### ✅ What Stayed the Same:
- Function implementations (unchanged)
- Function signatures (unchanged)
- Response models (unchanged)
- Dependencies (unchanged)
- **Actual API endpoint URLs** (unchanged)

### ✅ Benefits Gained:
- ✅ Centralized path management
- ✅ Easier to update paths globally
- ✅ Better IDE autocomplete
- ✅ Consistent naming across backend and frontend
- ✅ Self-documenting code

---

## Verification Steps

After making these changes, verify:

1. **Run the backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Check OpenAPI docs**:
   - Visit http://localhost:8000/docs
   - Verify all auth endpoints are listed
   - Paths should be identical to before

3. **Test endpoints**:
   ```bash
   # Test login
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123"}'
   ```

4. **Run tests**:
   ```bash
   PYTHONPATH=. python -m pytest app/tests/test_auth.py -v
   ```

5. **Frontend verification**:
   - Frontend should connect without any changes
   - API URLs are identical, just organized differently in backend

---

## Next Files to Update

Suggested order (easiest to hardest):

1. ✅ `auth.py` (6 routes) - SHOWN ABOVE
2. `dashboard.py` (3 routes) - Simple CRUD
3. `notifications.py` (5 routes) - Simple operations
4. `files.py` (1 route) - Very simple
5. `companies.py` (CRUD operations)
6. `positions.py` (More complex)
7. `exam.py` (Most complex, many routes)

---

## Quick Migration Script

Want to speed up the process? Here's a Python script to help:

```python
# scripts/migrate_endpoints.py
import re

def migrate_endpoint_file(filepath: str):
    """Migrate a single endpoint file to use API_ROUTES."""

    with open(filepath, 'r') as f:
        content = f.read()

    # Add import if not present
    if 'from app.config.endpoints import API_ROUTES' not in content:
        # Find where to insert (after other app imports)
        insert_pos = content.find('from app.database import')
        if insert_pos == -1:
            insert_pos = content.find('router = APIRouter()')

        lines = content.split('\n')
        # Insert import before router definition
        for i, line in enumerate(lines):
            if 'router = APIRouter()' in line:
                lines.insert(i, 'from app.config.endpoints import API_ROUTES')
                lines.insert(i, '')
                break

        content = '\n'.join(lines)

    # Map of common replacements (auth example)
    replacements = {
        r'@router\.post\("/login"': '@router.post(API_ROUTES.AUTH.LOGIN',
        r'@router\.post\("/register"': '@router.post(API_ROUTES.AUTH.REGISTER',
        r'@router\.get\("/me"': '@router.get(API_ROUTES.AUTH.ME',
        # Add more patterns as needed
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✅ Migrated {filepath}")


# Usage:
# migrate_endpoint_file('backend/app/endpoints/auth.py')
```

---

## Decision Time

**Do you want to:**

1. **Manually update** endpoints one file at a time (recommended for learning)
2. **Use a migration script** to automate replacements (faster, but review changes)
3. **Keep current approach** and only use constants for new endpoints
4. **Hybrid approach** - Use constants for new code, gradually migrate old code

**I recommend Option 1 or 4** for safety and understanding.

---

## Questions?

- **Will this break the frontend?** No, endpoint URLs remain identical.
- **Do I need to update all files?** No, you can migrate gradually.
- **What about tests?** Update tests to use the same constants.
- **How long will this take?** 5-10 minutes per endpoint file.

Ready to start? Begin with `auth.py` using the example above! 🚀
