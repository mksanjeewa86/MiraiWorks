# Frontend Implementation: Global Exam System

## Overview

This document outlines the frontend implementation plan for the Global Exam System. The backend is already complete, and now we need to update the frontend to support:

1. Displaying global/public exams alongside company exams
2. Cloning global/public exams
3. Visual indicators for exam types (Global/Public/Private)
4. System admin UI for creating global exams
5. Assignment workflow for global exams

## Implementation Plan

### Phase 1: Update Types and API Client
- [ ] Update TypeScript types to include `is_public` field
- [ ] Add clone exam API function
- [ ] Update exam list API to fetch global/public exams

### Phase 2: Update Exam List UI
- [ ] Add badges for Global/Public/Private exams
- [ ] Add "Clone" button for global/public exams
- [ ] Filter exams by type (All/Own/Global/Public)
- [ ] Update exam cards to show ownership

### Phase 3: Clone Exam Feature
- [ ] Create clone exam dialog/confirmation
- [ ] Handle clone API call
- [ ] Redirect to edit cloned exam
- [ ] Show success/error messages

### Phase 4: System Admin Features
- [ ] Add toggle for `is_public` when creating exam
- [ ] Add UI to indicate global exam creation (company_id = null)
- [ ] System admin exam list with all exams

### Phase 5: Assignment Flow
- [ ] Allow assigning global exams directly
- [ ] Show exam type in assignment list
- [ ] Update assignment form to support global exams

---

## Phase 1: Update Types and API Client

### Step 1.1: Update TypeScript Types

**File**: `frontend/src/types/exam.ts`

Update the `Exam` interface to include `is_public` and make `company_id` optional:

```typescript
export interface Exam {
  id: number;
  title: string;
  description: string | null;
  exam_type: string;
  status: string;
  company_id: number | null;  // ✅ Make nullable for global exams
  created_by: number | null;
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  is_public: boolean;  // ✅ NEW: Public exam flag
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string | null;
  created_at: string;
  updated_at: string;
  // Computed fields
  total_questions?: number | null;
  total_sessions?: number | null;
  completed_sessions?: number | null;
  average_score?: number | null;
}
```

Update `ExamInfo` interface:

```typescript
export interface ExamInfo {
  id: number;
  title: string;
  description: string | null;
  exam_type: string;
  status: string;
  company_id: number | null;  // ✅ Make nullable
  is_public: boolean;  // ✅ NEW
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string | null;
  created_at: string;
  total_questions: number;
}
```

Update `ExamFormData`:

```typescript
export interface ExamFormData {
  title: string;
  description: string;
  exam_type: string;
  company_id?: number | null;  // ✅ Optional for system admin
  is_public: boolean;  // ✅ NEW
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string;
}
```

### Step 1.2: Add Clone Exam API Function

**File**: `frontend/src/api/exam.ts`

Add the clone exam function:

```typescript
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { Exam, ExamInfo } from '@/types/exam';

export const examApi = {
  // ... existing functions ...

  /**
   * Clone a global or public exam to current company
   */
  async cloneExam(examId: number): Promise<ApiResponse<ExamInfo>> {
    try {
      const response = await apiClient.post<ExamInfo>(
        `/api/exams/${examId}/clone`
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        data: null,
        success: false,
        error: error.response?.data?.detail || 'Failed to clone exam',
      };
    }
  },
};
```

### Step 1.3: Update Exam List to Include Public Exams

The current `getExams` function should already work because the backend `get_by_company` now includes public exams by default. No changes needed here.

---

## Phase 2: Update Exam List UI

### Step 2.1: Create Exam Type Badge Component

**File**: `frontend/src/components/exam/ExamTypeBadge.tsx`

```typescript
import React from 'react';
import type { Exam } from '@/types/exam';

interface ExamTypeBadgeProps {
  exam: Exam;
  currentCompanyId?: number | null;
}

export function ExamTypeBadge({ exam, currentCompanyId }: ExamTypeBadgeProps) {
  // Global exam: company_id = null, is_public = true
  if (exam.company_id === null && exam.is_public) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
        🌍 Global
      </span>
    );
  }

  // Public exam from another company
  if (exam.is_public && exam.company_id !== currentCompanyId) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        🔓 Public
      </span>
    );
  }

  // Own company's public exam
  if (exam.is_public && exam.company_id === currentCompanyId) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        ✓ Public (Yours)
      </span>
    );
  }

  // Private exam
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
      🔒 Private
    </span>
  );
}
```

### Step 2.2: Create Clone Exam Dialog

**File**: `frontend/src/components/exam/CloneExamDialog.tsx`

```typescript
import React, { useState } from 'react';
import { examApi } from '@/api/exam';
import { useRouter } from 'next/navigation';
import type { Exam } from '@/types/exam';

interface CloneExamDialogProps {
  exam: Exam;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (clonedExamId: number) => void;
}

export function CloneExamDialog({
  exam,
  isOpen,
  onClose,
  onSuccess
}: CloneExamDialogProps) {
  const router = useRouter();
  const [isCloning, setIsCloning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClone = async () => {
    setIsCloning(true);
    setError(null);

    const response = await examApi.cloneExam(exam.id);

    if (response.success && response.data) {
      // Success - redirect to edit the cloned exam
      onClose();
      if (onSuccess) {
        onSuccess(response.data.id);
      } else {
        router.push(`/admin/exams/${response.data.id}/edit`);
      }
    } else {
      setError(response.error || 'Failed to clone exam');
      setIsCloning(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        {/* Overlay */}
        <div
          className="fixed inset-0 bg-black bg-opacity-30"
          onClick={onClose}
        />

        {/* Dialog */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 className="text-lg font-semibold mb-4">
            Clone Exam
          </h3>

          <p className="text-gray-600 mb-4">
            Clone "<strong>{exam.title}</strong>" to your company's exam library?
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
            <p className="text-sm text-blue-800">
              <strong>What will be cloned:</strong>
            </p>
            <ul className="text-sm text-blue-700 mt-2 space-y-1 list-disc list-inside">
              <li>All exam settings (time limit, passing score, etc.)</li>
              <li>All {exam.total_questions || 0} questions with answers</li>
            </ul>
          </div>

          <div className="bg-green-50 border border-green-200 rounded p-3 mb-4">
            <p className="text-sm text-green-800">
              <strong>After cloning, you can:</strong>
            </p>
            <ul className="text-sm text-green-700 mt-2 space-y-1 list-disc list-inside">
              <li>Edit all exam settings</li>
              <li>Add, edit, or delete questions</li>
              <li>Assign to your candidates</li>
            </ul>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={isCloning}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleClone}
              disabled={isCloning}
              className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {isCloning ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Cloning...
                </>
              ) : (
                'Clone Exam'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Step 2.3: Update Exam Card Component

**File**: `frontend/src/components/exam/ExamCard.tsx`

```typescript
import React, { useState } from 'react';
import { ExamTypeBadge } from './ExamTypeBadge';
import { CloneExamDialog } from './CloneExamDialog';
import type { Exam } from '@/types/exam';

interface ExamCardProps {
  exam: Exam;
  currentCompanyId?: number | null;
  onEdit?: (examId: number) => void;
  onDelete?: (examId: number) => void;
  onAssign?: (examId: number) => void;
  onCloneSuccess?: (clonedExamId: number) => void;
}

export function ExamCard({
  exam,
  currentCompanyId,
  onEdit,
  onDelete,
  onAssign,
  onCloneSuccess
}: ExamCardProps) {
  const [showCloneDialog, setShowCloneDialog] = useState(false);

  // Check if user can clone this exam
  const canClone = () => {
    // Can clone if:
    // 1. It's a global/public exam
    // 2. It's not our own exam
    return exam.is_public && exam.company_id !== currentCompanyId;
  };

  // Check if user can edit this exam
  const canEdit = () => {
    // Can edit if it's our company's exam
    return exam.company_id === currentCompanyId;
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {exam.title}
            </h3>
            <div className="flex items-center space-x-2">
              <ExamTypeBadge exam={exam} currentCompanyId={currentCompanyId} />
              <span className="text-sm text-gray-500">
                {exam.exam_type}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        {exam.description && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {exam.description}
          </p>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <span className="text-gray-500">Questions:</span>
            <span className="ml-2 font-medium">{exam.total_questions || 0}</span>
          </div>
          <div>
            <span className="text-gray-500">Time Limit:</span>
            <span className="ml-2 font-medium">
              {exam.time_limit_minutes ? `${exam.time_limit_minutes} min` : 'No limit'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Passing Score:</span>
            <span className="ml-2 font-medium">
              {exam.passing_score ? `${exam.passing_score}%` : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Status:</span>
            <span className="ml-2 font-medium capitalize">{exam.status}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          {canClone() && (
            <button
              onClick={() => setShowCloneDialog(true)}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
            >
              Clone
            </button>
          )}

          {canEdit() && (
            <button
              onClick={() => onEdit?.(exam.id)}
              className="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm font-medium"
            >
              Edit
            </button>
          )}

          <button
            onClick={() => onAssign?.(exam.id)}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium"
          >
            Assign
          </button>

          {canEdit() && (
            <button
              onClick={() => onDelete?.(exam.id)}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
            >
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Clone Dialog */}
      <CloneExamDialog
        exam={exam}
        isOpen={showCloneDialog}
        onClose={() => setShowCloneDialog(false)}
        onSuccess={onCloneSuccess}
      />
    </>
  );
}
```

---

## Phase 3: Update Exam List Page

**File**: `frontend/src/app/admin/exams/page.tsx`

Update the exam list page to:
1. Fetch and display global/public exams
2. Add filter tabs (All / Own / Global / Public)
3. Show exam cards with clone functionality

```typescript
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { examApi } from '@/api/exam';
import { ExamCard } from '@/components/exam/ExamCard';
import type { Exam } from '@/types/exam';

type ExamFilter = 'all' | 'own' | 'global' | 'public';

export default function ExamsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<ExamFilter>('all');

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    setLoading(true);
    const response = await examApi.getExams();
    if (response.success && response.data) {
      setExams(response.data.exams || []);
    }
    setLoading(false);
  };

  const filteredExams = exams.filter((exam) => {
    if (filter === 'all') return true;
    if (filter === 'own') return exam.company_id === user?.company_id;
    if (filter === 'global') return exam.company_id === null && exam.is_public;
    if (filter === 'public') return exam.is_public && exam.company_id !== user?.company_id;
    return true;
  });

  const handleCloneSuccess = (clonedExamId: number) => {
    // Reload exams to show the cloned exam
    loadExams();
    // Optionally redirect to edit the cloned exam
    router.push(`/admin/exams/${clonedExamId}/edit`);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-4">Exams</h1>

        {/* Filter Tabs */}
        <div className="flex space-x-2 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All Exams
          </button>
          <button
            onClick={() => setFilter('own')}
            className={`px-4 py-2 rounded ${
              filter === 'own'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            My Company
          </button>
          <button
            onClick={() => setFilter('global')}
            className={`px-4 py-2 rounded ${
              filter === 'global'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            🌍 Global
          </button>
          <button
            onClick={() => setFilter('public')}
            className={`px-4 py-2 rounded ${
              filter === 'public'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            🔓 Public
          </button>
        </div>

        {/* Create New Exam Button */}
        <button
          onClick={() => router.push('/admin/exams/create')}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          + Create New Exam
        </button>
      </div>

      {/* Exam Grid */}
      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : filteredExams.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No exams found
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredExams.map((exam) => (
            <ExamCard
              key={exam.id}
              exam={exam}
              currentCompanyId={user?.company_id}
              onEdit={(id) => router.push(`/admin/exams/${id}/edit`)}
              onAssign={(id) => router.push(`/admin/exams/${id}/assign`)}
              onCloneSuccess={handleCloneSuccess}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Phase 4: System Admin Features

### Step 4.1: Update Exam Create Form

**File**: `frontend/src/app/admin/exams/create/page.tsx`

Add checkbox for `is_public` and allow system admin to create global exams:

```typescript
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { examApi } from '@/api/exam';
import type { ExamFormData } from '@/types/exam';

export default function CreateExamPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [formData, setFormData] = useState<ExamFormData>({
    title: '',
    description: '',
    exam_type: 'custom',
    company_id: user?.company_id,
    is_public: false,  // NEW
    time_limit_minutes: 60,
    max_attempts: 1,
    passing_score: 70,
    is_randomized: false,
    allow_web_usage: true,
    monitor_web_usage: false,
    require_face_verification: false,
    face_check_interval_minutes: 5,
    show_results_immediately: true,
    show_correct_answers: false,
    show_score: true,
    instructions: '',
  });

  const isSystemAdmin = user?.roles?.some(
    (role) => role.role.name === 'SYSTEM_ADMIN'
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Call examApi.createExam(formData)
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create New Exam</h1>

      {/* Basic Info */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          Title *
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full border rounded px-3 py-2"
          required
        />
      </div>

      {/* System Admin: Global Exam Option */}
      {isSystemAdmin && (
        <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.company_id === null}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  company_id: e.target.checked ? null : user?.company_id,
                })
              }
              className="mr-2"
            />
            <span className="text-sm font-medium">
              🌍 Create as Global Exam (available to all companies)
            </span>
          </label>
        </div>
      )}

      {/* Public Exam Toggle */}
      <div className="mb-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.is_public}
            onChange={(e) =>
              setFormData({ ...formData, is_public: e.target.checked })
            }
            className="mr-2"
          />
          <span className="text-sm font-medium">
            🔓 Make this exam public (visible to other companies)
          </span>
        </label>
        <p className="text-xs text-gray-500 mt-1 ml-6">
          {formData.company_id === null
            ? 'Global exams are automatically public'
            : 'Other companies can clone and use this exam'}
        </p>
      </div>

      {/* Rest of form fields... */}

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={() => router.back()}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Create Exam
        </button>
      </div>
    </form>
  );
}
```

---

## Testing Checklist

### Backend API Testing
- [ ] Clone global exam returns correct data
- [ ] Clone sets company_id to current user's company
- [ ] Clone sets is_public to false
- [ ] Cannot clone own company's exam
- [ ] Cannot clone private exam
- [ ] All questions are copied correctly

### Frontend UI Testing
- [ ] Exam badges display correctly (Global/Public/Private)
- [ ] Clone button shows only for global/public exams
- [ ] Clone dialog shows exam details
- [ ] Clone success redirects to edit page
- [ ] Filter tabs work correctly
- [ ] System admin can create global exams
- [ ] Public toggle works correctly

### Integration Testing
- [ ] Company A can see Company B's public exam
- [ ] Company A can clone Company B's public exam
- [ ] Cloned exam appears in Company A's exam list
- [ ] Company A can edit cloned exam
- [ ] Company A cannot edit original public exam

---

## Next Steps

1. **Start with Phase 1**: Update types and API client
2. **Then Phase 2**: Update UI components
3. **Then Phase 3**: Update exam list page
4. **Finally Phase 4**: System admin features

Let's begin! 🚀
