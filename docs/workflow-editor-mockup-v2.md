# 🎨 Workflow Editor Modal - Redesign Mockup V2

**Last Updated**: October 2025


## Key Changes
- ❌ **Removed**: Step Properties/Details panel (use existing interview/todo modals instead)
- ✅ **Added**: More space for workflow configuration
- ✅ **Better**: Organized workflow settings and assignments

## Layout Structure

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  🔀 Workflow Editor                                                          [×]   │
│  Create step-by-step hiring processes with interviews and tasks                   │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  ┌─────────────────────────┐  ┌──────────────────────────────────────────────┐  │
│  │                         │  │                                              │  │
│  │   WORKFLOW STEPS        │  │        WORKFLOW CONFIGURATION                │  │
│  │   (Always Visible)      │  │                                              │  │
│  │                         │  │  ╔════════════════════════════════════════╗ │  │
│  │ ┌─────────────────────┐ │  │  ║  📋 BASIC INFORMATION                 ║ │  │
│  │ │ + Interview         │ │  │  ║                                        ║ │  │
│  │ │   Add Interview     │ │  │  ║  Workflow Name                         ║ │  │
│  │ │                     │ │  │  ║  ┌──────────────────────────────────┐ ║ │  │
│  │ │ + Todo              │ │  │  ║  │ Software Engineer Hiring         │ ║ │  │
│  │ │   Add Todo          │ │  │  ║  └──────────────────────────────────┘ ║ │  │
│  │ └─────────────────────┘ │  │  ║                                        ║ │  │
│  │                         │  │  ║  Description                           ║ │  │
│  │ ═══ WORKFLOW STEPS ═══  │  │  ║  ┌──────────────────────────────────┐ ║ │  │
│  │                         │  │  ║  │ Complete hiring process for      │ ║ │  │
│  │ [1] 🎙️ Technical...    │  │  ║  │ software engineering positions   │ ║ │  │
│  │     Interview           │  │  ║  └──────────────────────────────────┘ ║ │  │
│  │     Duration: 60min     │  │  ║                                        ║ │  │
│  │     [Edit] [×]          │  │  ║  Status: [Draft ▼]                     ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │ [2] 📋 Coding Test      │  │  ╚════════════════════════════════════════╝ │  │
│  │     Todo Assignment     │  │                                              │  │
│  │     Priority: High      │  │  ╔════════════════════════════════════════╗ │  │
│  │     [Edit] [×]          │  │  ║  👥 CANDIDATE ASSIGNMENT              ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │ [3] 🎙️ HR Interview    │  │  ║  Assign candidates to workflow         ║ │  │
│  │     Interview           │  │  ║  ┌────────────────────┐  [+ Assign]   ║ │  │
│  │     Duration: 45min     │  │  ║  │ Search candidates  │               ║ │  │
│  │     [Edit] [×]          │  │  ║  └────────────────────┘               ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │ [4] 🎙️ Final...        │  │  ║  Assigned (0)                          ║ │  │
│  │     Interview           │  │  ║  ┌──────────────────────────────────┐ ║ │  │
│  │     Duration: 30min     │  │  ║  │ No candidates assigned yet       │ ║ │  │
│  │     [Edit] [×]          │  │  ║  └──────────────────────────────────┘ ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │ Drag to reorder ⇅       │  │  ╚════════════════════════════════════════╝ │  │
│  │                         │  │                                              │  │
│  │                         │  │  ╔════════════════════════════════════════╗ │  │
│  │                         │  │  ║  👁️ WORKFLOW VIEWERS                  ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │                         │  │  ║  Add reviewers and managers            ║ │  │
│  │                         │  │  ║  ┌────────────┐ [Viewer▼] [+ Add]    ║ │  │
│  │                         │  │  ║  │ User ID    │                       ║ │  │
│  │                         │  │  ║  └────────────┘                       ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │                         │  │  ║  Viewers (0)                           ║ │  │
│  │                         │  │  ║  ┌──────────────────────────────────┐ ║ │  │
│  │                         │  │  ║  │ No viewers assigned yet          │ ║ │  │
│  │                         │  │  ║  └──────────────────────────────────┘ ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │                         │  │  ╚════════════════════════════════════════╝ │  │
│  │                         │  │                                              │  │
│  │                         │  │  ╔════════════════════════════════════════╗ │  │
│  │                         │  │  ║  ⚙️ WORKFLOW SETTINGS                 ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │                         │  │  ║  Automation                            ║ │  │
│  │                         │  │  ║  ☑ Auto-create interviews & todos      ║ │  │
│  │                         │  │  ║  ☐ Auto-advance on completion          ║ │  │
│  │                         │  │  ║  ☐ Send notifications to candidates    ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │                         │  │  ║  Template Options                      ║ │  │
│  │                         │  │  ║  ☐ Save as template                    ║ │  │
│  │                         │  │  ║  ☐ Make public                         ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │                         │  │  ╚════════════════════════════════════════╝ │  │
│  │                         │  │                                              │  │
│  └─────────────────────────┘  └──────────────────────────────────────────────┘  │
│                                                                                    │
├────────────────────────────────────────────────────────────────────────────────────┤
│  📊 3 steps • 2 interviews • 1 todo                    [Cancel]  [Save Workflow]  │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 How It Works

### Left Panel: Workflow Steps (320px fixed)
```
┌─────────────────────────┐
│ + Interview             │ ← Click to add new interview
│   Add Interview         │
│                         │
│ + Todo                  │ ← Click to add new todo
│   Add Todo              │
├─────────────────────────┤
│ ═══ WORKFLOW STEPS ═══  │
│                         │
│ [1] 🎙️ Technical       │
│     Interview           │
│     Duration: 60min     │
│     [Edit] [×]          │ ← Edit opens interview modal
│                         │
│ [2] 📋 Coding Test      │
│     Todo Assignment     │
│     Priority: High      │
│     [Edit] [×]          │ ← Edit opens todo modal
│                         │
│ [3] 🎙️ HR Interview    │
│     Interview           │
│     Duration: 45min     │
│     [Edit] [×]          │
│                         │
│ Drag to reorder ⇅       │
└─────────────────────────┘
```

### Right Panel: Workflow Configuration (Flexible width)
```
┌──────────────────────────────────────┐
│  📋 BASIC INFORMATION                │
│                                      │
│  Workflow Name                       │
│  ┌────────────────────────────────┐ │
│  │ Software Engineer Hiring       │ │
│  └────────────────────────────────┘ │
│                                      │
│  Description                         │
│  ┌────────────────────────────────┐ │
│  │ Complete hiring process...     │ │
│  │                                │ │
│  └────────────────────────────────┘ │
│                                      │
│  Status: [Draft ▼]                   │
│                                      │
├──────────────────────────────────────┤
│  👥 CANDIDATE ASSIGNMENT             │
│                                      │
│  Assign candidates to workflow       │
│  ┌──────────────────┐  [+ Assign]   │
│  │ Search candidates│               │
│  └──────────────────┘               │
│                                      │
│  Assigned Candidates (0)             │
│  ┌────────────────────────────────┐ │
│  │ No candidates assigned yet     │ │
│  └────────────────────────────────┘ │
│                                      │
├──────────────────────────────────────┤
│  👁️ WORKFLOW VIEWERS                 │
│                                      │
│  Add reviewers and managers          │
│  ┌────────────┐ [Viewer▼] [+ Add]   │
│  │ User ID    │                     │
│  └────────────┘                     │
│                                      │
│  Assigned Viewers (0)                │
│  ┌────────────────────────────────┐ │
│  │ No viewers assigned yet        │ │
│  └────────────────────────────────┘ │
│                                      │
├──────────────────────────────────────┤
│  ⚙️ WORKFLOW SETTINGS                │
│                                      │
│  Automation                          │
│  ☑ Auto-create interviews & todos    │
│  ☐ Auto-advance on completion        │
│  ☐ Send notifications                │
│                                      │
│  Template Options                    │
│  ☐ Save as template                  │
│  ☐ Make public                       │
│                                      │
└──────────────────────────────────────┘
```

## 🔄 Step Editing Flow

### When user clicks "Edit" on a step:

#### For Interview Steps:
```
[Edit] → Opens existing InterviewEditModal
       → User edits in full interview modal
       → On save, updates step in workflow
       → Modal closes, back to workflow editor
```

#### For Todo Steps:
```
[Edit] → Opens existing TodoEditModal
       → User edits in full todo modal
       → On save, updates step in workflow
       → Modal closes, back to workflow editor
```

### When user clicks "+ Interview" or "+ Todo":
```
[+ Interview] → Creates new step with defaults
              → Opens InterviewEditModal (create mode)
              → User fills in details
              → On save, adds to workflow steps
              → Modal closes

[+ Todo] → Creates new step with defaults
         → Opens TodoEditModal (create mode)
         → User fills in details
         → On save, adds to workflow steps
         → Modal closes
```

## 📋 Right Panel Sections (All in one scrollable area)

### Section 1: Basic Information
- **Workflow Name**: Text input
- **Description**: Textarea
- **Status**: Dropdown (Draft/Active/Inactive)
- **Created/Updated**: Read-only dates

### Section 2: Candidate Assignment
- **Search/Add**: Input with "+ Assign" button
- **Assigned List**: Cards showing assigned candidates
  - Candidate name, email
  - Remove button [×]
  - Status indicator
- **Bulk Actions**: Assign multiple at once

### Section 3: Workflow Viewers
- **Add Viewer**: Input + Role dropdown + "+ Add" button
  - Roles: Viewer, Reviewer, Manager
- **Viewer List**: Cards showing viewers
  - User name, role badge
  - Remove button [×]
  - Permission indicator

### Section 4: Workflow Settings
- **Automation Options**:
  - ☑ Auto-create interviews & todos
  - ☐ Auto-advance on completion
  - ☐ Send notifications to candidates
  - ☐ Send reminders before deadlines

- **Template Options**:
  - ☐ Save as template
  - ☐ Make template public
  - Template category dropdown

## 🎨 Visual Design

### Step Cards (Left Panel)
```
┌─────────────────────────────────┐
│ [1] 🎙️ Technical Interview     │
│     Interview • 60 minutes      │
│     [Edit]           [×]        │
└─────────────────────────────────┘
  ↓ Can drag to reorder

┌─────────────────────────────────┐
│ [2] 📋 Coding Challenge         │
│     Assignment • High Priority  │
│     [Edit]           [×]        │
└─────────────────────────────────┘
```

### Section Cards (Right Panel)
```
╔═════════════════════════════════╗
║  📋 BASIC INFORMATION           ║
║                                 ║
║  Content here...                ║
║                                 ║
╚═════════════════════════════════╝
  ↓ Gap
╔═════════════════════════════════╗
║  👥 CANDIDATE ASSIGNMENT        ║
║                                 ║
║  Content here...                ║
║                                 ║
╚═════════════════════════════════╝
```

### Footer Summary Bar
```
┌─────────────────────────────────────────────────────────┐
│ 📊 3 steps • 2 interviews • 1 todo  [Cancel] [Save]     │
└─────────────────────────────────────────────────────────┘
```

## ✨ Key Benefits

### ✅ Uses Existing Modals
- No duplicate step editing UI
- Consistent with interview/todo pages
- Reuses existing validation and logic
- Users familiar with interface

### ✅ More Space for Configuration
- All workflow settings visible at once
- No tab switching needed
- Better overview of entire workflow
- Clearer organization

### ✅ Simple Workflow
1. Add basic info (name, description)
2. Add steps (opens modals for editing)
3. Assign candidates and viewers
4. Configure settings
5. Save workflow

### ✅ Clean Left Panel
- Pure step list, always visible
- Drag-and-drop reordering
- Quick edit/delete actions
- Visual step indicators

### ✅ Organized Right Panel
- Grouped by concern
- Scrollable single column
- Clear section headers
- Logical flow top-to-bottom

## 🔧 Technical Implementation

### Modal Communication
```typescript
// When user clicks Edit on interview step
const handleEditInterviewStep = (step: LinearWorkflowStep) => {
  setEditingInterview({
    id: step.interview_id,
    title: step.title,
    description: step.description,
    duration: step.config.duration,
    // ... other fields
  });
  setIsInterviewModalOpen(true);
};

// When interview modal saves
const handleInterviewSave = (updatedInterview: Interview) => {
  // Update the step in workflow
  updateStep(selectedStep.id, {
    title: updatedInterview.title,
    description: updatedInterview.description,
    config: {
      duration: updatedInterview.duration,
      interview_type: updatedInterview.interview_type,
      location: updatedInterview.location,
    }
  });
  setIsInterviewModalOpen(false);
};
```

## 📱 Responsive Layout

### Desktop (>1024px)
- Left Panel: 320px fixed
- Right Panel: Flexible (600px+ available)
- Modal: 90vh height

### Tablet (768px - 1024px)
- Left Panel: 280px fixed
- Right Panel: Flexible
- Smaller cards and inputs

### Mobile (<768px)
- Stack vertically
- Left panel collapsible
- Full-width sections
- Touch-friendly drag handles

## 🎯 Summary

**This design:**
- ✅ Keeps workflow steps always visible on left
- ✅ Uses existing interview/todo modals (no duplicate UI)
- ✅ Better organizes all workflow configuration
- ✅ More space for assignments and settings
- ✅ Simpler, cleaner interface
- ✅ Consistent with rest of application

**Ready to implement?** 🚀
