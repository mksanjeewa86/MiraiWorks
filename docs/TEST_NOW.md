# Global Exam System - Live Testing Guide

**Objective**: Verify the global exam bug fix works correctly end-to-end.

**Estimated Time**: 5-10 minutes

---

## ✅ Pre-Test Checklist

- [x] Backend running on `http://localhost:8000`
- [x] Frontend running on `http://localhost:3000`
- [ ] You have admin credentials ready

---

## 🧪 Test 1: Create Global Exam (System Admin)

### Step 1.1: Login as System Admin

1. Open browser: `http://localhost:3000`
2. Login with:
   - **Email**: `admin@miraiworks.com`
   - **Password**: `admin123` (or your password)

### Step 1.2: Navigate to Create Exam

1. Click **"Exams"** in the sidebar
2. Click **"+ Create New Exam"** button

### Step 1.3: Fill Exam Details

**Basic Information**:
```
Title: Global SPI Test
Description: Standard SPI aptitude assessment for all companies
Exam Type: SPI (or Aptitude)
```

**Settings**:
```
Time Limit: 90 minutes
Max Attempts: 1
Passing Score: 70%
```

### Step 1.4: Enable Global Exam ⭐ CRITICAL

**Look for the blue-highlighted section**:
```
┌─────────────────────────────────────────────────────┐
│  🌍 Global Exam (System Admin Only)      [TOGGLE]  │
│  Create a system-wide exam template accessible to  │
│  all companies. Global exams are not tied to any   │
│  specific company.                                  │
└─────────────────────────────────────────────────────┘
```

1. **Toggle "Global Exam" to ON** ← MOST IMPORTANT STEP
2. Verify:
   - ✅ "Public Exam" toggle automatically turns ON
   - ✅ "Public Exam" toggle becomes disabled (greyed out)
   - ✅ Blue highlight remains visible

### Step 1.5: Add a Test Question

1. Click **"Add Question"**
2. Fill in:
   ```
   Question Text: What is 2+2?
   Question Type: Single Choice
   Points: 10
   ```
3. Add options:
   - Option 1: `3`
   - Option 2: `4` ← Mark as correct
   - Option 3: `5`
4. Click **"Save Question"**

### Step 1.6: Create the Exam

1. Click **"Create Exam"** button at bottom
2. Wait for success message
3. Should redirect to exam list

### Step 1.7: Verify in UI

**In the exam list**, look for your new exam:
- ✅ Should have **🌍 Global** badge (purple background)
- ✅ Card should have blue border or highlight
- ✅ Title: "Global SPI Test"

---

## 🔍 Test 2: Verify in Database

### Step 2.1: Run Verification Script

**Windows CMD/PowerShell**:
```cmd
cd backend
python verify_global_exam.py
```

**Expected Output**:
```
================================================================================
GLOBAL EXAM VERIFICATION
================================================================================

[Latest Exam Created]
ID: 17
Title: Global SPI Test
Company ID: NULL
Is Public: True
Created At: 2025-10-05 ...

--------------------------------------------------------------------------------
[SUCCESS] This is a GLOBAL EXAM!
  - company_id = NULL
  - is_public = True
  - Visible to all companies

[Database Statistics]
  GLOBAL    :   1 exams  ← NEW!
  PRIVATE   :   4 exams
  TOTAL     :   5 exams

[Visibility Test]
  [CAN SEE] admin@miraiworks.com   (company_id: 88)
  [CAN SEE] admin@techcorp.jp      (company_id: 89)

================================================================================
```

### Step 2.2: Expected Results

✅ **SUCCESS if**:
- Company ID: **NULL** (not 88 or 89)
- Is Public: **True**
- Both users can see the exam
- Database shows 1 GLOBAL exam

❌ **FAILURE if**:
- Company ID: **88** or **89** (bug still exists)
- Is Public: **False**
- WARNING message appears

---

## 👥 Test 3: Company Admin Visibility

### Step 3.1: Logout System Admin

1. Click user menu (top right)
2. Click **"Logout"**

### Step 3.2: Login as Company Admin

1. Login with:
   - **Email**: `admin@techcorp.jp`
   - **Password**: `admin123`

### Step 3.3: Navigate to Exams

1. Click **"Exams"** in sidebar
2. Look for "Global SPI Test"

### Step 3.4: Verify Visibility

**You should see**:
- ✅ "Global SPI Test" with **🌍 Global** badge
- ✅ Your own company exams (2 exams from TechCorp)
- ✅ Total: 3 exams visible (2 own + 1 global)

**Filters to test**:
- Click **"All Exams"**: Shows all 3 exams
- Click **"My Company"**: Shows only 2 TechCorp exams
- Click **"🌍 Global"**: Shows only 1 global exam

---

## 🔄 Test 4: Clone Functionality

### Step 4.1: Open Global Exam

1. While logged in as `admin@techcorp.jp`
2. Click on **"Global SPI Test"** card
3. Should see exam details page

### Step 4.2: Clone the Exam

1. Look for **"Clone to My Company"** button
2. Click it
3. Clone dialog should appear showing:
   ```
   Clone "Global SPI Test" to your company's exam library?

   What will be cloned:
   - All exam settings
   - All 1 questions with answers

   After cloning, you can:
   - Edit all exam settings
   - Add, edit, or delete questions
   - Assign to your candidates
   ```
4. Click **"Clone Exam"** button

### Step 4.3: Verify Clone Success

**Expected behavior**:
- ✅ Success toast/message appears
- ✅ Redirects to edit page of cloned exam
- ✅ Title shows "Global SPI Test (Copy)" or similar

### Step 4.4: Verify Cloned Exam

**On the edit page, check**:
- ✅ All settings copied (90 min, 70%, etc.)
- ✅ Question "What is 2+2?" is present
- ✅ Exam is now owned by TechCorp (company_id = 89)
- ✅ Exam is **private** (is_public = false)
- ✅ No "🌍 Global" badge (it's now a private company exam)

---

## 🎯 Test 5: Final Database Verification

### Step 5.1: Run Full Diagnostic

```cmd
cd backend
python test_global_exam_workflow.py
```

### Step 5.2: Expected Output

```
[Step 1] Checking current exam state...
GLOBAL    :   1 exams  ← From system admin
PRIVATE   :   5 exams  ← 4 original + 1 cloned
TOTAL     :   6 exams

[Step 3] Testing exam visibility...

  Checking visibility for: admin@miraiworks.com
  Role: system_admin, Company: 88
  Visible exams: 6
    - Global exams:        1
    - Public exams:        0
    - Private exams:       5
    - Own company exams:   2

  Checking visibility for: admin@techcorp.jp
  Role: admin, Company: 89
  Visible exams: 3
    - Global exams:        1  ← Can see global exam
    - Public exams:        0
    - Private exams:       2  ← Own company (including cloned)
    - Own company exams:   2

[OK] 1 global exam(s) exist in the database
```

---

## ✅ Success Criteria

**All of these must be TRUE**:

- [x] Created exam has `company_id = NULL`
- [x] Created exam has `is_public = True`
- [x] Exam shows 🌍 Global badge in UI
- [x] System admin can see the exam
- [x] Company admin can see the exam
- [x] Company admin can clone the exam
- [x] Cloned exam has `company_id = 89` (TechCorp)
- [x] Cloned exam has `is_public = False`
- [x] Database shows 1 GLOBAL exam

---

## 🚨 Troubleshooting

### Issue: No "Global Exam" toggle visible

**Fix**: Make sure you're logged in as `admin@miraiworks.com` (system admin)

---

### Issue: Exam created with company_id = 88

**Diagnosis**: Bug still exists - frontend not sending `null`

**Check**:
1. Verify line 67 in `frontend/src/app/admin/exams/create/page.tsx`
2. Should be: `company_id: null,` (not `undefined`)
3. Restart frontend dev server

---

### Issue: "Global exams must be public" error

**Fix**: This is expected validation - ensure "Public Exam" toggle is ON

---

### Issue: Company admin cannot see global exam

**Check**:
1. Run `python verify_global_exam.py`
2. Verify `company_id = NULL` in database
3. Verify `is_public = True`
4. Check backend console for errors

---

## 📊 Quick Reference

| Test | Expected Result |
|------|----------------|
| **Create global exam** | Success message, redirects to list |
| **Database check** | `company_id = NULL`, `is_public = True` |
| **Badge in UI** | 🌍 Global (purple badge) |
| **System admin sees** | All exams (including global) |
| **Company admin sees** | Global + own company exams |
| **Clone button** | Visible for global exams |
| **Clone success** | Creates private copy with company_id |
| **Cloned exam editable** | Yes, can edit all settings |

---

## 🎉 Next Steps After Testing

### If all tests PASS:
1. ✅ Mark Phase 4 as complete
2. 📝 Update documentation
3. 🚀 Consider deploying to staging
4. 💡 Optional: Implement Phase 5 (direct assignment)

### If any test FAILS:
1. 🐛 Note which test failed
2. 📋 Check troubleshooting section
3. 🔍 Run diagnostic scripts
4. 💬 Report the issue with error details

---

**Good luck with testing! 🚀**

**Report results**: Let me know which tests passed/failed so I can help fix any issues.
