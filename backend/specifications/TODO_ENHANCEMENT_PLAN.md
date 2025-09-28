# TODO System Enhancement Plan

## Current Implementation Analysis

### ✅ **ALREADY IMPLEMENTED FEATURES**

1. **User Creation & Basic CRUD**
   - ✅ Any user can create todos
   - ✅ Basic CRUD operations (Create, Read, Update, Delete)
   - ✅ Creator ownership model (`owner_id` field)

2. **Assignment System**
   - ✅ Creator can assign someone as assignee (`assigned_user_id`)
   - ✅ Assignee can view todos on their page
   - ✅ Permission service validates assignment rights

3. **Viewer System**
   - ✅ Creator can add users as viewers (`TodoViewer` model)
   - ✅ Viewers can see todos in their list
   - ✅ Many-to-many relationship through `todo_viewers` table

4. **Permission System**
   - ✅ Role-based access control (`TodoPermissionService`)
   - ✅ Creator-only edit/delete permissions
   - ✅ Visibility levels (PRIVATE, PUBLIC, VIEWER)

5. **Due Date & Extension System**
   - ✅ Due date can be set by creator
   - ✅ Extension request system (`TodoExtensionRequest` model)
   - ✅ 3-day advance request validation
   - ✅ Creator-only extension approval

6. **Status Management**
   - ✅ Assignee can change status to finish
   - ✅ Status-based access restrictions (completed todos are read-only)

### ❌ **MISSING FEATURES TO IMPLEMENT**

1. **Secret Memo System**
   - ❌ Creator, assignee, and viewers cannot add secret memos
   - ❌ No personal notes system per user per todo

2. **Assignee Visibility Restriction**
   - ❌ Assignee can currently see viewers (needs to be hidden)

3. **Enhanced Permission Checks**
   - ❌ After completion, assignee restrictions need reinforcement

---

## 🎯 **IMPLEMENTATION PLAN**

### **Phase 1: Secret Memo System**

#### 1.1 Database Schema Changes

**New Model: `TodoMemo`**
```sql
CREATE TABLE todo_memos (
    id INTEGER PRIMARY KEY,
    todo_id INTEGER NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memo_content TEXT NOT NULL,
    is_secret BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX(todo_id, user_id),
    UNIQUE(todo_id, user_id)  -- One memo per user per todo
);
```

#### 1.2 Backend Implementation

**Files to Create/Modify:**
1. `app/models/todo_memo.py` - New model
2. `app/schemas/todo_memo.py` - Pydantic schemas
3. `app/crud/todo_memo.py` - CRUD operations
4. `app/endpoints/todo_memos.py` - API endpoints
5. `app/services/todo_permissions.py` - Update permissions

**API Endpoints:**
- `POST /api/todos/{todo_id}/memo` - Create/update secret memo
- `GET /api/todos/{todo_id}/memo` - Get user's secret memo
- `DELETE /api/todos/{todo_id}/memo` - Delete user's secret memo

#### 1.3 Frontend Implementation

**Files to Create/Modify:**
1. `frontend/src/types/todo-memo.ts` - TypeScript types
2. `frontend/src/api/todo-memos.ts` - API client
3. `frontend/src/components/todos/TodoMemoModal.tsx` - Memo modal
4. `frontend/src/components/todos/TodoMemoSection.tsx` - Memo section in todo detail

### **Phase 2: Assignee Visibility Restriction**

#### 2.1 Backend Permission Updates

**Files to Modify:**
1. `app/services/todo_permissions.py` - Add viewer visibility rules
2. `app/endpoints/todos.py` - Filter viewer list for assignees
3. `app/schemas/todo.py` - Conditional viewer serialization

**Logic Changes:**
- When assignee requests todo details, exclude `viewers` field
- Add new permission: `can_view_viewers()`
- Only creator and viewers can see the full viewer list

#### 2.2 Frontend Permission Updates

**Files to Modify:**
1. `frontend/src/utils/todoPermissions.ts` - Add viewer visibility logic
2. `frontend/src/components/todos/TodoDetail.tsx` - Conditional viewer display
3. `frontend/src/types/todo.ts` - Update interfaces with conditional fields

### **Phase 3: Enhanced Completion Restrictions**

#### 3.1 Backend Logic Updates

**Files to Modify:**
1. `app/services/todo_permissions.py` - Strengthen completion restrictions
2. `app/endpoints/todos.py` - Add completion state validation

**Rules to Implement:**
- After completion, assignee cannot:
  - Edit any todo fields
  - Add/remove attachments
  - Request extensions
  - Change status back to pending

#### 3.2 Frontend UI Updates

**Files to Modify:**
1. `frontend/src/components/todos/TodoItem.tsx` - Disable actions for completed todos
2. `frontend/src/components/todos/TaskModal.tsx` - Read-only mode for completed todos

---

## 📋 **DETAILED IMPLEMENTATION TASKS**

### **Task 1: Todo Memo System Implementation**

#### Backend Tasks:
1. **Create Database Model** (`app/models/todo_memo.py`)
   ```python
   class TodoMemo(Base):
       __tablename__ = "todo_memos"

       id: Mapped[int] = mapped_column(Integer, primary_key=True)
       todo_id: Mapped[int] = mapped_column(Integer, ForeignKey("todos.id"), nullable=False)
       user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
       memo_content: Mapped[str] = mapped_column(Text, nullable=False)
       is_secret: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
       created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
       updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

2. **Create Pydantic Schemas** (`app/schemas/todo_memo.py`)
   ```python
   class TodoMemoCreate(BaseModel):
       memo_content: str = Field(..., max_length=2000)
       is_secret: bool = True

   class TodoMemoUpdate(BaseModel):
       memo_content: str = Field(..., max_length=2000)

   class TodoMemoRead(BaseModel):
       id: int
       todo_id: int
       user_id: int
       memo_content: str
       is_secret: bool
       created_at: datetime
       updated_at: datetime
   ```

3. **Create CRUD Operations** (`app/crud/todo_memo.py`)
4. **Create API Endpoints** (`app/endpoints/todo_memos.py`)
5. **Update Permission Service** - Add memo access validation

#### Frontend Tasks:
1. **Create TypeScript Types** (`frontend/src/types/todo-memo.ts`)
2. **Create API Client** (`frontend/src/api/todo-memos.ts`)
3. **Create Memo Components**:
   - `TodoMemoModal.tsx` - Modal for adding/editing memos
   - `TodoMemoSection.tsx` - Display memo in todo detail view
4. **Update Todo Detail Views** - Integrate memo functionality

### **Task 2: Assignee Viewer Restriction**

#### Backend Tasks:
1. **Update Permission Service** (`app/services/todo_permissions.py`)
   ```python
   @staticmethod
   async def can_view_viewers(db: AsyncSession, user_id: int, todo: Todo) -> bool:
       """Check if user can see the viewers list."""
       # Creator can always see viewers
       if todo.owner_id == user_id:
           return True

       # Viewers can see other viewers
       if await todo_viewer.is_viewer(db, todo_id=todo.id, user_id=user_id):
           return True

       # Assignee cannot see viewers
       return False
   ```

2. **Update Todo Serialization** - Conditionally include viewers based on permissions

#### Frontend Tasks:
1. **Update Permission Utils** (`frontend/src/utils/todoPermissions.ts`)
2. **Update Todo Components** - Hide viewer list from assignees

### **Task 3: Completion State Enforcement**

#### Backend Tasks:
1. **Strengthen Permission Checks** - Ensure completed todos are immutable for assignees
2. **Add Validation** - Prevent any assignee actions on completed todos

#### Frontend Tasks:
1. **Update UI Components** - Disable all assignee actions on completed todos
2. **Add Visual Indicators** - Show completion state clearly

---

## 🛣️ **MIGRATION PLAN**

### **Database Migrations**

1. **Create todo_memos table**
   ```sql
   -- Migration: add_todo_memos_table.sql
   CREATE TABLE todo_memos (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       todo_id INTEGER NOT NULL,
       user_id INTEGER NOT NULL,
       memo_content TEXT NOT NULL,
       is_secret BOOLEAN NOT NULL DEFAULT 1,
       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE CASCADE,
       FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
   );

   CREATE INDEX idx_todo_memos_todo_id ON todo_memos(todo_id);
   CREATE INDEX idx_todo_memos_user_id ON todo_memos(user_id);
   CREATE UNIQUE INDEX idx_todo_memos_todo_user ON todo_memos(todo_id, user_id);
   ```

### **Deployment Steps**

1. **Backend Deployment**
   - Run database migrations
   - Deploy new models and endpoints
   - Update permission service

2. **Frontend Deployment**
   - Update types and API clients
   - Deploy new components
   - Update existing todo components

3. **Testing**
   - Test memo functionality
   - Verify assignee restrictions
   - Test completion state enforcement

---

## 🧪 **TESTING REQUIREMENTS**

### **Backend Tests**
1. **Todo Memo Tests** (`test_todo_memos.py`)
   - CRUD operations
   - Permission validation
   - Data integrity

2. **Permission Tests** (`test_todo_permissions.py`)
   - Viewer visibility restrictions
   - Completion state enforcement
   - Access control validation

### **Frontend Tests**
1. **Component Tests**
   - Memo modal functionality
   - Conditional viewer display
   - Completion state UI

2. **Integration Tests**
   - End-to-end memo workflow
   - Permission-based UI behavior

---

## 📈 **SUCCESS CRITERIA**

### **Functional Requirements**
- ✅ Secret memos work for creator, assignee, and viewers
- ✅ Assignees cannot see viewer list
- ✅ Completed todos are immutable for assignees
- ✅ All existing functionality remains intact

### **Performance Requirements**
- ✅ Memo operations complete within 200ms
- ✅ Permission checks add minimal overhead
- ✅ UI remains responsive with new features

### **Security Requirements**
- ✅ Memos are user-private and secure
- ✅ Permission system prevents unauthorized access
- ✅ No data leakage between users

---

## 🔄 **ROLLBACK PLAN**

### **If Issues Occur**
1. **Database**: Keep migration scripts for rollback
2. **Backend**: Feature flags for new endpoints
3. **Frontend**: Progressive enhancement approach
4. **Monitoring**: Track error rates and performance

---

This plan ensures that all your requirements are met while maintaining the existing functionality and following the established architecture patterns in the MiraiWorks codebase.