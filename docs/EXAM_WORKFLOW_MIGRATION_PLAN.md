# Exam Workflow Integration - Migration Plan

**Date:** 2025-01-10
**Project:** MiraiWorks
**Feature:** Hybrid Exam System with TODO Workflow Integration

---

## 🎯 Overview

This document outlines the complete migration plan for implementing:

1. **Hybrid Exam System** - Mix company-specific questions with global question bank
2. **TODO-based Exam Workflow** - Exams as TODO type within recruitment workflows
3. **Automated Exam Assignment** - Auto-create, assign, and notify candidates

---

## 📋 Architecture Summary

### **Core Concept:**
- **Exams are TODOs**, not separate workflow nodes
- Workflow nodes create "EXAM" type TODOs
- Completing exam auto-completes TODO → workflow advances

### **Workflow Flow:**
```
Employer creates workflow
  ↓
Node 2: TODO (type=EXAM, config={exam: "SPI + Custom Questions"})
  ↓
Workflow executes → Creates exam TODO for candidate
  ↓
Auto-assigns exam + sends email notification
  ↓
Candidate takes exam
  ↓
Exam completion → Auto-complete TODO
  ↓
Workflow advances to next node
```

---

## 🗂️ Database Schema Changes

### **Phase 1: Question Bank System**

#### **1.1 New Model: `QuestionBank`**
```python
# backend/app/models/question_bank.py

class QuestionBank(Base):
    """Reusable question pools for exams"""

    __tablename__ = "question_banks"

    id: int (PK)
    name: str(255)                    # "SPI Aptitude Test - Verbal"
    description: text
    exam_type: str(50)                # "spi", "skill", "aptitude"
    category: str(100)                # "verbal", "math", "logic", "programming"
    difficulty: str(20)               # "easy", "medium", "hard", "mixed"
    is_public: bool = False           # Global or company-specific
    company_id: int (FK, nullable)    # NULL = global bank
    created_by: int (FK)
    created_at: datetime
    updated_at: datetime

    # Relationships
    questions: relationship("QuestionBankItem")
    company: relationship("Company")
    creator: relationship("User")
```

**SQL Migration:**
```sql
CREATE TABLE question_banks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    exam_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    difficulty VARCHAR(20),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    company_id INT NULL,
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_question_banks_exam_type (exam_type),
    INDEX idx_question_banks_category (category),
    INDEX idx_question_banks_is_public (is_public),
    INDEX idx_question_banks_company_id (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

#### **1.2 New Model: `QuestionBankItem`**
```python
# backend/app/models/question_bank.py

class QuestionBankItem(Base):
    """Individual questions in a question bank"""

    __tablename__ = "question_bank_items"

    id: int (PK)
    bank_id: int (FK)                 # Link to QuestionBank
    question_text: text
    question_type: str(50)            # From QuestionType enum
    order_index: int = 0
    points: float = 1.0
    difficulty: str(20)               # "easy", "medium", "hard"

    # Question data (same structure as ExamQuestion)
    options: JSON                     # {"A": "Option 1", "B": "Option 2"}
    correct_answers: JSON             # ["A", "B"]
    explanation: text
    tags: JSON                        # ["programming", "python", "loops"]

    # Text question settings
    max_length: int
    min_length: int

    # Rating settings
    rating_scale: int

    created_at: datetime
    updated_at: datetime

    # Relationships
    bank: relationship("QuestionBank")
```

**SQL Migration:**
```sql
CREATE TABLE question_bank_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    points FLOAT NOT NULL DEFAULT 1.0,
    difficulty VARCHAR(20),
    options JSON,
    correct_answers JSON,
    explanation TEXT,
    tags JSON,
    max_length INT,
    min_length INT,
    rating_scale INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (bank_id) REFERENCES question_banks(id) ON DELETE CASCADE,

    INDEX idx_question_bank_items_bank_id (bank_id),
    INDEX idx_question_bank_items_difficulty (difficulty),
    INDEX idx_question_bank_items_question_type (question_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### **Phase 2: Exam Enhancements**

#### **2.1 Modify `ExamQuestion` Model**

**Add source tracking fields:**
```python
# backend/app/models/exam.py

class ExamQuestion(Base):
    # ... existing fields ...

    # NEW FIELDS:
    source_type: str(20) = "custom"   # "custom", "template", "question_bank"
    source_bank_id: int (FK, nullable) # If from question bank
    source_question_id: int (FK, nullable) # Original question ID

    # Relationships
    source_bank: relationship("QuestionBank")
    source_question: relationship("QuestionBankItem")
```

**SQL Migration:**
```sql
ALTER TABLE exam_questions
ADD COLUMN source_type VARCHAR(20) NOT NULL DEFAULT 'custom'
    COMMENT 'custom, template, question_bank',
ADD COLUMN source_bank_id INT NULL,
ADD COLUMN source_question_id INT NULL,
ADD INDEX idx_exam_questions_source_type (source_type),
ADD CONSTRAINT fk_exam_questions_source_bank
    FOREIGN KEY (source_bank_id) REFERENCES question_banks(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_exam_questions_source_question
    FOREIGN KEY (source_question_id) REFERENCES question_bank_items(id) ON DELETE SET NULL;
```

---

#### **2.2 Modify `Exam` Model**

**Add question selection rules:**
```python
# backend/app/models/exam.py

class Exam(Base):
    # ... existing fields ...

    # NEW FIELD:
    question_selection_rules: JSON
    # Stores how exam was created (for audit/recreation)
    # Example:
    # {
    #   "custom_count": 10,
    #   "template_selections": [
    #     {"bank_id": 5, "count": 20, "category": "verbal", "difficulty": "medium"}
    #   ]
    # }
```

**SQL Migration:**
```sql
ALTER TABLE exams
ADD COLUMN question_selection_rules JSON NULL
    COMMENT 'Stores hybrid exam creation rules';
```

---

### **Phase 3: TODO Integration**

#### **3.1 Add `TodoType.EXAM` Enum**

```python
# backend/app/utils/constants.py

class TodoType(str, Enum):
    REGULAR = "regular"
    ASSIGNMENT = "assignment"
    EXAM = "exam"  # ← NEW
```

**No SQL migration needed** - enum stored as string

---

#### **3.2 Modify `Todo` Model**

**Add exam-related fields:**
```python
# backend/app/models/todo.py

class Todo(Base):
    # ... existing fields ...

    # NEW FIELDS:
    exam_id: int (FK, nullable)           # Link to Exam
    exam_assignment_id: int (FK, nullable) # Link to ExamAssignment
    exam_config: JSON                     # Exam configuration from workflow

    # Relationships
    exam: relationship("Exam")
    exam_assignment: relationship("ExamAssignment")
```

**SQL Migration:**
```sql
ALTER TABLE todos
ADD COLUMN exam_id INT NULL,
ADD COLUMN exam_assignment_id INT NULL,
ADD COLUMN exam_config JSON NULL
    COMMENT 'Exam configuration from workflow node',
ADD INDEX idx_todos_exam_id (exam_id),
ADD INDEX idx_todos_exam_assignment_id (exam_assignment_id),
ADD CONSTRAINT fk_todos_exam
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_todos_exam_assignment
    FOREIGN KEY (exam_assignment_id) REFERENCES exam_assignments(id) ON DELETE CASCADE;
```

---

#### **3.3 Modify `ExamAssignment` Model**

**Add workflow tracking:**
```python
# backend/app/models/exam.py

class ExamAssignment(Base):
    # ... existing fields ...

    # NEW FIELDS:
    todo_id: int (FK, nullable)                    # Link to TODO
    workflow_node_execution_id: int (FK, nullable) # Workflow tracking

    # Relationships
    todo: relationship("Todo")
    node_execution: relationship("WorkflowNodeExecution")
```

**SQL Migration:**
```sql
ALTER TABLE exam_assignments
ADD COLUMN todo_id INT NULL,
ADD COLUMN workflow_node_execution_id INT NULL,
ADD INDEX idx_exam_assignments_todo_id (todo_id),
ADD INDEX idx_exam_assignments_workflow_execution (workflow_node_execution_id),
ADD CONSTRAINT fk_exam_assignments_todo
    FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_exam_assignments_workflow_execution
    FOREIGN KEY (workflow_node_execution_id)
    REFERENCES workflow_node_executions(id) ON DELETE SET NULL;
```

---

## 📦 New Components to Create

### **Backend Models**

| File | Status | Description |
|------|--------|-------------|
| `backend/app/models/question_bank.py` | ❌ New | QuestionBank + QuestionBankItem models |

### **Backend Schemas**

| File | Status | Description |
|------|--------|-------------|
| `backend/app/schemas/question_bank.py` | ❌ New | QuestionBank schemas |
| `backend/app/schemas/exam.py` | ✏️ Modify | Add HybridExamCreate, TemplateQuestionSelection |
| `backend/app/schemas/workflow/workflow_node.py` | ✏️ Modify | Add ExamTodoConfig |

### **Backend CRUD**

| File | Status | Description |
|------|--------|-------------|
| `backend/app/crud/question_bank.py` | ❌ New | QuestionBank CRUD operations |
| `backend/app/crud/exam.py` | ✏️ Modify | Add create_hybrid_exam(), get_random_bank_questions() |

### **Backend Services**

| File | Status | Description |
|------|--------|-------------|
| `backend/app/services/exam_todo_service.py` | ❌ New | Exam TODO orchestration |
| `backend/app/services/workflow/workflow_engine.py` | ✏️ Modify | Add _create_exam_todo() |

### **Backend Endpoints**

| File | Status | Description |
|------|--------|-------------|
| `backend/app/endpoints/question_bank.py` | ❌ New | QuestionBank API |
| `backend/app/endpoints/exam.py` | ✏️ Modify | Add hybrid exam endpoint, completion hook |

### **Database Migrations**

| File | Status | Description |
|------|--------|-------------|
| `backend/alembic/versions/xxx_add_question_banks.py` | ❌ New | Create question_banks, question_bank_items tables |
| `backend/alembic/versions/xxx_add_exam_source_tracking.py` | ❌ New | Modify exam_questions table |
| `backend/alembic/versions/xxx_add_todo_exam_fields.py` | ❌ New | Modify todos, exam_assignments tables |

---

## 🔄 Implementation Order

### **Sprint 1: Question Bank Foundation (Week 1)**

#### **Day 1-2: Database & Models**
- [ ] Create QuestionBank model
- [ ] Create QuestionBankItem model
- [ ] Create Alembic migration
- [ ] Run migration on dev database
- [ ] Test model relationships

#### **Day 3-4: CRUD & Schemas**
- [ ] Create QuestionBank schemas
- [ ] Create QuestionBank CRUD operations
- [ ] Add unit tests for CRUD
- [ ] Create seed data for testing

#### **Day 5: API Endpoints**
- [ ] Create QuestionBank endpoints
- [ ] Add permission checks (system admin only for global banks)
- [ ] Test API endpoints
- [ ] Update API documentation

---

### **Sprint 2: Hybrid Exam System (Week 2)**

#### **Day 1-2: Exam Model Updates**
- [ ] Modify ExamQuestion model (add source tracking)
- [ ] Modify Exam model (add selection rules)
- [ ] Create Alembic migration
- [ ] Run migration on dev database

#### **Day 3-4: Hybrid Exam Logic**
- [ ] Create HybridExamCreate schema
- [ ] Implement create_hybrid_exam() in CRUD
- [ ] Add _get_random_bank_questions() helper
- [ ] Add unit tests

#### **Day 5: API Integration**
- [ ] Create hybrid exam endpoint
- [ ] Test hybrid exam creation
- [ ] Update API documentation

---

### **Sprint 3: TODO Workflow Integration (Week 3)**

#### **Day 1-2: TODO Model Updates**
- [ ] Add TodoType.EXAM enum
- [ ] Modify Todo model (add exam fields)
- [ ] Modify ExamAssignment model (add todo_id)
- [ ] Create Alembic migration
- [ ] Run migration on dev database

#### **Day 3-4: Exam TODO Service**
- [ ] Create ExamTodoService
- [ ] Implement create_exam_todo_from_workflow()
- [ ] Implement on_exam_completed() hook
- [ ] Add unit tests

#### **Day 5: Workflow Engine Integration**
- [ ] Modify WorkflowEngineService._execute_todo_node()
- [ ] Add _create_exam_todo() method
- [ ] Update exam completion endpoint
- [ ] Integration testing

---

### **Sprint 4: Frontend & Testing (Week 4)**

#### **Day 1-2: Frontend Components**
- [ ] Create QuestionBank management UI
- [ ] Add exam TODO configuration in workflow builder
- [ ] Create exam TODO display for candidates
- [ ] Test UI flows

#### **Day 3-4: End-to-End Testing**
- [ ] Test complete workflow: create → assign → take → complete
- [ ] Test hybrid exam creation
- [ ] Test notification emails
- [ ] Test workflow advancement

#### **Day 5: Documentation & Deployment**
- [ ] Update CLAUDE.md with new architecture
- [ ] Create user documentation
- [ ] Deploy to staging
- [ ] Final QA testing

---

## 🧪 Testing Checklist

### **Unit Tests**

- [ ] QuestionBank CRUD operations
- [ ] QuestionBankItem CRUD operations
- [ ] Hybrid exam creation
- [ ] Random question selection
- [ ] Exam TODO creation
- [ ] Exam completion hook

### **Integration Tests**

- [ ] Create workflow with exam TODO node
- [ ] Assign candidate to workflow
- [ ] Execute exam TODO node
- [ ] Candidate takes exam
- [ ] Exam completion auto-completes TODO
- [ ] Workflow advances to next node

### **API Tests**

- [ ] POST /api/question-banks
- [ ] GET /api/question-banks
- [ ] POST /api/question-banks/{id}/questions
- [ ] POST /api/exams/hybrid
- [ ] POST /api/exams/sessions/{id}/complete (with TODO hook)

### **Permission Tests**

- [ ] System admin can create global question banks
- [ ] Company admin can create company question banks
- [ ] Company admin can only see own + global banks
- [ ] Candidates can take assigned exams
- [ ] Exam completion permissions

---

## 🔐 Security Considerations

1. **Question Bank Access Control**
   - System admins: Create/edit global banks
   - Company admins: Create/edit company banks only
   - Candidates: No direct access to banks

2. **Exam Answer Validation**
   - Never expose correct answers in API responses (except in admin views)
   - Validate exam ownership before allowing edits
   - Prevent candidates from accessing other candidates' results

3. **Workflow Execution Security**
   - Verify candidate assignment before creating exam TODO
   - Validate workflow permissions
   - Prevent unauthorized workflow advancement

---

## 📊 Success Metrics

### **Functional Requirements**
- [ ] Employers can create question banks
- [ ] Employers can create hybrid exams
- [ ] Workflow creates exam TODOs automatically
- [ ] Candidates receive email notifications
- [ ] Exams auto-complete TODOs
- [ ] Workflows auto-advance after exam completion

### **Performance Requirements**
- [ ] Question bank query < 200ms
- [ ] Hybrid exam creation < 1s
- [ ] Exam TODO creation < 500ms
- [ ] Notification email sent < 5s

### **User Experience**
- [ ] Clear exam instructions in email
- [ ] Intuitive exam taking interface
- [ ] Real-time progress tracking
- [ ] Immediate feedback (if configured)

---

## 🚨 Rollback Plan

If critical issues occur:

1. **Database Rollback**
   ```bash
   # Rollback last migration
   alembic downgrade -1

   # Rollback to specific version
   alembic downgrade <revision_id>
   ```

2. **Feature Flag Disable**
   - Disable exam TODO creation in workflow engine
   - Fall back to manual exam assignment

3. **Data Preservation**
   - All existing exams remain functional
   - Existing TODOs unaffected
   - Only new exam TODO features disabled

---

## 📝 Migration Scripts

### **Create Question Banks Table**
```bash
# Generate migration
alembic revision -m "add_question_banks"

# Edit migration file
# Add create_table operations

# Run migration
alembic upgrade head
```

### **Modify Exam Questions Table**
```bash
alembic revision -m "add_exam_source_tracking"
alembic upgrade head
```

### **Modify TODO and ExamAssignment Tables**
```bash
alembic revision -m "add_todo_exam_integration"
alembic upgrade head
```

---

## 🎯 Next Steps

1. **Review this plan** with team
2. **Estimate effort** for each sprint
3. **Create Jira/GitHub issues** for each task
4. **Set up dev environment** for testing
5. **Begin Sprint 1** - Question Bank Foundation

---

## 📚 References

- **Architecture Docs**: `CLAUDE.md`
- **Existing Exam System**: `backend/app/models/exam.py`
- **Existing TODO System**: `backend/app/models/todo.py`
- **Workflow Engine**: `backend/app/services/workflow/workflow_engine.py`

---

**Document Version:** 1.0
**Last Updated:** 2025-01-10
**Author:** Claude Code Assistant
**Status:** Ready for Review
