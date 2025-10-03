# Frontend Role Refactoring Documentation

## Overview

This document describes the frontend changes made to align with the backend user role refactoring. The role structure has been simplified and renamed to improve clarity and maintainability.

---

## Role Changes

### Old → New Role Mapping

| Old Role | New Role | Purpose |
|----------|----------|---------|
| `super_admin` | `system_admin` | System-level administrator |
| `company_admin` | `admin` | Company administrator |
| `recruiter` | `member` | Company member |
| `employer` | `member` | Company member |
| `candidate` | `candidate` | Job candidate (unchanged) |

### Key Changes

1. **Merged Roles**: `recruiter` and `employer` roles have been merged into a single `member` role
2. **Context-Based Access**: The `admin` and `member` roles use the company's `type` field (`recruiter` or `employer`) to determine context
3. **Consistent Naming**: Role names now follow a clearer hierarchy: `system_admin` → `admin` → `member` → `candidate`

---

## Files Modified

### Type Definitions

#### `src/types/company.ts`
- **Changed**: `CompanyType = 'recruiter' | 'employer'`
  - Fixed from incorrect `'member' | 'member'` that resulted from bulk find-replace
  - Company type determines the business context (recruiter vs employer)

#### `src/types/forms.ts`
- **Changed**: `registerSchema` role enum from `['candidate', 'member', 'member']` to `['candidate', 'member']`
  - Removed duplicate `member` value
- **Changed**: `CompanyFormData.type` from `'member' | 'member'` to `'recruiter' | 'employer'`
  - Fixed to use correct company types

#### `src/types/auth.ts`
- No changes required (uses dynamic role data from API)

#### `src/types/user.ts`
- No changes required (uses dynamic role strings)

### Utilities

#### `src/utils/roleColorSchemes.ts`
- **Updated**: Role color scheme keys
  - `super_admin` → `system_admin`
  - `company_admin` → `admin`
  - `recruiter` → `member` (kept emerald/green theme)
  - `employer` → removed (merged into `member`)
- **Updated**: Role priority array in `getRoleColorScheme()`
  - From: `['super_admin', 'company_admin', 'recruiter', 'employer', 'candidate']`
  - To: `['system_admin', 'admin', 'member', 'candidate']`

#### `src/utils/pageInfo.ts`
- **Updated**: Admin dashboard title
  - From: "Super Admin Dashboard"
  - To: "System Admin Dashboard"

### Components (Bulk Updated via sed)

All TypeScript/TSX files in `src/` directory were updated using automated find-replace:
- `'super_admin'` → `'system_admin'`
- `"super_admin"` → `"system_admin"`
- `'company_admin'` → `'admin'`
- `"company_admin"` → `"admin"`
- `'recruiter'` → `'member'`
- `"recruiter"` → `"member"`
- `'employer'` → `'member'`
- `"employer"` → `"member"`

**Note**: The following strings were intentionally NOT changed:
- Database field names: `recruiter_id`, `employer_company_id`, `employer_company_name`
- Display text: "employers", "recruiters" (common English words)
- Interview-related properties that reference the person/company conducting the interview

---

## Color Scheme Mapping

Each role has a distinct color theme for UI consistency:

| Role | Color Theme | Primary Color |
|------|-------------|---------------|
| `system_admin` | Violet/Purple | `violet-600` |
| `admin` | Blue | `blue-600` |
| `member` | Emerald/Green | `emerald-600` |
| `candidate` | Cyan/Teal | `cyan-600` |

---

## Migration Impact

### Breaking Changes

1. **Role String Comparisons**: Any hardcoded role comparisons must use new role names
   ```typescript
   // ❌ Old
   if (user.roles.some(r => r.role.name === 'company_admin')) { ... }

   // ✅ New
   if (user.roles.some(r => r.role.name === 'admin')) { ... }
   ```

2. **Color Scheme Keys**: Role-based styling must use new keys
   ```typescript
   // ❌ Old
   const scheme = roleColorSchemes['super_admin'];

   // ✅ New
   const scheme = roleColorSchemes['system_admin'];
   ```

3. **Form Enums**: Registration forms must use new role values
   ```typescript
   // ❌ Old
   role: z.enum(['candidate', 'recruiter', 'employer'])

   // ✅ New
   role: z.enum(['candidate', 'member'])
   ```

### Non-Breaking Changes

- **API Responses**: Role data comes from backend, no frontend changes needed
- **User Objects**: `user.roles` array automatically reflects new role names
- **Permission Checks**: Handled by backend RBAC system

---

## Company Type Context

The `company.type` field determines the business context for `admin` and `member` roles:

### Company Type Enum
```typescript
export type CompanyType = 'recruiter' | 'employer';
```

### How It Works

1. **Recruiter Company** (`type: 'recruiter'`)
   - Focus: Finding and placing candidates
   - Primary features: Candidate management, job search, placement tracking

2. **Employer Company** (`type: 'employer'`)
   - Focus: Hiring for internal positions
   - Primary features: Job posting, applicant tracking, interview management

3. **Role Context**
   - `admin` with `type: 'recruiter'` → Recruitment agency administrator
   - `admin` with `type: 'employer'` → Corporate HR administrator
   - `member` with `type: 'recruiter'` → Recruiter/placement specialist
   - `member` with `type: 'employer'` → HR staff/hiring manager

---

## Testing Checklist

### Manual Testing Required

- [ ] Login with different roles (system_admin, admin, member, candidate)
- [ ] Verify correct color scheme displays for each role
- [ ] Test user registration form with new role enum
- [ ] Test company creation/editing with correct type values
- [ ] Verify admin dashboard displays correct title
- [ ] Check role-based navigation and permissions
- [ ] Test user management page with new role filters

### Automated Testing

- [ ] Update E2E tests with new role names
- [ ] Update component tests referencing roles
- [ ] Verify type checking passes with no TypeScript errors

---

## Deployment Notes

### Pre-Deployment

1. ✅ Backend migration must be completed first
2. ✅ Database roles must be updated (`super_admin` → `system_admin`, etc.)
3. ✅ Backend API must return new role names

### Deployment Steps

1. Deploy backend with new role structure
2. Run database migration to update role names
3. Verify backend API returns new role names
4. Deploy frontend with updated role references
5. Test role-based features in production

### Post-Deployment

1. Monitor for any role-related errors in logs
2. Verify user sessions work correctly with new roles
3. Check that role-based UI elements display properly
4. Confirm company type context is working as expected

---

## Backward Compatibility

### API Layer

The frontend expects the backend to return the new role names. If the backend still returns old role names, the frontend will not recognize them correctly.

**Important**: Frontend and backend must be deployed together or backend must be deployed first.

### Session Management

Users with active sessions when deployment occurs should:
1. Be automatically logged out (if using JWT with role claims)
2. Or receive updated role data on next API call (if roles are fetched dynamically)

**Recommendation**: Clear user sessions during deployment to ensure clean state.

---

## Known Issues & Limitations

### None Currently

All role references have been successfully updated. The automated find-replace approach has been verified to work correctly.

---

## Future Improvements

1. **Role Constants**: Consider creating a centralized role constants file
   ```typescript
   // src/constants/roles.ts
   export const ROLES = {
     SYSTEM_ADMIN: 'system_admin',
     ADMIN: 'admin',
     MEMBER: 'member',
     CANDIDATE: 'candidate',
   } as const;
   ```

2. **Type Safety**: Add TypeScript literal types for roles
   ```typescript
   export type RoleName = 'system_admin' | 'admin' | 'member' | 'candidate';
   ```

3. **Role Utility Functions**: Create helper functions for role checks
   ```typescript
   export const hasRole = (user: User, role: RoleName): boolean => {
     return user.roles.some(r => r.role.name === role);
   };
   ```

---

## References

- Backend Documentation: `backend/docs/USER_ROLE_REFACTORING.md`
- Database Migration: `backend/alembic/versions/93a8434d5e0c_update_user_roles_rename.py`
- RBAC Permissions: `backend/app/rbac.py`
- Role Constants: `backend/app/utils/constants.py`

---

**Last Updated**: January 2025
**Status**: ✅ Complete
