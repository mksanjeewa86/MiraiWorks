# Exam Settings Refactoring

## Overview

This document describes the refactoring of exam settings to support per-assignee customization. Previously, exam settings like time limits and randomization were defined at the exam level. Now, these settings can be customized for each assignment.

## Motivation

Different candidates may require different exam conditions:
- **Time limits**: Some candidates may need accommodations (extended time)
- **Randomization**: Some assignments may need randomized questions, others may not
- **Max attempts**: Different candidates may be allowed different numbers of attempts

## Changes Made

### 1. Database Schema

**File**: `backend/app/models/exam.py`

#### ExamAssignment Model
Added new field to support per-assignment customization:
```python
custom_is_randomized = Column(Boolean, nullable=True)  # Override exam default randomization
```

**Existing fields** (already supported):
- `custom_time_limit_minutes` - Override exam's default time limit
- `custom_max_attempts` - Override exam's default max attempts

**Exam Model** - The following fields remain at the exam level:
- `time_limit_minutes` - Default time limit for all assignments
- `max_attempts` - Default max attempts for all assignments
- `is_randomized` - Default randomization setting
- `passing_score` - Same for all (policy decision)
- `allow_web_usage`, `monitor_web_usage` - Company policy
- `require_face_verification`, `face_check_interval_minutes` - Company policy
- `show_results_immediately`, `show_correct_answers`, `show_score` - Display settings

### 2. Migration

**File**: `backend/alembic/versions/4362115dcd78_add_custom_is_randomized_to_exam_.py`

```python
def upgrade() -> None:
    op.add_column('exam_assignments', sa.Column('custom_is_randomized', sa.Boolean(), nullable=True))

def downgrade() -> None:
    op.drop_column('exam_assignments', 'custom_is_randomized')
```

### 3. Backend Schemas

**File**: `backend/app/schemas/exam.py`

#### ExamAssignmentCreate
```python
class ExamAssignmentCreate(BaseModel):
    exam_id: int
    candidate_ids: list[int]
    due_date: Optional[datetime] = None
    custom_time_limit_minutes: Optional[int] = Field(None, ge=1)
    custom_max_attempts: Optional[int] = Field(None, ge=1, le=10)
    custom_is_randomized: Optional[bool] = None  # NEW
```

#### ExamAssignmentUpdate
```python
class ExamAssignmentUpdate(BaseModel):
    due_date: Optional[datetime] = None
    custom_time_limit_minutes: Optional[int] = Field(None, ge=1)
    custom_max_attempts: Optional[int] = Field(None, ge=1, le=10)
    custom_is_randomized: Optional[bool] = None  # NEW
    is_active: Optional[bool] = None
```

#### ExamAssignmentInfo
```python
class ExamAssignmentInfo(BaseModel):
    # ... existing fields ...
    custom_is_randomized: Optional[bool]  # NEW
    # ... rest of fields ...
```

### 4. Frontend Types

**File**: `frontend/src/types/exam.ts`

#### ExamAssignment Interface
```typescript
export interface ExamAssignment {
  id: number;
  exam_id: number;
  candidate_id: number;
  assigned_by: number | null;
  due_date: string | null;
  custom_time_limit_minutes: number | null;
  custom_max_attempts: number | null;
  custom_is_randomized: boolean | null;  // NEW
  is_active: boolean;
  completed: boolean;
  // ... other fields ...
}
```

## How It Works

### Creating an Exam

When creating an exam, you define:
1. **Content**: Title, description, instructions, questions, answers
2. **Default Settings**: Default time limit, max attempts, randomization
3. **Policies**: Monitoring settings, face verification, result display

### Assigning an Exam

When assigning an exam to a candidate, you can optionally override:
1. **Time Limit**: `custom_time_limit_minutes`
2. **Max Attempts**: `custom_max_attempts`
3. **Randomization**: `custom_is_randomized`

If these fields are `null`, the exam's default values are used.

### Taking an Exam

When a candidate starts an exam session:
1. System checks the assignment for custom settings
2. If custom settings exist, they override the exam defaults
3. If no custom settings, exam defaults are used

### Example Workflow

```typescript
// 1. Create exam with default settings
POST /api/exams
{
  "title": "JavaScript Assessment",
  "time_limit_minutes": 60,      // Default: 60 minutes
  "max_attempts": 2,              // Default: 2 attempts
  "is_randomized": true,          // Default: randomized
  "questions": [...]
}

// 2. Assign to candidate A (use defaults)
POST /api/exams/1/assignments
{
  "candidate_ids": [101],
  // No custom settings - will use exam defaults
}

// 3. Assign to candidate B (needs accommodation)
POST /api/exams/1/assignments
{
  "candidate_ids": [102],
  "custom_time_limit_minutes": 90,    // Extended time
  "custom_max_attempts": 3,           // Extra attempt
  "custom_is_randomized": false       // No randomization
}
```

## Migration Guide

### For Backend Developers

1. **Database**: Run migration `alembic upgrade head`
2. **Assignment Creation**: Update assignment endpoints to accept `custom_is_randomized`
3. **Session Logic**: Update session creation to use assignment overrides

### For Frontend Developers

1. **Types**: Import updated `ExamAssignment` interface
2. **Assignment Form**: Add UI for `custom_is_randomized` toggle
3. **Display**: Show effective settings (custom or default) in assignment views

## API Changes

### Assignment Creation Endpoint

**Before**:
```typescript
{
  exam_id: number;
  candidate_ids: number[];
  due_date?: string;
  custom_time_limit_minutes?: number;
  custom_max_attempts?: number;
}
```

**After**:
```typescript
{
  exam_id: number;
  candidate_ids: number[];
  due_date?: string;
  custom_time_limit_minutes?: number;
  custom_max_attempts?: number;
  custom_is_randomized?: boolean;  // NEW
}
```

## Benefits

1. **Flexibility**: Customize exam conditions per candidate
2. **Accessibility**: Provide accommodations easily
3. **A/B Testing**: Test different settings on different candidates
4. **Compliance**: Meet accessibility requirements
5. **Backwards Compatible**: Existing exams work without changes

## Future Enhancements

Potential future customizations:
- `custom_passing_score` - Different passing scores per assignment
- `custom_face_check_interval` - Adjust monitoring frequency
- `custom_question_subset` - Assign only specific questions from an exam

---

**Created**: 2025-10-05
**Status**: ✅ Implemented
**Migration**: `4362115dcd78`
