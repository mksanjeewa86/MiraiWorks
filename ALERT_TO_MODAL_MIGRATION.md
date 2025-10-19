# Alert to Modal Migration Plan

## Executive Summary

**Total Alerts**: 58 alerts across 15 files
**Recommendation**: **Hybrid Approach** - Common modal component + specialized modals for complex cases

## Analysis

### Alert Distribution by Type

1. **Success Messages** (~20 alerts)
   - "copied to clipboard"
   - "updated successfully"
   - "created successfully"

2. **Error Messages** (~25 alerts)
   - "failed to load"
   - "failed to update"
   - "failed to delete"

3. **Validation/Warning** (~10 alerts)
   - "please fill in required fields"
   - "file size must be less than X"
   - "must be public to share"

4. **Info Messages** (~3 alerts)
   - "download functionality not available"
   - "thank you messages"

### Files with Most Alerts

1. `workflows/page.tsx` - 13 alerts
2. `resumes/[id]/edit/page.tsx` - 6 alerts
3. `resumes/page.tsx` - 8 alerts
4. `resumes/[id]/preview/page.tsx` - 8 alerts
5. `resumes/create/page.tsx` - 4 alerts
6. Others - 19 alerts (1-4 per file)

## Recommendation: Hybrid Approach

### Why Hybrid?

**✅ Advantages:**
- **Consistency** for simple notifications (toast/snackbar style)
- **Flexibility** for complex interactions (confirmations, forms)
- **Better UX** - right tool for the right job
- **Easier migration** - incremental approach

**❌ Why not 100% common component?**
- Some alerts need actions (confirm/cancel)
- Some need custom content (forms, lists)
- Would force awkward props/configuration

**❌ Why not 58 separate modals?**
- Massive code duplication
- Inconsistent styling
- Hard to maintain
- Overkill for simple messages

### Solution Architecture

```
Common Components:
├── Toast/Snackbar (90% of alerts) → Simple notifications
│   ├── Success
│   ├── Error
│   ├── Warning
│   └── Info
│
└── Specialized Modals (10% of alerts) → Complex interactions
    ├── ConfirmDialog (delete confirmations)
    ├── FormModal (multi-step interactions)
    └── ValidationModal (detailed validation errors)
```

## Migration Strategy

### Phase 1: Setup Toast System (Week 1)

**Priority: HIGH**

1. **Install Toast Library**
   ```bash
   npm install react-hot-toast
   # OR
   npm install sonner
   ```

2. **Create Toast Context** (`src/contexts/ToastContext.tsx`)
   ```typescript
   interface ToastContextType {
     success: (message: string) => void;
     error: (message: string) => void;
     warning: (message: string) => void;
     info: (message: string) => void;
   }
   ```

3. **Integrate with App** (`src/app/layout.tsx`)

**Deliverable**: Working toast system ready for migration

### Phase 2: Migrate Simple Alerts (Week 2-3)

**Priority: HIGH**

Convert 90% of alerts (52 alerts) to toast notifications:

#### 2.1 Success Messages (20 alerts)
- ✅ "copied to clipboard" → `toast.success()`
- ✅ "updated successfully" → `toast.success()`
- ✅ "created successfully" → `toast.success()`

**Files**:
- `public/resume/[slug]/page.tsx` (3 alerts)
- `workflows/page.tsx` (2 alerts)
- `admin/connections/page.tsx` (2 alerts)
- `resumes/` (multiple files, 13 alerts)

#### 2.2 Error Messages (25 alerts)
- ❌ "failed to load" → `toast.error()`
- ❌ "failed to update" → `toast.error()`
- ❌ "failed to delete" → `toast.error()`

**Files**:
- `workflows/page.tsx` (9 alerts)
- `resumes/` (multiple files, 10 alerts)
- `admin/connections/page.tsx` (3 alerts)
- Others (3 alerts)

#### 2.3 Warning/Info Messages (7 alerts)
- ⚠️ "must be public to share" → `toast.warning()`
- ℹ️ "thank you message" → `toast.info()`

**Files**:
- `resumes/page.tsx` (1 alert)
- `employer/contact/page.tsx` (1 alert)
- `recruiter/contact/page.tsx` (1 alert)
- Others (4 alerts)

**Deliverable**: 52 alerts converted to toast

### Phase 3: Create Specialized Modals (Week 4)

**Priority: MEDIUM**

Convert remaining 10% of alerts (6 alerts) that need user interaction:

#### 3.1 Validation Modal
**Use case**: Multiple validation errors with details

**Target alerts** (3 alerts):
- `resumes/[id]/edit/page.tsx:121` - "Please fill in required fields: Title and Full Name"
- `resumes/create/page.tsx:231` - "Please fill in required fields: Title, Last Name, and First Name"
- `admin/exams/create/exam-question-form.tsx` (3 validation alerts)

**Component**: `src/components/ui/ValidationModal.tsx`
```typescript
interface ValidationModalProps {
  isOpen: boolean;
  onClose: () => void;
  errors: string[];
  title?: string;
}
```

#### 3.2 Confirm Dialog
**Use case**: Require user confirmation before action

**Target alerts** (None currently, but recommended for):
- Delete operations (currently no confirmation!)
- Status changes in workflows
- Making resumes public/private

**Component**: `src/components/ui/ConfirmDialog.tsx`
```typescript
interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  variant?: 'danger' | 'warning' | 'info';
}
```

**Deliverable**: 6 complex alerts converted + new confirmation flows

## Migration Checklist

### Setup Phase
- [ ] Choose toast library (recommend: `sonner` for modern Next.js)
- [ ] Install dependencies
- [ ] Create `ToastContext.tsx`
- [ ] Create `useToast()` hook
- [ ] Integrate with app layout
- [ ] Setup i18n for toast messages

### Migration Phase (By File)

#### High Priority (Most alerts)
- [ ] `workflows/page.tsx` (13 alerts)
  - [ ] Lines 251, 255 (status change)
  - [ ] Lines 272, 276 (archive)
  - [ ] Lines 311, 1035, 1051, 1084, 1110 (create/load errors)
  - [ ] Lines 1333, 1336 (success messages)

- [ ] `resumes/page.tsx` (8 alerts)
  - [ ] Line 125 (delete error)
  - [ ] Lines 132, 152, 155 (PDF download)
  - [ ] Lines 166, 170 (visibility toggle)
  - [ ] Lines 176, 184, 194 (share link)

- [ ] `resumes/[id]/preview/page.tsx` (8 alerts)
  - [ ] Line 113 (load error)
  - [ ] Lines 134, 154, 157 (PDF download)
  - [ ] Line 184 (make public error)
  - [ ] Lines 197, 207 (share link)

- [ ] `resumes/[id]/edit/page.tsx` (6 alerts)
  - [ ] Line 58 (load error)
  - [ ] Lines 85, 90 (photo validation)
  - [ ] Line 121 (required fields - **use ValidationModal**)
  - [ ] Lines 140, 144 (update success/error)

- [ ] `resumes/create/page.tsx` (4 alerts)
  - [ ] Lines 79, 84 (photo validation)
  - [ ] Line 231 (required fields - **use ValidationModal**)
  - [ ] Line 324 (create error)

#### Medium Priority
- [ ] `public/resume/[slug]/page.tsx` (4 alerts)
- [ ] `admin/connections/page.tsx` (4 alerts)
- [ ] `candidates/page.tsx` (1 alert)
- [ ] `resumes/preview/page.tsx` (2 alerts)

#### Low Priority
- [ ] `employer/contact/page.tsx` (1 alert)
- [ ] `recruiter/contact/page.tsx` (1 alert)
- [ ] `admin/exams/create/exam-question-form.tsx` (3 alerts - **use ValidationModal**)
- [ ] `mbti/MBTITestButton.tsx` (1 alert)
- [ ] `ui/ImageCropModal.tsx` (1 alert)
- [ ] `profile/SectionPrivacyToggle.tsx` (1 alert)

### Specialized Modals
- [ ] Create `ValidationModal.tsx`
- [ ] Create `ConfirmDialog.tsx`
- [ ] Migrate 3 validation alerts to `ValidationModal`
- [ ] Add confirmations for delete operations (new feature!)

### Testing Phase
- [ ] Test all success toasts
- [ ] Test all error toasts
- [ ] Test all warning toasts
- [ ] Test ValidationModal with multiple errors
- [ ] Test ConfirmDialog for delete operations
- [ ] Test i18n for all messages
- [ ] Test accessibility (keyboard navigation, screen readers)

### Cleanup Phase
- [ ] Remove all `alert()` calls
- [ ] Update i18n files (move alert messages to toast keys)
- [ ] Document toast usage in README
- [ ] Add toast examples to component library (if you have one)

## Implementation Details

### Toast System Setup

**Option 1: Sonner (Recommended for Next.js)**
```typescript
// src/contexts/ToastContext.tsx
import { toast, Toaster } from 'sonner';

export const ToastProvider = ({ children }: { children: ReactNode }) => (
  <>
    <Toaster position="top-right" />
    {children}
  </>
);

export const useToast = () => ({
  success: (message: string) => toast.success(message),
  error: (message: string) => toast.error(message),
  warning: (message: string) => toast.warning(message),
  info: (message: string) => toast.info(message),
});
```

**Option 2: React Hot Toast**
```typescript
// Similar setup, slightly different API
import toast, { Toaster } from 'react-hot-toast';
```

### Migration Example

**Before:**
```typescript
try {
  await updateResume(id, data);
  alert('Resume updated successfully!');
} catch (error) {
  alert('Failed to update resume. Please try again.');
}
```

**After:**
```typescript
const { success, error } = useToast();

try {
  await updateResume(id, data);
  success('Resume updated successfully!');
} catch (err) {
  error('Failed to update resume. Please try again.');
}
```

### i18n Integration

```typescript
// Update i18n files
// en/common.json
{
  "toast": {
    "success": {
      "resumeUpdated": "Resume updated successfully!",
      "copiedToClipboard": "Copied to clipboard!"
    },
    "error": {
      "resumeUpdateFailed": "Failed to update resume. Please try again.",
      "loadFailed": "Failed to load data. Please try again."
    }
  }
}

// Usage
const { t } = useTranslation('common');
success(t('toast.success.resumeUpdated'));
```

## Benefits of This Approach

### User Experience
- ✅ **Non-blocking**: Toasts don't interrupt workflow
- ✅ **Better positioning**: Toasts in corner, modals centered
- ✅ **Auto-dismiss**: Success messages disappear automatically
- ✅ **Stackable**: Multiple notifications visible
- ✅ **Modern**: Industry standard pattern

### Developer Experience
- ✅ **Simple API**: `toast.success()` vs creating modal components
- ✅ **Type-safe**: TypeScript support
- ✅ **i18n ready**: Easy to integrate with existing translations
- ✅ **Consistent**: Single source of truth for notifications
- ✅ **Maintainable**: One component to update styling

### Performance
- ✅ **Lightweight**: Toast libraries are small (~5-10KB)
- ✅ **Optimized**: Built for React rendering performance
- ✅ **No re-renders**: Context-based, minimal re-renders

## Timeline

- **Week 1**: Setup toast system (3-5 hours)
- **Week 2-3**: Migrate simple alerts (10-15 hours)
- **Week 4**: Create specialized modals (5-8 hours)
- **Total**: ~20-30 hours

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking i18n | HIGH | Test all locales, keep fallback messages |
| Missing edge cases | MEDIUM | Thorough testing checklist |
| User confusion | LOW | Toast messages clear and actionable |
| Library incompatibility | LOW | Use proven libraries (sonner/react-hot-toast) |

## Recommended Next Steps

1. **Decision**: Choose toast library (sonner or react-hot-toast)
2. **Proof of Concept**: Setup toast system for 1 file (e.g., `resumes/page.tsx`)
3. **Validate**: Ensure UX/UI meets requirements
4. **Scale**: Follow migration checklist file-by-file
5. **Review**: PR review after each file or batch of files

## Appendix: Library Comparison

| Feature | Sonner | React Hot Toast |
|---------|--------|-----------------|
| Size | 5KB | 8KB |
| Next.js Support | Excellent | Good |
| Customization | High | Very High |
| TypeScript | ✅ | ✅ |
| Accessibility | ✅ | ✅ |
| Popularity | Growing | Established |
| Recommendation | ⭐ Best for new Next.js | Proven, feature-rich |

## Questions?

Contact the development team or open an issue in the project repository.

---
*Last updated: January 2025*
