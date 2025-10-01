# 🎙️ Interview Modal - Redesign Mockup

**Last Updated**: October 2025


## Overview
A comprehensive modal for creating and editing interviews, replacing the current full-page approach.

## Layout Structure

```
┌────────────────────────────────────────────────────────────────────────────┐
│  🎙️ Schedule Interview                                              [×]   │
│  Create a new interview session                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │                          │  │                                     │  │
│  │   INTERVIEW DETAILS      │  │   SCHEDULE & SETTINGS               │  │
│  │                          │  │                                     │  │
│  │  Interview Title *       │  │  Interview Type *                   │  │
│  │  ┌────────────────────┐  │  │  ┌────┐ ┌────┐ ┌────┐             │  │
│  │  │ Technical Interview│  │  │  │📹  │ │📞  │ │👥  │             │  │
│  │  └────────────────────┘  │  │  │Vid │ │Phn │ │In- │             │  │
│  │                          │  │  │eo  │ │one │ │Per │             │  │
│  │  Select Candidate *      │  │  └────┘ └────┘ └────┘             │  │
│  │  ┌────────────────────┐  │  │                                     │  │
│  │  │🔍 Search...    [×]│  │  │  ┌ Video Call Setup ──────────────┐ │  │
│  │  └────────────────────┘  │  │  │ ⚪ System Generated             │ │  │
│  │    ▼ Dropdown           │  │  │    Auto-create video room       │ │  │
│  │                          │  │  │                                  │ │  │
│  │  Position Title          │  │  │ ○ Custom URL                    │ │  │
│  │  ┌────────────────────┐  │  │  │   Use Zoom, Meet, etc.         │ │  │
│  │  │ Frontend Developer │  │  │  └──────────────────────────────── │ │  │
│  │  └────────────────────┘  │  │                                     │  │
│  │                          │  │  Start Time *                       │  │
│  │  Description             │  │  ┌────────────────────────┐        │  │
│  │  ┌────────────────────┐  │  │  │ 📅 2025-10-15 10:00   │        │  │
│  │  │ Assess technical   │  │  │  └────────────────────────┘        │  │
│  │  │ skills...          │  │  │                                     │  │
│  │  └────────────────────┘  │  │  End Time *                         │  │
│  │                          │  │  ┌────────────────────────┐        │  │
│  │                          │  │  │ 📅 2025-10-15 11:00   │        │  │
│  │                          │  │  └────────────────────────┘        │  │
│  │                          │  │                                     │  │
│  │                          │  │  Location / Meeting URL             │  │
│  │                          │  │  ┌────────────────────────┐        │  │
│  │                          │  │  │ (Auto-generated)       │        │  │
│  │                          │  │  └────────────────────────┘        │  │
│  │                          │  │                                     │  │
│  └──────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                            │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   ADDITIONAL NOTES (Collapsible)                            [▼]  │   │
│  │                                                                   │   │
│  │   Interview Notes                 Preparation Notes              │   │
│  │   ┌────────────────────┐          ┌────────────────────┐        │   │
│  │   │ Internal notes...  │          │ Prep materials...  │        │   │
│  │   │                    │          │                    │        │   │
│  │   └────────────────────┘          └────────────────────┘        │   │
│  │                                                                   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                    [Cancel] [Schedule]     │
└────────────────────────────────────────────────────────────────────────────┘
```

## Design Specifications

### Modal Size
- **Width**: 900px (max-w-4xl)
- **Height**: 85vh max (scrollable content)
- **Padding**: 24px all sides

### Two-Column Layout

#### Left Column: Interview Details (400px)
```
┌────────────────────────────────┐
│  INTERVIEW DETAILS             │
│                                │
│  Interview Title *             │
│  [Text Input - Full width]     │
│                                │
│  Select Candidate *            │
│  [Searchable Dropdown]         │
│  └─ Shows: Name, Email         │
│                                │
│  Position Title                │
│  [Text Input]                  │
│                                │
│  Description                   │
│  [Textarea - 4 rows]           │
│                                │
└────────────────────────────────┘
```

#### Right Column: Schedule & Settings (400px)
```
┌────────────────────────────────┐
│  SCHEDULE & SETTINGS           │
│                                │
│  Interview Type *              │
│  [📹 Video] [📞 Phone] [👥 In] │
│                                │
│  ┌─ Video Options ──────────┐ │
│  │ ⚪ System Generated       │ │
│  │ ○ Custom URL             │ │
│  └──────────────────────────┘ │
│                                │
│  Start Time *                  │
│  [DateTime Picker]             │
│                                │
│  End Time *                    │
│  [DateTime Picker]             │
│  (Auto-calculates 1hr)         │
│                                │
│  Location / Meeting URL        │
│  [Text Input]                  │
│  (Context-aware label)         │
│                                │
└────────────────────────────────┘
```

### Bottom Section: Additional Notes (Collapsible)
```
┌──────────────────────────────────────────────────┐
│  📝 ADDITIONAL NOTES              [Expand ▼]     │
├──────────────────────────────────────────────────┤
│  [When Expanded]                                 │
│                                                  │
│  Interview Notes        Preparation Notes        │
│  ┌──────────────────┐   ┌──────────────────┐   │
│  │ Internal notes   │   │ Prep materials   │   │
│  │ for interviewer  │   │ for candidate    │   │
│  │                  │   │                  │   │
│  │                  │   │                  │   │
│  └──────────────────┘   └──────────────────┘   │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Features & Behavior

### 1. Create Mode
```typescript
<InterviewModal
  isOpen={true}
  mode="create"
  onClose={() => {}}
  onSuccess={(interview) => {}}
/>
```

**Behavior**:
- Empty form fields
- Default values set:
  - Interview type: Video
  - Video call: System generated
  - Start time: 1 hour from now
  - End time: 2 hours from now
  - Timezone: User's local timezone
- Title: "Schedule Interview"
- Button: "Schedule Interview"

### 2. Edit Mode
```typescript
<InterviewModal
  isOpen={true}
  mode="edit"
  interviewId={123}
  onClose={() => {}}
  onSuccess={(interview) => {}}
/>
```

**Behavior**:
- Loads existing interview data
- All fields pre-populated
- Title: "Edit Interview"
- Button: "Save Changes"
- Shows loading state while fetching

### 3. Candidate Selection
```
┌────────────────────────────────┐
│ 🔍 Search candidates...    [×] │ ← Input with search icon
└────────────────────────────────┘
        ↓ (On focus/type)
┌────────────────────────────────┐
│ John Doe                       │ ← Dropdown results
│ john.doe@example.com           │
├────────────────────────────────┤
│ Jane Smith                     │
│ jane.smith@example.com         │
├────────────────────────────────┤
│ No candidates found            │ ← Empty state
└────────────────────────────────┘
```

**Features**:
- Real-time search (name, email)
- Shows avatar/initials
- Shows name + email
- Clear selection [×] button
- Loading state
- Empty state message

### 4. Interview Type Selector
```
┌──────┐ ┌──────┐ ┌──────┐
│  📹  │ │  📞  │ │  👥  │
│Video │ │Phone │ │In-   │
│      │ │      │ │Person│
└──────┘ └──────┘ └──────┘
  ⬆ Selected (blue border + bg)
```

**Behavior**:
- Radio button group styled as cards
- Selected: Blue border + light blue background
- Not selected: Gray border
- Hover effect on all
- Changes form fields below based on selection

### 5. Video Call Options (Only when Video selected)
```
╔═══════════════════════════════════╗
║ 📹 Video Call Configuration       ║
╠═══════════════════════════════════╣
║                                   ║
║ ⚪ System Generated                ║
║    Auto-create video call room    ║
║    ✓ Screen sharing               ║
║    ✓ Recording                    ║
║    ✓ Real-time transcription      ║
║                                   ║
║ ○ Custom URL                      ║
║   Use Zoom, Google Meet, etc.     ║
║   ┌─────────────────────────┐    ║
║   │ Meeting URL             │    ║
║   └─────────────────────────┘    ║
║                                   ║
╚═══════════════════════════════════╝
```

**Behavior**:
- Only shows when interview_type === 'video'
- System Generated:
  - Hides Meeting URL input
  - Shows feature list
  - Auto-generates URL on save
- Custom URL:
  - Shows Meeting URL input
  - Required field
  - Validates URL format

### 6. DateTime Pickers
```
Start Time *
┌──────────────────────────┐
│ 📅 2025-10-15 10:00  [▼]│ ← Click opens calendar
└──────────────────────────┘

Calendar Widget:
┌────────────────────────────┐
│ ◀ October 2025          ▶ │
│ ─────────────────────────  │
│ Su Mo Tu We Th Fr Sa       │
│     1  2  3  4  5  6       │
│  7  8  9 10 11 12 13       │
│ 14 [15]16 17 18 19 20      │
│                            │
│ Time: [10]:[00] [AM ▼]     │
│                            │
│ [Cancel]          [Select] │
└────────────────────────────┘
```

**Features**:
- react-datepicker component
- Shows date + time in one picker
- 15-minute intervals
- Default 1-hour duration
- Auto-adjusts end time when start changes
- Validates end > start

### 7. Context-Aware Location Field
```
When Video + Custom URL:
Location / Meeting URL
┌────────────────────────────┐
│ https://zoom.us/j/...      │
└────────────────────────────┘
Placeholder: "Zoom, Meet, Teams URL"

When In-Person:
Location *
┌────────────────────────────┐
│ Office Room 302            │
└────────────────────────────┘
Placeholder: "Office address or room"

When Phone:
Phone Details
┌────────────────────────────┐
│ +1 234-567-8900            │
└────────────────────────────┘
Placeholder: "Phone number or instructions"
```

### 8. Validation
```
Error States:
┌────────────────────────────┐
│ [Empty field]              │ ← Red border
└────────────────────────────┘
⚠️ Interview title is required

Required Fields:
- Interview Title *
- Candidate *
- Interview Type *
- Start Time *
- End Time *
- Location * (if in-person)
- Meeting URL * (if custom URL)

Validation Rules:
- End time must be after start time
- Valid URL format for custom meeting URL
- All required fields filled
```

## Component Structure

```typescript
interface InterviewModalProps {
  isOpen: boolean;
  mode: 'create' | 'edit';
  interviewId?: number; // Required for edit mode
  onClose: () => void;
  onSuccess: (interview: Interview) => void;
  // Optional: Pre-fill data for create mode
  defaultData?: Partial<InterviewFormData>;
}

const InterviewModal = ({
  isOpen,
  mode,
  interviewId,
  onClose,
  onSuccess,
  defaultData
}: InterviewModalProps) => {
  // State management
  const [formData, setFormData] = useState<InterviewFormData>({...});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Fetch interview data in edit mode
  useEffect(() => {
    if (mode === 'edit' && interviewId) {
      fetchInterview(interviewId);
    }
  }, [mode, interviewId]);

  // Form handlers
  const handleInputChange = (e) => {...};
  const handleCandidateSelect = (candidate) => {...};
  const validateForm = () => {...};
  const handleSubmit = async () => {...};

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
        {/* Modal content */}
      </DialogContent>
    </Dialog>
  );
};
```

## Usage Examples

### From Interview List Page
```typescript
// interviews/page.tsx
const [isModalOpen, setIsModalOpen] = useState(false);
const [editingId, setEditingId] = useState<number | null>(null);

// Create new interview
<button onClick={() => {
  setEditingId(null);
  setIsModalOpen(true);
}}>
  + New Interview
</button>

// Edit existing interview
<button onClick={() => {
  setEditingId(interview.id);
  setIsModalOpen(true);
}}>
  Edit
</button>

<InterviewModal
  isOpen={isModalOpen}
  mode={editingId ? 'edit' : 'create'}
  interviewId={editingId || undefined}
  onClose={() => {
    setIsModalOpen(false);
    setEditingId(null);
  }}
  onSuccess={(interview) => {
    loadInterviews(); // Refresh list
    setIsModalOpen(false);
  }}
/>
```

### From Workflow Editor
```typescript
// workflows/page.tsx - WorkflowEditorModal
const [isInterviewModalOpen, setIsInterviewModalOpen] = useState(false);
const [editingStep, setEditingStep] = useState<LinearWorkflowStep | null>(null);

// Add new interview step
const addInterviewStep = () => {
  setEditingStep(null);
  setIsInterviewModalOpen(true);
};

// Edit existing interview step
const editInterviewStep = (step: LinearWorkflowStep) => {
  setEditingStep(step);
  setIsInterviewModalOpen(true);
};

<InterviewModal
  isOpen={isInterviewModalOpen}
  mode={editingStep ? 'edit' : 'create'}
  interviewId={editingStep?.interview_id}
  onClose={() => {
    setIsInterviewModalOpen(false);
    setEditingStep(null);
  }}
  onSuccess={(interview) => {
    if (editingStep) {
      // Update step with interview data
      updateStep(editingStep.id, {
        title: interview.title,
        description: interview.description,
        interview_id: interview.id,
        config: {
          duration: calculateDuration(interview.scheduled_start, interview.scheduled_end),
          interview_type: interview.interview_type,
          location: interview.location || interview.meeting_url
        }
      });
    } else {
      // Add new step
      addStepFromInterview(interview);
    }
    setIsInterviewModalOpen(false);
  }}
/>
```

## Responsive Design

### Desktop (>768px)
- Two-column layout
- Side-by-side fields
- 900px modal width

### Tablet (768px - 1024px)
- Two-column maintained
- Slightly smaller width (750px)
- Adjusted spacing

### Mobile (<768px)
- Single column layout
- Stack all fields vertically
- Full-width modal (95vw)
- Adjusted button layout

## Benefits

✅ **Consistent UX**: Same modal for create & edit
✅ **Context Maintained**: Stay on current page
✅ **Faster Workflow**: No page navigation
✅ **Reusable**: Works in interviews page & workflow editor
✅ **Better Organization**: Two-column layout, logical grouping
✅ **Smart Defaults**: Auto-fills sensible values
✅ **Validation**: Real-time error feedback
✅ **Responsive**: Works on all screen sizes

---

**Ready to implement this design?** 🚀
