# Global Exam System - Quick Test Guide

## What Was Fixed?

**Bug**: Global exams weren't being created properly - all had company_id set instead of NULL.

**Fix**: Changed frontend to send `null` instead of `undefined` for global exams.

---

## Quick Test (5 minutes)

### Step 1: Verify Current State

```bash
cd backend
PYTHONPATH=. python test_global_exam_workflow.py
```

**You should see**:
```
[WARNING] NO GLOBAL EXAMS EXIST!
PRIVATE   :   4 exams
TOTAL     :   4 exams
```

This confirms the bug existed - no global exams in database.

---

### Step 2: Create Global Exam (UI)

1. **Start frontend** (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Log in as system admin**:
   - Email: `admin@miraiworks.com`
   - Password: `admin123` (or whatever password is set)

3. **Navigate to Create Exam**:
   - Go to `/admin/exams/create`

4. **Fill in exam details**:
   - Title: `Test Global Exam`
   - Description: `Testing global exam functionality`
   - Exam Type: `Aptitude`

5. **Enable Global Exam**:
   - Toggle **"Global Exam (System Admin Only)"** to **ON**
   - Notice:
     - Blue highlight appears around section
     - "Public Exam" toggle automatically turns ON
     - Cannot be disabled while Global is ON

6. **Add a test question**:
   - Click "Add Question"
   - Question text: `What is 2+2?`
   - Question type: `Single Choice`
   - Add options: `3`, `4`, `5`
   - Mark `4` as correct answer

7. **Create the exam**:
   - Click "Create Exam" button
   - Should see success message
   - Should redirect to exam list

---

### Step 3: Verify Global Exam Creation

**Option A: Re-run diagnostic test**
```bash
cd backend
PYTHONPATH=. python test_global_exam_workflow.py
```

**You should now see**:
```
[OK] 1 global exam(s) exist in the database

Global exams should be visible to:
  - System admins (can see all exams)
  - Company admins (can see global + public + own company exams)
```

**Option B: Check in UI**
- Exam list should show new exam with 🌍 **Global** badge
- Exam card should have blue border

---

### Step 4: Test Company Admin Visibility

1. **Log out** from system admin

2. **Log in as company admin**:
   - Email: `admin@techcorp.jp`
   - Password: `admin123`

3. **Go to exam list** (`/admin/exams`)

4. **Verify visibility**:
   - Should see "Test Global Exam" with 🌍 badge
   - Should also see own company's exams
   - Should NOT see other companies' private exams

---

### Step 5: Test Clone Functionality

1. While logged in as **company admin** (`admin@techcorp.jp`)

2. Click on the global exam to view details

3. Click **"Clone to My Company"** button

4. Verify:
   - Success message appears
   - Redirects to cloned exam
   - Cloned exam has your company's ID (not global)
   - Cloned exam is private (not public)

---

## Expected Results Summary

| Test | Before Fix | After Fix |
|------|-----------|-----------|
| **Database** | No global exams (company_id set) | Global exams exist (company_id = NULL) |
| **System Admin** | Sees all exams | Sees all exams including new global exam |
| **Company Admin** | Cannot see "global" exams | Can see global exams + own company exams |
| **Clone** | N/A (no global exams) | Can clone global exams to own company |
| **UI Badge** | No badge | 🌍 Global badge displayed |

---

## Troubleshooting

### Issue: "Global Exam" toggle not visible

**Cause**: Not logged in as system admin

**Fix**: Log in with `admin@miraiworks.com`

---

### Issue: Cannot create exam - validation error

**Error**: "Global exams must be public"

**Cause**: This is expected validation (working correctly)

**Fix**: Ensure "Public Exam" toggle is ON

---

### Issue: Global exam not visible to company admin

**Check**:
1. Log in as system admin and verify exam shows 🌍 badge
2. Run diagnostic test to verify `company_id = NULL` in database
3. Check that `is_public = true` for the exam

---

### Issue: TypeScript error in console

**Error**: `Type 'null' is not assignable to type 'number | undefined'`

**Fix**: Verify all files have been updated:
- `frontend/src/types/exam.ts` line 288: `company_id?: number | null`

---

## Files to Check

If something doesn't work, verify these files have the fixes:

1. **frontend/src/app/admin/exams/create/page.tsx**
   - Line 67: `company_id: null,`
   - Line 340: `handleExamDataChange('company_id', null);`

2. **frontend/src/app/admin/exams/[id]/edit/page.tsx**
   - Line 265: `company_id: checked ? null : examData.company_id,`

3. **frontend/src/types/exam.ts**
   - Line 288: `company_id?: number | null;`

4. **backend/app/endpoints/exam.py**
   - Lines 83-89: Global exam validation present

---

## Success Criteria

✅ All these should be true after testing:

- [ ] Diagnostic test shows global exams exist
- [ ] Global exam has `company_id = NULL` in database
- [ ] Global exam has `is_public = true`
- [ ] System admin can create global exams
- [ ] Company admin can see global exams
- [ ] Global exam shows 🌍 badge in UI
- [ ] Company admin can clone global exam
- [ ] Cloned exam has company_id set to company admin's company

---

## Next Actions

After successful testing:

1. ✅ Mark global exam feature as complete
2. 📝 Update user documentation
3. 🗃️ Consider adding seed data with sample global exams
4. 🧪 Add automated tests for global exam CRUD
5. 🚀 Deploy to staging/production

---

**Quick Command Reference**:

```bash
# Run diagnostic test
cd backend && PYTHONPATH=. python test_global_exam_workflow.py

# Start backend
cd backend && uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend && npm run dev

# Check database directly (if needed)
# mysql -u root -p miraiworks
# SELECT id, title, company_id, is_public FROM exams;
```

---

**Status**: ✅ Ready for Testing

**Estimated Test Time**: 5-10 minutes

**Last Updated**: 2025-10-05
