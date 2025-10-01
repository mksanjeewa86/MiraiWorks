# Assignment Workflow Implementation

**Last Updated**: October 2025


This document describes the comprehensive assignment workflow system implemented for MiraiWorks, designed to handle any type of task assignment scenario (coding tests, document reviews, evaluations, etc.).

## Overview

The assignment workflow enables:
1. **Employers** create assignments with attachments
2. **Assign to candidates** and add **multiple recruiters as viewers**
3. **Draft/Published workflow** - creator controls visibility
4. **Submit-Review-Assess cycle** with automatic state management
5. **Pass/Fail assessment** with detailed feedback

## Architecture Components

### 1. Database Schema Additions

#### New Todo Fields:
```sql
-- Todo type and publishing
todo_type VARCHAR(20) DEFAULT 'regular'           -- 'regular' or 'assignment'
publish_status VARCHAR(20) DEFAULT 'published'    -- 'draft' or 'published'

-- Assignment specific tracking
assignment_status VARCHAR(20) NULL                -- Assignment lifecycle status
assignment_assessment TEXT NULL                   -- Reviewer feedback
assignment_score INTEGER NULL                     -- Numeric score (0-100)
submitted_at DATETIME NULL                        -- When assignee submitted
reviewed_at DATETIME NULL                         -- When review completed
reviewed_by INTEGER NULL                          -- FK to users.id (reviewer)
```

#### Assignment Status Values:
- `not_started` - Assignment created but not begun
- `in_progress` - Assignee is working on it
- `submitted` - Assignee has submitted for review
- `under_review` - Reviewer is evaluating
- `approved` - Assignment passed review
- `rejected` - Assignment failed review

### 2. Workflow States

#### Draft Mode:
- Creator can edit all fields
- **NOT visible** to assignee or viewers
- Creator can add attachments, modify instructions
- Publish when ready

#### Published Mode:
- **Visible** to assignee and viewers
- Assignee can work on the assignment
- Viewers can monitor progress

#### Submission Flow:
1. **Assignee submits** → Status: `submitted`, assignee **cannot edit anymore**
2. **Auto-review mode** → Status: `under_review`
3. **Creator reviews** → Status: `approved`/`rejected` with assessment

### 3. User Permissions

#### Creator (Employer):
- Create assignments in draft mode
- Publish when ready
- Assign to candidates
- Add viewers (recruiters)
- Review and assess submissions
- Full control throughout lifecycle

#### Assignee (Candidate):
- **Cannot see** draft assignments
- Can work on published assignments
- Can submit for review
- **Cannot edit** after submission
- Receives assessment feedback

#### Viewers (Recruiters):
- **Cannot see** draft assignments
- Can monitor published assignments
- Can see progress and final results
- **Cannot edit** or assess

### 4. API Endpoints Added

#### Assignment Workflow:
```
POST /api/todos/{id}/publish          # Publish draft
POST /api/todos/{id}/make-draft       # Return to draft
POST /api/todos/{id}/submit           # Submit for review
POST /api/todos/{id}/review           # Review and assess
```

#### Data Schemas:
```python
# Publishing
TodoPublishUpdate(publish_status: "published" | "draft")

# Submission
AssignmentSubmission(notes?: string)

# Review
AssignmentReview(
    assignment_status: "approved" | "rejected",
    assessment?: string,
    score?: number
)
```

## Implementation Example

### Scenario: Coding Test Assignment

1. **Employer creates coding test:**
   ```python
   todo = TodoCreate(
       title="Python Algorithm Challenge",
       description="Implement sorting algorithms",
       todo_type="assignment",
       publish_status="draft",
       assigned_user_id=candidate_id,
       viewer_ids=[recruiter1_id, recruiter2_id]
   )
   ```

2. **Add test instructions as attachment**
3. **Publish assignment:**
   ```python
   POST /api/todos/{id}/publish
   ```

4. **Candidate works and submits:**
   ```python
   POST /api/todos/{id}/submit
   # Status: submitted, candidate can't edit anymore
   ```

5. **Employer reviews:**
   ```python
   POST /api/todos/{id}/review
   {
       "assignment_status": "approved",
       "assessment": "Excellent implementation of quicksort",
       "score": 85
   }
   ```

## Frontend Integration

### TodoModal Changes:
- **Todo Type selector** (Regular/Assignment)
- **Publish Status toggle** for assignments
- **Assignment Status badge**
- **Submit button** for assignees
- **Review panel** for creators

### Assignment Workflow UI:
```typescript
// Assignment creation
<TodoTypeSelector value={todoType} onChange={setTodoType} />
<PublishStatusToggle value={publishStatus} onChange={setPublishStatus} />

// Assignment submission (assignee view)
{canSubmit && (
  <SubmitButton onClick={handleSubmit} disabled={isSubmitted} />
)}

// Assignment review (creator view)
{canReview && (
  <ReviewPanel
    onApprove={handleApprove}
    onReject={handleReject}
    assessment={assessment}
    score={score}
  />
)}
```

### User Connections Integration:
- **Assignee**: Single user from connections
- **Viewers**: Multiple users from connections
- **Creator controls**: Full assignment lifecycle

## Testing Scenarios

### 1. Complete Assignment Flow
```bash
# Create assignment in draft
POST /api/todos
{
  "title": "Document Review Task",
  "todo_type": "assignment",
  "publish_status": "draft",
  "assigned_user_id": 5,
  "viewer_ids": [10, 11]
}

# Verify draft not visible to assignee/viewers
GET /api/todos  # As assignee - should not see the todo

# Publish assignment
POST /api/todos/{id}/publish

# Verify now visible to assignee/viewers
GET /api/todos  # As assignee - should see the todo

# Assignee submits
POST /api/todos/{id}/submit

# Verify assignee cannot edit
PUT /api/todos/{id}  # Should fail with permission error

# Creator reviews and approves
POST /api/todos/{id}/review
{
  "assignment_status": "approved",
  "assessment": "Great work on the analysis",
  "score": 92
}

# Verify final state
GET /api/todos/{id}
# Should show: assignment_status="approved", reviewed_at, etc.
```

### 2. Visibility Testing
```bash
# Test draft visibility
- Creator: ✅ Can see and edit
- Assignee: ❌ Cannot see
- Viewers: ❌ Cannot see

# Test published visibility
- Creator: ✅ Can see and review
- Assignee: ✅ Can see and work
- Viewers: ✅ Can see (read-only)

# Test post-submission
- Creator: ✅ Can review and assess
- Assignee: ✅ Can see (read-only)
- Viewers: ✅ Can see (read-only)
```

### 3. Permission Testing
```bash
# Test assignment editing after submission
PUT /api/todos/{id}  # As assignee after submit
# Expected: 403 Forbidden

# Test review permissions
POST /api/todos/{id}/review  # As non-creator
# Expected: 403 Forbidden

# Test publish permissions
POST /api/todos/{id}/publish  # As non-creator
# Expected: 403 Forbidden
```

## Backend Implementation Status

✅ **Database Migration**: Added all assignment fields to todos table
✅ **Todo Model**: Added assignment properties and methods
✅ **Constants**: Added TodoType, TodoPublishStatus, AssignmentStatus enums
✅ **Schemas**: Added assignment workflow schemas with validation
⏳ **CRUD Operations**: Need to update for assignment filtering
⏳ **API Endpoints**: Need to add assignment workflow endpoints
⏳ **Permissions**: Need to update permission service

## Frontend Implementation Status

✅ **Base Todo System**: Assignee and viewers selection working
⏳ **Assignment Type UI**: Need todo type selector
⏳ **Publishing Controls**: Need draft/publish toggle
⏳ **Submission UI**: Need submit button for assignees
⏳ **Review UI**: Need review panel for creators
⏳ **Status Indicators**: Need assignment status badges

## Next Steps

1. **Update CRUD operations** for assignment filtering
2. **Add assignment workflow endpoints**
3. **Update permission service** for assignment rules
4. **Implement frontend assignment UI**
5. **Add comprehensive API tests**
6. **Create user documentation**

## Configuration

### Environment Variables
```bash
# Assignment settings
ASSIGNMENT_DEFAULT_REVIEW_DAYS=7
ASSIGNMENT_MAX_SCORE=100
ASSIGNMENT_AUTO_PUBLISH=false
```

### Feature Flags
```python
# Feature toggles
ENABLE_ASSIGNMENT_WORKFLOW=True
ENABLE_ASSIGNMENT_SCORING=True
ENABLE_AUTO_REVIEW_TRANSITION=True
```

This assignment workflow provides a complete foundation for any task assignment scenario while maintaining the existing todo functionality for regular tasks.
