# User Role Refactoring

**Date**: 2025-10-03
**Status**: Completed

---

## 📋 Overview

This document describes the refactoring of the user role system to simplify role management and leverage company type for context determination.

---

## 🔄 Role Changes

### Old Role Structure
```
- super_admin    # System-level administrator
- company_admin  # Company administrator
- recruiter      # Recruiter company member
- employer       # Employer company member
- candidate      # Job candidate
```

### New Role Structure
```
- system_admin   # System-level administrator (renamed from super_admin)
- admin          # Company administrator (renamed from company_admin)
- member         # Company member (merged recruiter + employer)
- candidate      # Job candidate (unchanged)
```

---

## 🎯 Key Changes

### 1. **Role Renaming**
- `super_admin` → `system_admin`
- `company_admin` → `admin`

### 2. **Role Merging**
- `recruiter` + `employer` → `member`
- Context is now determined by `company.type` field
- If `company.type = 'recruiter'` → member acts as recruiter
- If `company.type = 'employer'` → member acts as employer

### 3. **Company Type Usage**
The `Company` model already has a `type` field with `CompanyType` enum:
```python
class CompanyType(str, Enum):
    RECRUITER = "recruiter"
    EMPLOYER = "employer"
```

This field determines the context for `admin` and `member` roles.

---

## 📁 Files Modified

### Core Configuration
- ✅ `app/utils/constants.py` - Updated `UserRole` enum
- ✅ `app/rbac.py` - Updated role permissions mapping
- ✅ `app/utils/permissions.py` - Updated `check_company_access()`
- ✅ `app/dependencies.py` - Added `require_system_admin()` with backward compatible alias

### Database
- ✅ `alembic/versions/93a8434d5e0c_update_user_roles_rename.py` - Migration for role data changes

### Tests
- ✅ `app/tests/conftest.py` - Updated test fixtures:
  - `test_admin_user` uses `ADMIN` role
  - `test_employer_user` uses `MEMBER` role
  - `test_system_admin` uses `SYSTEM_ADMIN` role
  - Added backward compatible aliases

---

## 🗄️ Database Migration

### Migration Steps

**File**: `alembic/versions/93a8434d5e0c_update_user_roles_rename.py`

#### Upgrade (Forward)
```sql
-- Rename super_admin to system_admin
UPDATE roles
SET name = 'system_admin', description = 'System-level administrator'
WHERE name = 'super_admin';

-- Rename company_admin to admin
UPDATE roles
SET name = 'admin', description = 'Company administrator (context: company type)'
WHERE name = 'company_admin';

-- Merge recruiter and employer into member
UPDATE roles
SET name = 'member', description = 'Company member (context: company type)'
WHERE name = 'recruiter';

UPDATE user_roles ur
SET role_id = (SELECT id FROM roles WHERE name = 'member')
WHERE role_id = (SELECT id FROM roles WHERE name = 'employer');

DELETE FROM roles WHERE name = 'employer';
```

#### Downgrade (Rollback)
```sql
-- Revert system_admin to super_admin
UPDATE roles
SET name = 'super_admin', description = 'Super administrator'
WHERE name = 'system_admin';

-- Revert admin to company_admin
UPDATE roles
SET name = 'company_admin', description = 'Company administrator'
WHERE name = 'admin';

-- Revert member to recruiter
UPDATE roles
SET name = 'recruiter', description = 'Recruiter'
WHERE name = 'member';

-- Recreate employer role
INSERT INTO roles (name, description)
VALUES ('employer', 'Employer');
```

**Note**: The downgrade cannot perfectly restore the recruiter/employer split without additional data tracking which users were which role originally.

---

## 🔐 Updated RBAC Permissions

### system_admin (formerly super_admin)
- **All permissions** across all companies
- System-level administration

### admin (formerly company_admin)
- **Company-level administration** (scoped to their company)
- Context determined by `company.type`
- User management, notifications, password reset
- Company data read/update
- Interview and resume management

### member (merged recruiter + employer)
- **Regular member** of a company
- Context determined by `company.type`:
  - If recruiter company: acts as recruiter
  - If employer company: acts as employer
- Messaging, interviews, calendar, resumes
- Limited user visibility

### candidate (unchanged)
- **Job candidate** (no company affiliation)
- Own profile management
- Interview participation
- Resume management
- Messaging with recruiters/employers

---

## 🧪 Testing Strategy

### Test Fixtures
Updated test fixtures in `conftest.py`:

```python
# System admin (no company)
test_system_admin → UserRole.SYSTEM_ADMIN

# Company admin
test_admin_user → UserRole.ADMIN + company

# Company member (context via company.type)
test_employer_user → UserRole.MEMBER + company (type=employer)

# Candidate (no company)
test_candidate_only_user → UserRole.CANDIDATE
```

### Backward Compatibility
Aliases provided for smooth transition:
- `test_super_admin` → `test_system_admin`
- `require_super_admin()` → `require_system_admin()`

---

## 🚀 Deployment Steps

### 1. Pre-Deployment
```bash
# Review the migration
cd backend
python -m alembic history

# Check current roles in database
# SELECT * FROM roles;
```

### 2. Run Migration
```bash
# Apply migration
python -m alembic upgrade head

# Verify role changes
# SELECT * FROM roles;
# SELECT * FROM user_roles JOIN roles ON user_roles.role_id = roles.id;
```

### 3. Post-Deployment
- Verify all users have correct roles
- Test admin access with new role names
- Verify company type context works correctly

---

## 📝 Code Usage Examples

### Checking User Role with Company Context
```python
from app.utils.constants import UserRole, CompanyType

# Get user's role
user_roles = [ur.role.name for ur in user.user_roles]

# Check if admin
if UserRole.ADMIN.value in user_roles:
    # Check company context
    if user.company.type == CompanyType.RECRUITER:
        # Admin of recruiter company
        pass
    elif user.company.type == CompanyType.EMPLOYER:
        # Admin of employer company
        pass

# Check if member
if UserRole.MEMBER.value in user_roles:
    # Context determined by company.type
    context = user.company.type  # 'recruiter' or 'employer'
```

### Permission Checking
```python
from app.utils.permissions import requires_role
from app.utils.constants import UserRole

# Require system admin
@requires_role([UserRole.SYSTEM_ADMIN])
async def system_level_operation():
    pass

# Require admin or system admin
@requires_role([UserRole.SYSTEM_ADMIN, UserRole.ADMIN])
async def admin_operation():
    pass

# Require member (recruiter or employer based on company)
@requires_role([UserRole.MEMBER])
async def member_operation(current_user: User):
    if current_user.company.type == CompanyType.RECRUITER:
        # Recruiter logic
        pass
    elif current_user.company.type == CompanyType.EMPLOYER:
        # Employer logic
        pass
```

---

## ⚠️ Breaking Changes

### API Changes
- None - role values changed but API behavior remains the same

### Database Schema
- Role names changed in `roles` table
- `recruiter` and `employer` merged into `member`
- User role assignments automatically updated by migration

### Code References
- Old role constants will cause errors:
  - `UserRole.SUPER_ADMIN` → Use `UserRole.SYSTEM_ADMIN`
  - `UserRole.COMPANY_ADMIN` → Use `UserRole.ADMIN`
  - `UserRole.RECRUITER` → Use `UserRole.MEMBER`
  - `UserRole.EMPLOYER` → Use `UserRole.MEMBER`

---

## 🔍 Remaining Work

### Files Still to Update (if needed)
The following files contain old role references and may need updates based on their usage:

**Seed Data**:
- `app/seeds/users_and_companies.py`
- `app/seeds/comprehensive_seed.py`
- `app/seeds/docker_safe_seed.py`

**Tests** (42 test files total):
- `test_permission_matrix_*.py` files
- `test_users_management.py`
- `test_companies.py`
- `test_interviews*.py`
- Others as needed

**Documentation**:
- `docs/SYSTEM_DOCUMENTATION.md`
- `docs/scenario-test-implementations.md`
- `specifications/database_definition.md`

---

## ✅ Checklist

- [x] Update `UserRole` enum
- [x] Update RBAC permissions
- [x] Update permission utilities
- [x] Create database migration
- [x] Update test fixtures
- [x] Add backward compatibility aliases
- [x] Document changes
- [ ] Update seed data files
- [ ] Run migration on staging
- [ ] Update remaining test files
- [ ] Update documentation files

---

## 👥 Authors

**Refactoring completed by**: Claude Code Assistant
**Date**: October 3, 2025
**Project**: MiraiWorks Recruitment System

---

## 📄 Related Documentation

- [RBAC Configuration](../app/rbac.py)
- [User Model](../app/models/user.py)
- [Company Model](../app/models/company.py)
- [Migration File](../alembic/versions/93a8434d5e0c_update_user_roles_rename.py)
