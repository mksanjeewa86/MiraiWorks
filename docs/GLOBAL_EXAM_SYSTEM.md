# Global Exam System

## Overview

The MiraiWorks exam system now supports **global/public exams** that can be shared across all companies. This allows system administrators to create standardized exams (like SPI, CAB, etc.) that all companies can use, while maintaining the ability for companies to customize them.

## Key Concepts

### 1. **Global Exams**
- Created by **system administrators**
- `company_id = NULL` (not owned by any company)
- `is_public = True` (visible to all companies)
- **Cannot be edited or deleted** by company admins
- Can be **cloned** by company admins for customization

### 2. **Public Exams**
- Created by **any company**
- `company_id = <company_id>` (owned by specific company)
- `is_public = True` (shared with other companies)
- Can be **cloned** by other companies
- **Cannot be edited or deleted** by other companies

### 3. **Private Exams**
- Created by **company admins**
- `company_id = <company_id>` (owned by specific company)
- `is_public = False` (only visible to own company)
- Can only be edited/deleted by own company

## Workflow

### System Admin Workflow

#### 1. Create Global Exam
```http
POST /api/exams
Authorization: Bearer <system_admin_token>

{
  "title": "SPI Comprehensive Test",
  "description": "Standard SPI aptitude test",
  "exam_type": "spi",
  "company_id": null,  # Global exam
  "is_public": true,   # Public to all companies
  "time_limit_minutes": 90,
  "max_attempts": 1,
  "passing_score": 70,
  ...
}
```

**Questions for global exams:**
- Each question in the global exam is owned by the global exam
- Company admins **cannot modify or delete** global exam questions
- When a company clones the exam, all questions are copied to the new exam

#### 2. Publish Global Exam
- Set `status = "active"` to make it available
- Set `is_public = True` to share with all companies

#### 3. Manage Global Exams
- **Edit**: Only system admins can edit global exams
- **Delete**: Only system admins can delete global exams
- **Add Questions**: Only system admins can add questions to global exams

### Company Admin Workflow

#### 1. View Available Exams

Company admins can see:
- Their own company's exams
- Global/public exams (company_id = NULL, is_public = True)
- Public exams from other companies (is_public = True)

```http
GET /api/exams?status=active
Authorization: Bearer <company_admin_token>

# Returns:
# - Own company exams
# - Global public exams
# - Other companies' public exams
```

#### 2. Use Global Exam (Direct Assignment)

Company admins can assign global exams directly to candidates:

```http
POST /api/exams/{exam_id}/assignments
Authorization: Bearer <company_admin_token>

{
  "candidate_ids": [101, 102, 103],
  "due_date": "2025-10-15T23:59:59Z",
  "custom_time_limit_minutes": 120,  # Override default
  "custom_max_attempts": 2,           # Override default
  "custom_is_randomized": true        # Override default
}
```

**Assignment Settings Override:**
- `custom_time_limit_minutes`: Override exam's default time limit
- `custom_max_attempts`: Override exam's default max attempts
- `custom_is_randomized`: Override exam's randomization setting

#### 3. Clone Global Exam (For Customization)

If a company wants to customize a global exam:

```http
POST /api/exams/{exam_id}/clone
Authorization: Bearer <company_admin_token>

# Creates a copy with:
# - company_id = current user's company
# - is_public = false (private by default)
# - All questions copied
# - Title = "Original Title (Copy)"
```

**After cloning:**
- The cloned exam belongs to the company
- Company can add/edit/delete questions
- Company can modify all exam settings
- Company can assign to their candidates

#### 4. Add Questions to Cloned Exam

```http
POST /api/exams/{cloned_exam_id}/questions
Authorization: Bearer <company_admin_token>

{
  "question_text": "What is...",
  "question_type": "single_choice",
  "options": {"A": "...", "B": "..."},
  "correct_answers": ["A"],
  ...
}
```

**Permission Rules:**
- ✅ Can add questions to **own company's exams**
- ❌ Cannot add questions to **global exams**
- ❌ Cannot add questions to **other companies' public exams**

#### 5. Delete Questions

```http
DELETE /api/questions/{question_id}
Authorization: Bearer <company_admin_token>
```

**Permission Rules:**
- ✅ Can delete questions from **own company's exams**
- ❌ Cannot delete questions from **global exams**
- ❌ Cannot delete questions from **other companies' public exams**

## Database Schema

### Exam Model Changes

```python
class Exam(Base):
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    # NULL = global exam (system admin)
    # NOT NULL = company-owned exam

    is_public = Column(Boolean, default=False, nullable=False)
    # True = shared with other companies
    # False = private to company only

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Track who created the exam
```

### Migration

**Migration ID**: `7aa585326f05`

```python
def upgrade():
    # Add is_public column
    op.add_column('exams', sa.Column('is_public', sa.Boolean(),
                  nullable=False, server_default='0'))

    # Make company_id nullable
    op.alter_column('exams', 'company_id', nullable=True)
```

## API Endpoints

### Clone Exam

```http
POST /api/exams/{exam_id}/clone
```

**Request**: No body required

**Response**:
```json
{
  "id": 123,
  "title": "SPI Comprehensive Test (Copy)",
  "company_id": 5,
  "is_public": false,
  "total_questions": 50,
  ...
}
```

**Permissions**:
- Only company admins can clone
- Cannot clone own company's exams
- Can only clone public exams (is_public = True)

### Create Exam (System Admin)

```http
POST /api/exams
```

**Request**:
```json
{
  "title": "Global SPI Test",
  "company_id": null,  # System admin only
  "is_public": true,
  ...
}
```

**Permissions**:
- Only system admins can create global exams (company_id = null)
- Company admins must have company_id set to their company

### Assign Exam

```http
POST /api/exams/{exam_id}/assignments
```

**Request**:
```json
{
  "candidate_ids": [101, 102],
  "custom_time_limit_minutes": 120,
  "custom_max_attempts": 2,
  "custom_is_randomized": true
}
```

**Permissions**:
- Can assign own company's exams
- Can assign global/public exams
- Cannot assign other companies' private exams

## Permission Matrix

| Operation | Global Exam | Public Exam (Other Co.) | Own Company Exam |
|-----------|-------------|------------------------|------------------|
| **View** | ✅ All | ✅ All | ✅ Own Company |
| **Assign** | ✅ All | ✅ All | ✅ Own Company |
| **Clone** | ✅ All | ✅ All | ❌ N/A |
| **Edit** | ❌ System Admin Only | ❌ Owner Only | ✅ Own Company |
| **Delete** | ❌ System Admin Only | ❌ Owner Only | ✅ Own Company |
| **Add Questions** | ❌ System Admin Only | ❌ Owner Only | ✅ Own Company |
| **Edit Questions** | ❌ System Admin Only | ❌ Owner Only | ✅ Own Company |
| **Delete Questions** | ❌ System Admin Only | ❌ Owner Only | ✅ Own Company |

## Use Cases

### Use Case 1: System Admin Creates Standard SPI Test

1. **System Admin**: Create global SPI exam
   - `company_id = NULL`
   - `is_public = True`
   - Add 100 standard SPI questions

2. **Company A Admin**: Assign SPI exam to candidates
   - Direct assignment (no cloning needed)
   - Override time limit to 120 minutes
   - Assign to 50 candidates

3. **Company B Admin**: Clone and customize SPI exam
   - Clone the global exam
   - Add 10 company-specific questions
   - Assign to their candidates

### Use Case 2: Company Shares Their Custom Exam

1. **Company A Admin**: Create custom programming test
   - `company_id = Company A`
   - `is_public = False` (initially private)

2. **Company A Admin**: Publish exam
   - Set `is_public = True`
   - Now visible to all companies

3. **Company B Admin**: Clone Company A's exam
   - Clone the exam to their company
   - Modify questions as needed
   - Assign to their candidates

### Use Case 3: Company Creates Private Exam

1. **Company A Admin**: Create internal exam
   - `company_id = Company A`
   - `is_public = False`

2. **Only Company A** can:
   - View the exam
   - Edit the exam
   - Assign to their candidates

3. **Other companies**: Cannot see or access this exam

## Error Scenarios

### 1. Company Admin Tries to Edit Global Exam

```http
PUT /api/exams/{global_exam_id}
Authorization: Bearer <company_admin_token>
```

**Response**: `403 Forbidden`
```json
{
  "detail": "Global exams can only be edited by system admins. Clone the exam to customize it."
}
```

### 2. Company Admin Tries to Add Question to Global Exam

```http
POST /api/exams/{global_exam_id}/questions
Authorization: Bearer <company_admin_token>
```

**Response**: `403 Forbidden`
```json
{
  "detail": "Cannot add questions to global exams. Clone the exam first."
}
```

### 3. Company Admin Tries to Clone Own Exam

```http
POST /api/exams/{own_exam_id}/clone
Authorization: Bearer <company_admin_token>
```

**Response**: `400 Bad Request`
```json
{
  "detail": "Cannot clone your own company's exam. Use duplicate instead."
}
```

## Frontend Implementation

### Display Exam List

```typescript
interface Exam {
  id: number;
  title: string;
  company_id: number | null;  // null = global
  is_public: boolean;
  // ... other fields
}

function ExamCard({ exam }: { exam: Exam }) {
  const badge = exam.company_id === null
    ? <Badge>Global</Badge>
    : exam.is_public
    ? <Badge>Public</Badge>
    : <Badge>Private</Badge>;

  return (
    <div>
      <h3>{exam.title}</h3>
      {badge}
      {canClone(exam) && <Button onClick={() => cloneExam(exam.id)}>Clone</Button>}
      {canEdit(exam) && <Button onClick={() => editExam(exam.id)}>Edit</Button>}
      <Button onClick={() => assignExam(exam.id)}>Assign</Button>
    </div>
  );
}

function canClone(exam: Exam): boolean {
  // Can clone if:
  // 1. It's a global/public exam
  // 2. It's not our own exam
  return exam.is_public && exam.company_id !== currentUser.company_id;
}

function canEdit(exam: Exam): boolean {
  // Can edit if:
  // 1. It's our company's exam
  return exam.company_id === currentUser.company_id;
}
```

### Clone Exam Flow

```typescript
async function cloneExam(examId: number) {
  try {
    const response = await fetch(`/api/exams/${examId}/clone`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to clone exam');
    }

    const clonedExam = await response.json();

    toast.success(`Exam cloned successfully: ${clonedExam.title}`);
    router.push(`/admin/exams/${clonedExam.id}/edit`);
  } catch (error) {
    toast.error('Failed to clone exam');
  }
}
```

## Testing

### Test Cases

1. **System Admin Creates Global Exam**
   - ✅ Can create with company_id = NULL
   - ✅ Can add questions
   - ✅ Can edit exam
   - ✅ Can delete exam

2. **Company Admin Views Exams**
   - ✅ Sees own company's exams
   - ✅ Sees global/public exams
   - ✅ Does NOT see other companies' private exams

3. **Company Admin Clones Global Exam**
   - ✅ Clone succeeds
   - ✅ Cloned exam has correct company_id
   - ✅ All questions copied
   - ✅ Can add questions to cloned exam

4. **Company Admin Tries to Edit Global Exam**
   - ❌ Edit fails with 403
   - ❌ Delete fails with 403
   - ❌ Add question fails with 403

5. **Company Admin Assigns Global Exam**
   - ✅ Assignment succeeds
   - ✅ Can override time limit
   - ✅ Candidates receive email

## Migration Checklist

- [x] Update Exam model (company_id nullable, add is_public)
- [x] Create migration `7aa585326f05`
- [x] Update ExamBase, ExamCreate, ExamUpdate, ExamInfo schemas
- [x] Update exam permission logic in endpoints
- [x] Create clone endpoint
- [x] Update get_by_company CRUD to include public exams
- [x] Update assignment logic to allow global exam assignments
- [x] Add validation to prevent editing/deleting global exams
- [x] Update frontend types
- [ ] Add UI for cloning exams
- [ ] Add UI badges for global/public/private exams
- [ ] Update exam list to show exam source
- [ ] Add system admin UI for creating global exams
- [ ] Add tests for all permission scenarios

## Next Steps

1. **Frontend Implementation**
   - Add clone button to exam cards
   - Add badges for exam visibility (Global/Public/Private)
   - Add system admin page for creating global exams
   - Update exam list filters

2. **Testing**
   - Create comprehensive test suite
   - Test all permission scenarios
   - Test clone functionality
   - Test assignment with global exams

3. **Documentation**
   - Update API documentation
   - Create user guide for company admins
   - Create system admin guide

---

**Created**: 2025-10-05
**Status**: ✅ Backend Implementation Complete
**Migration**: `7aa585326f05_make_exam_company_id_nullable_add_is_public.py`
