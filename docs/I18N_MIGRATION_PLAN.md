# I18N Translation Migration Plan

## Overview
This document tracks the progress of migrating the MiraiWorks application to use next-intl for internationalization (i18n) with English (en) and Japanese (ja) support.

**Last Updated:** 2025-10-11

---

## Current Status Summary

### ✅ Completed (8 pages)
- [x] Settings page - Full translation support
- [x] Auth pages (Login, Register, Forgot Password, Reset Password, Two-Factor)
- [x] Account Activation page
- [x] Root/Home page

### 🚧 In Progress (0 pages)
- None currently

### 📋 Translation Files Status

#### ✅ Created and Validated
1. **auth.json** (EN/JA) - Authentication pages
2. **common.json** (EN/JA) - Common UI elements
3. **settings.json** (EN/JA) - Settings page ✨ **Fixed duplicate keys**
4. **errors.json** (EN/JA) - Error messages
5. **validation.json** (EN/JA) - Form validation messages

#### ✅ Created but Pages Not Implemented
6. **calendar.json** (EN/JA) - Calendar integration
7. **candidates.json** (EN/JA) - Candidate management
8. **companies.json** (EN/JA) - Company profiles ✨ **Fixed duplicate keys**
9. **dashboard.json** (EN/JA) - Dashboard views
10. **exams.json** (EN/JA) - Exam system
11. **interviews.json** (EN/JA) - Interview scheduling ✨ **Fixed duplicate keys**
12. **jobs.json** (EN/JA) - Job postings
13. **messages.json** (EN/JA) - Messaging system
14. **profile.json** (EN/JA) - User profiles

#### ❌ Need to Create (11 files × 2 languages = 22 files)
- **resumes.json** - Resume builder and management
- **users.json** - User management
- **todos.json** - Task management
- **workflows.json** - Recruitment workflows
- **subscription.json** - Subscription management
- **positions.json** - Position management
- **video-call.json** - Video call interface
- **room.json** - Interview room
- **admin.json** - Admin-specific features
- **website.json** - Marketing/landing pages
- **public.json** - Public-facing pages

---

## Recent Fixes

### Duplicate Key Resolution ✅
Fixed duplicate JSON keys in the following files:

1. **companies.json** (EN/JA):
   - `contacts` → `contactsTab` (Line 76)
   - `notes` → `notesTab` (Line 77)
   - `activity` → `activityTab` (Line 78)

2. **interviews.json** (EN/JA):
   - `feedback` → `feedbackTab` (Line 52)

3. **settings.json** (EN/JA):
   - `title` → `jobTitle` (Line 30, in profile section)

### Settings Page Translation Keys Fixed ✅
Corrected translation key mismatches in notification section:
- Updated `notificationChannels` keys to match JSON structure
- Updated `eventNotifications` keys to match JSON structure

---

## Detailed Migration Plan

### Phase 1: Core User Features (Priority: HIGH)
**Timeline:** 2-3 days

#### 1.1 Dashboard Page
- **File:** `frontend/src/app/[locale]/(app)/dashboard/page.tsx`
- **Translation File:** `dashboard.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace hardcoded strings with `t()` calls
  - [ ] Test with EN/JA switching
- **Estimated Time:** 2 hours

#### 1.2 Profile Page
- **File:** `frontend/src/app/[locale]/(app)/profile/page.tsx`
- **Translation File:** `profile.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace hardcoded strings
  - [ ] Test profile editing in both languages
- **Estimated Time:** 1.5 hours

#### 1.3 Calendar Page
- **File:** `frontend/src/app/[locale]/(app)/calendar/page.tsx`
- **Translation File:** `calendar.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace hardcoded strings
  - [ ] Ensure date formatting respects locale
- **Estimated Time:** 2 hours

---

### Phase 2: Recruitment Core Features (Priority: HIGH)
**Timeline:** 3-4 days

#### 2.1 Jobs Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/jobs/page.tsx`
- **Translation File:** `jobs.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace job listing strings
  - [ ] Handle job status translations
  - [ ] Test job search/filter UI
- **Estimated Time:** 3 hours

#### 2.2 Candidates Page
- **File:** `frontend/src/app/[locale]/(app)/candidates/page.tsx`
- **Translation File:** `candidates.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace candidate list strings
  - [ ] Handle candidate status translations
  - [ ] Test filtering/sorting UI
- **Estimated Time:** 3 hours

#### 2.3 Companies Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/companies/page.tsx`
  - `frontend/src/app/[locale]/(app)/companies/add/page.tsx`
  - `frontend/src/app/[locale]/(app)/companies/[id]/edit/page.tsx`
- **Translation File:** `companies.json` ✅ Already exists (duplicate keys fixed)
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace company profile strings
  - [ ] Handle company tabs: `contactsTab`, `notesTab`, `activityTab`
  - [ ] Test CRUD operations in both languages
- **Estimated Time:** 4 hours

#### 2.4 Interviews Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/interviews/page.tsx`
  - `frontend/src/app/[locale]/(app)/interviews/new/page.tsx`
  - `frontend/src/app/[locale]/(app)/interviews/[id]/page.tsx`
  - `frontend/src/app/[locale]/(app)/interviews/[id]/edit/page.tsx`
- **Translation File:** `interviews.json` ✅ Already exists (duplicate keys fixed)
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace interview scheduling strings
  - [ ] Handle interview details with `feedbackTab`
  - [ ] Test interview types translations
  - [ ] Test status transitions
- **Estimated Time:** 5 hours

---

### Phase 3: Workflow & Exam System (Priority: MEDIUM)
**Timeline:** 4-5 days

#### 3.1 Workflows Page
- **File:** `frontend/src/app/[locale]/(app)/workflows/page.tsx`
- **Translation File:** `workflows.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `workflows.json` (EN/JA)
  - [ ] Define workflow status translations
  - [ ] Define workflow node type translations
  - [ ] Import `useTranslations` hook
  - [ ] Replace workflow builder strings
  - [ ] Test workflow creation/editing
- **Estimated Time:** 6 hours

#### 3.2 Exam System Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/exams/page.tsx`
  - `frontend/src/app/[locale]/(app)/exams/demo/page.tsx`
  - `frontend/src/app/[locale]/(app)/exams/take/[examId]/page.tsx`
  - `frontend/src/app/[locale]/(app)/exams/results/[sessionId]/page.tsx`
  - `frontend/src/app/[locale]/(app)/admin/exams/**/*.tsx`
- **Translation File:** `exams.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook in all exam pages
  - [ ] Replace exam list/detail strings
  - [ ] Handle exam question types
  - [ ] Handle exam timer/proctoring messages
  - [ ] Test exam taking flow
  - [ ] Test admin exam management
- **Estimated Time:** 8 hours

---

### Phase 4: Resume & User Management (Priority: MEDIUM)
**Timeline:** 3-4 days

#### 4.1 Resume Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/resumes/page.tsx`
  - `frontend/src/app/[locale]/(app)/resumes/create/page.tsx`
  - `frontend/src/app/[locale]/(app)/resumes/builder/page.tsx`
  - `frontend/src/app/[locale]/(app)/resumes/[id]/edit/page.tsx`
  - `frontend/src/app/[locale]/(app)/resumes/[id]/preview/page.tsx`
  - `frontend/src/app/[locale]/(app)/resumes/preview/page.tsx`
  - `frontend/src/app/[locale]/public/resume/[slug]/page.tsx`
- **Translation File:** `resumes.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `resumes.json` (EN/JA) with sections:
    - Resume list view
    - Resume builder sections
    - Resume templates
    - Preview/print options
    - Public resume view
  - [ ] Import `useTranslations` hook
  - [ ] Replace resume builder strings
  - [ ] Handle resume section labels
  - [ ] Test resume creation/editing
- **Estimated Time:** 6 hours

#### 4.2 User Management Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/users/page.tsx`
  - `frontend/src/app/[locale]/(app)/users/add/page.tsx`
  - `frontend/src/app/[locale]/(app)/users/[id]/edit/page.tsx`
- **Translation File:** `users.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `users.json` (EN/JA) with sections:
    - User list
    - User roles
    - User status
    - User permissions
    - User actions
  - [ ] Import `useTranslations` hook
  - [ ] Replace user management strings
  - [ ] Test user CRUD operations
- **Estimated Time:** 4 hours

---

### Phase 5: Communication & Collaboration (Priority: MEDIUM)
**Timeline:** 3-4 days

#### 5.1 Messages Page
- **File:** `frontend/src/app/[locale]/(app)/messages/page.tsx`
- **Translation File:** `messages.json` ✅ Already exists
- **Tasks:**
  - [ ] Import `useTranslations` hook
  - [ ] Replace messaging UI strings
  - [ ] Handle message status/timestamps
  - [ ] Test chat functionality
- **Estimated Time:** 3 hours

#### 5.2 Video Call Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/video-call/[id]/page.tsx`
  - `frontend/src/app/[locale]/(app)/room/[roomCode]/page.tsx`
- **Translation Files:**
  - `video-call.json` ❌ Need to create
  - `room.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `video-call.json` (EN/JA)
  - [ ] Create `room.json` (EN/JA)
  - [ ] Import `useTranslations` hook
  - [ ] Replace video call UI strings
  - [ ] Handle connection status messages
  - [ ] Test video call interface
- **Estimated Time:** 5 hours

#### 5.3 Todos Page
- **File:** `frontend/src/app/[locale]/(app)/todos/page.tsx`
- **Translation File:** `todos.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `todos.json` (EN/JA)
  - [ ] Import `useTranslations` hook
  - [ ] Replace todo list strings
  - [ ] Handle todo status
  - [ ] Test todo CRUD
- **Estimated Time:** 2 hours

---

### Phase 6: Admin & Subscription (Priority: LOW)
**Timeline:** 3-4 days

#### 6.1 Admin Pages
- **Files:**
  - `frontend/src/app/[locale]/(app)/admin/plan-requests/page.tsx`
  - `frontend/src/app/[locale]/(app)/admin/plans/page.tsx`
  - `frontend/src/app/[locale]/(app)/admin/question-banks/**/*.tsx`
- **Translation File:** `admin.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `admin.json` (EN/JA)
  - [ ] Import `useTranslations` hook
  - [ ] Replace admin UI strings
  - [ ] Test admin workflows
- **Estimated Time:** 5 hours

#### 6.2 Subscription Page
- **File:** `frontend/src/app/[locale]/(app)/subscription/page.tsx`
- **Translation File:** `subscription.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `subscription.json` (EN/JA)
  - [ ] Import `useTranslations` hook
  - [ ] Replace subscription UI strings
  - [ ] Handle plan features
  - [ ] Test subscription flow
- **Estimated Time:** 3 hours

#### 6.3 Positions Page
- **File:** `frontend/src/app/[locale]/(app)/positions/page.tsx`
- **Translation File:** `positions.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `positions.json` (EN/JA)
  - [ ] Import `useTranslations` hook
  - [ ] Replace position strings
  - [ ] Test position management
- **Estimated Time:** 2 hours

---

### Phase 7: Marketing & Public Pages (Priority: LOW)
**Timeline:** 2-3 days

#### 7.1 Landing Pages
- **Files:**
  - `frontend/src/app/[locale]/(employer)/employer/page.tsx`
  - `frontend/src/app/[locale]/(employer)/employer/about/page.tsx`
  - `frontend/src/app/[locale]/(employer)/employer/services/page.tsx`
  - `frontend/src/app/[locale]/(employer)/employer/pricing/page.tsx`
  - `frontend/src/app/[locale]/(employer)/employer/contact/page.tsx`
  - `frontend/src/app/[locale]/(recruiter)/recruiter/**/*.tsx`
  - `frontend/src/app/[locale]/(candidate)/candidate/page.tsx`
- **Translation File:** `website.json` ❌ Need to create
- **Tasks:**
  - [ ] Create `website.json` (EN/JA) with sections:
    - Hero sections
    - Features
    - Pricing plans
    - Contact forms
    - About content
  - [ ] Import `useTranslations` hook
  - [ ] Replace marketing copy
  - [ ] Test all landing pages
- **Estimated Time:** 6 hours

---

## Translation File Templates

### Standard Structure for New Translation Files

```json
{
  "page": {
    "title": "Page Title",
    "subtitle": "Page subtitle or description"
  },
  "tabs": {
    "tab1": "Tab 1",
    "tab2": "Tab 2"
  },
  "actions": {
    "create": "Create",
    "edit": "Edit",
    "delete": "Delete",
    "cancel": "Cancel",
    "save": "Save"
  },
  "status": {
    "active": "Active",
    "inactive": "Inactive",
    "pending": "Pending"
  },
  "messages": {
    "success": "Operation successful",
    "error": "An error occurred",
    "loading": "Loading..."
  }
}
```

---

## Implementation Checklist for Each Page

When migrating a page to use translations:

### 1. Setup (5 minutes)
- [ ] Import `useTranslations` from `next-intl`
- [ ] Import `useLocale` if needed for locale-specific logic
- [ ] Add translation hook: `const t = useTranslations('namespace');`

### 2. String Replacement (varies by page)
- [ ] Replace page title/heading
- [ ] Replace button labels
- [ ] Replace form labels
- [ ] Replace table headers
- [ ] Replace status badges
- [ ] Replace error/success messages
- [ ] Replace placeholder text
- [ ] Replace tooltips/descriptions

### 3. Dynamic Content (10-15 minutes)
- [ ] Use translation parameters for dynamic values: `t('key', { value })`
- [ ] Handle pluralization if needed
- [ ] Handle date/time formatting with locale
- [ ] Handle number formatting with locale

### 4. Testing (15-20 minutes)
- [ ] Test in English (en)
- [ ] Test in Japanese (ja)
- [ ] Test language switching
- [ ] Check for missing translations (should show key path)
- [ ] Verify dynamic content renders correctly
- [ ] Check responsive design with longer Japanese text

### 5. Validation (5 minutes)
- [ ] No hardcoded strings remain
- [ ] All translation keys exist in JSON files
- [ ] No duplicate keys in JSON files
- [ ] JSON files are valid (use `node -e "JSON.parse(...)"`)

---

## Testing Strategy

### Manual Testing
1. **Language Switching:**
   - Click language switcher in UI
   - Verify all text changes immediately
   - No page reload required

2. **Fallback Behavior:**
   - Remove a translation key temporarily
   - Verify fallback to key path is displayed
   - Console should show warning

3. **Dynamic Content:**
   - Test with different data values
   - Verify interpolation works correctly
   - Check pluralization rules

### Automated Testing (Future)
```typescript
// Example test structure
describe('i18n for Dashboard', () => {
  it('should display in English', () => {
    // Test EN translations
  });

  it('should display in Japanese', () => {
    // Test JA translations
  });

  it('should switch languages', () => {
    // Test language switching
  });
});
```

---

## Common Patterns & Best Practices

### ✅ DO:
```typescript
// Use semantic namespacing
const t = useTranslations('dashboard');
<h1>{t('page.title')}</h1>

// Use parameters for dynamic content
<p>{t('greeting', { name: user.name })}</p>

// Use consistent key structure
{
  "page.title": "Title",
  "page.subtitle": "Subtitle",
  "actions.create": "Create",
  "status.active": "Active"
}
```

### ❌ DON'T:
```typescript
// Don't use inline strings
<h1>Dashboard</h1>

// Don't concatenate translations
<p>{t('hello')} {user.name}</p>

// Don't use inconsistent key naming
{
  "pageTitle": "Title",
  "page_subtitle": "Subtitle",
  "CREATE_ACTION": "Create"
}
```

---

## Known Issues & Resolutions

### Issue 1: Duplicate Keys ✅ RESOLVED
**Problem:** JSON files had duplicate keys causing linter warnings.

**Files Affected:**
- `companies.json`
- `interviews.json`
- `settings.json`

**Resolution:** Renamed conflicting keys with contextual suffixes (e.g., `Tab`, `Section`)

### Issue 2: Notification Tab Keys Mismatch ✅ RESOLVED
**Problem:** Translation keys didn't match the JSON structure.

**Resolution:** Updated component to use correct keys:
- `notificationChannels.emailNotifications`
- `eventNotifications.interviewReminders`

---

## Progress Tracking

### Overall Completion: ~12% (8/66 pages)

| Phase | Pages | Status | Completion |
|-------|-------|--------|------------|
| Phase 1: Core Features | 3 | 🚧 Not Started | 0% |
| Phase 2: Recruitment | 4 page groups | 🚧 Not Started | 0% |
| Phase 3: Workflow & Exams | 2 page groups | 🚧 Not Started | 0% |
| Phase 4: Resume & Users | 2 page groups | 🚧 Not Started | 0% |
| Phase 5: Communication | 3 page groups | 🚧 Not Started | 0% |
| Phase 6: Admin | 3 page groups | 🚧 Not Started | 0% |
| Phase 7: Marketing | 1 page group | 🚧 Not Started | 0% |

### Translation Files: 64% (14/22 needed)
- ✅ Created: 14 files
- ❌ Need to Create: 8 files

---

## Next Steps

### Immediate (This Week):
1. ✅ Complete Settings page Company Profile section translations
2. ✅ Test settings page fully in EN/JA
3. [ ] Start Phase 1: Dashboard, Profile, Calendar

### Short-term (Next 2 Weeks):
1. [ ] Complete Phase 2: Jobs, Candidates, Companies, Interviews
2. [ ] Create missing translation files for workflows, resumes, users
3. [ ] Start Phase 3: Workflows and Exams

### Long-term (Month):
1. [ ] Complete all phases
2. [ ] Add automated i18n tests
3. [ ] Document i18n conventions for team
4. [ ] Consider additional languages (if needed)

---

## Resources

### Documentation
- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [Next.js i18n Routing](https://nextjs.org/docs/app/building-your-application/routing/internationalization)
- [ICU Message Format](https://unicode-org.github.io/icu/userguide/format_parse/messages/)

### Tools
- VS Code JSON Linter (validates translation files)
- `node -e "JSON.parse(require('fs').readFileSync('file.json', 'utf8'))"` (validate JSON)
- Translation management tools (if needed for scaling)

---

## Contributors
- Initial i18n setup: [Your Name]
- Settings page migration: [Your Name]
- Duplicate key fixes: [Your Name]

---

**Last Review:** 2025-10-11
**Next Review:** Weekly (check progress and adjust timeline)
