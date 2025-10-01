# 🎨 Workflow Editor Modal - Redesign Mockup

**Last Updated**: October 2025


## Layout Structure

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  🔀 Workflow Editor                                                          [×]   │
│  Create step-by-step hiring processes with interviews and tasks                   │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  ┌─────────────────────────┐  ┌──────────────────────────────────────────────┐  │
│  │                         │  │  [Overview] [Assignments] [Settings]         │  │
│  │   WORKFLOW STEPS        │  │                                              │  │
│  │   (Always Visible)      │  │  ╔════════════════════════════════════════╗ │  │
│  │                         │  │  ║                                        ║ │  │
│  │ ┌─────────────────────┐ │  │  ║  TAB CONTENT AREA                     ║ │  │
│  │ │ + Interview         │ │  │  ║                                        ║ │  │
│  │ │   Add Interview     │ │  │  ║  Overview: Basic workflow info         ║ │  │
│  │ │                     │ │  │  ║  • Workflow Name                       ║ │  │
│  │ │ + Todo              │ │  │  ║  • Description                         ║ │  │
│  │ │   Add Todo          │ │  │  ║  • Status                              ║ │  │
│  │ └─────────────────────┘ │  │  ║  • Statistics                          ║ │  │
│  │                         │  │  ║                                        ║ │  │
│  │ ═══ WORKFLOW STEPS ═══  │  │  ║  Assignments: Manage candidates        ║ │  │
│  │                         │  │  ║  • Assign Candidates                   ║ │  │
│  │ [1] 🎙️ Technical...    │◄─┼──┼──║  • Add Viewers/Reviewers              ║ │  │
│  │     Interview           │  │  ║  • Permission Management               ║ │  │
│  │     Duration: 60min     │  │  ║                                        ║ │  │
│  │     [Edit] [Delete]     │  │  ║  Settings: Advanced options            ║ │  │
│  │                         │  │  ║  • Auto-advance settings               ║ │  │
│  │ [2] 📋 Coding Test      │  │  ║  • Notification preferences            ║ │  │
│  │     Todo Assignment     │  │  ║  • Integration options                 ║ │  │
│  │     Priority: High      │  │  ║  • Template settings                   ║ │  │
│  │     [Edit] [Delete]     │  │  ║                                        ║ │  │
│  │                         │  │  ╚════════════════════════════════════════╝ │  │
│  │ [3] 🎙️ HR Interview    │  │                                              │  │
│  │     Interview           │  │  ┌────────────────────────────────────────┐ │  │
│  │     Duration: 45min     │  │  │  STEP DETAILS (When step selected)     │ │  │
│  │     [Edit] [Delete]     │  │  │                                        │ │  │
│  │                         │  │  │  Selected: Technical Interview         │ │  │
│  │ Drag to reorder ⇅       │  │  │                                        │ │  │
│  │                         │  │  │  ┌─ Title ─────────────────────────┐  │ │  │
│  │                         │  │  │  │ Technical Interview            │  │ │  │
│  │                         │  │  │  └─────────────────────────────────┘  │ │  │
│  │                         │  │  │                                        │ │  │
│  │                         │  │  │  ┌─ Description ────────────────────┐ │ │  │
│  │                         │  │  │  │ Deep dive into technical skills  │ │ │  │
│  │                         │  │  │  │ and problem-solving abilities   │ │ │  │
│  │                         │  │  │  └─────────────────────────────────┘ │ │  │
│  │                         │  │  │                                        │ │  │
│  │                         │  │  │  Interview Settings                    │ │  │
│  │                         │  │  │  Duration: [60] minutes                │ │  │
│  │                         │  │  │  Type: [Video ▼]                       │ │  │
│  │                         │  │  │  Location: [Video Call]                │ │  │
│  │                         │  │  │                                        │ │  │
│  │                         │  │  │  [Update Step]                         │ │  │
│  │                         │  │  └────────────────────────────────────────┘ │  │
│  └─────────────────────────┘  └──────────────────────────────────────────────┘  │
│                                                                                    │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                    [Cancel]  [Save Workflow]       │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### Left Panel: Workflow Steps (Always Visible)
- **Fixed Width**: 320px
- **Scrollable**: When many steps
- **Quick Actions**:
  - ➕ Add Interview / Add Todo buttons at top
  - 🎙️ Interview steps with blue icon
  - 📋 Todo steps with green icon
- **Drag & Drop**: Reorder steps by dragging
- **Step Cards**: Show key info (title, type, duration/priority)
- **Quick Actions**: Edit/Delete buttons on each step

### Right Panel: Tabbed Content (Flexible)
- **Three Tabs**: Overview | Assignments | Settings
- **Context-Aware**: Step Details panel appears when step selected
- **Responsive**: Takes remaining space

### Tab 1: Overview
```
┌─────────────────────────────────────────┐
│  📋 WORKFLOW INFORMATION                │
│                                         │
│  Workflow Name                          │
│  ┌─────────────────────────────────┐   │
│  │ Software Engineer Hiring        │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Description                            │
│  ┌─────────────────────────────────┐   │
│  │ Complete hiring process for     │   │
│  │ software engineering positions  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Status: [Draft ▼]                      │
│  Created: Jan 15, 2025                  │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  📊 WORKFLOW STATISTICS                 │
│                                         │
│  • Total Steps: 3                       │
│  • Interviews: 2                        │
│  • Todos: 1                             │
│  • Estimated Duration: ~2 weeks         │
│                                         │
└─────────────────────────────────────────┘
```

### Tab 2: Assignments
```
┌─────────────────────────────────────────┐
│  👥 CANDIDATE ASSIGNMENT                │
│                                         │
│  Assign candidates to this workflow     │
│  ┌──────────────────┐  [+ Add]         │
│  │ Search candidates│                   │
│  └──────────────────┘                   │
│                                         │
│  Assigned Candidates (0)                │
│  ┌─────────────────────────────────┐   │
│  │ No candidates assigned yet      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  👁️ WORKFLOW VIEWERS                    │
│                                         │
│  Add viewers and reviewers              │
│  ┌──────────────────┐  [Viewer ▼]      │
│  │ Enter user ID    │  [+ Add]         │
│  └──────────────────┘                   │
│                                         │
│  Roles:                                 │
│  • Viewer: Can view workflow            │
│  • Reviewer: Can review & comment       │
│  • Manager: Full management access      │
│                                         │
│  Assigned Viewers (0)                   │
│  ┌─────────────────────────────────┐   │
│  │ No viewers assigned yet         │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Tab 3: Settings
```
┌─────────────────────────────────────────┐
│  ⚙️ WORKFLOW SETTINGS                   │
│                                         │
│  🔄 Automation                          │
│  ☐ Auto-advance on completion           │
│  ☐ Send notifications to candidates     │
│  ☐ Send reminders 24h before deadlines  │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  🔗 Integration Options                 │
│  ☑ Create real interviews & todos       │
│  ☐ Sync with calendar                   │
│  ☐ Integrate with ATS                   │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  📑 Template Settings                   │
│  ☐ Save as template                     │
│  ☐ Make template public                 │
│                                         │
│  Template Category: [General ▼]         │
│                                         │
│  ─────────────────────────────────      │
│                                         │
│  🗑️ DANGER ZONE                         │
│  [Archive Workflow]                     │
│  [Delete Workflow]                      │
│                                         │
└─────────────────────────────────────────┘
```

### Step Details Panel (Shows when step selected)
```
┌─────────────────────────────────────────┐
│  📝 STEP DETAILS                        │
│                                         │
│  Editing: Technical Interview (#1)      │
│                                         │
│  Title                                  │
│  ┌─────────────────────────────────┐   │
│  │ Technical Interview             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Description                            │
│  ┌─────────────────────────────────┐   │
│  │ Assess technical skills         │   │
│  │ and problem-solving             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ── Interview Settings ──               │
│                                         │
│  Duration: [60] minutes                 │
│  Type: [Video ▼]                        │
│  Location: [Video Call room]            │
│                                         │
│  ── Advanced ──                         │
│                                         │
│  ☑ Required step                        │
│  ☐ Can be skipped                       │
│  ☑ Create real interview record         │
│                                         │
│  [Update Step]  [Close]                 │
└─────────────────────────────────────────┘
```

## 🎨 Design Specifications

### Colors
- **Primary**: Violet (#7C3AED) - Workflow brand color
- **Interview**: Blue (#3B82F6) - Interview steps
- **Todo**: Green (#10B981) - Todo/assignment steps
- **Background**: Gray-50 (#F9FAFB) - Left panel
- **Border**: Gray-200 (#E5E7EB)

### Typography
- **Headers**: font-bold text-lg
- **Labels**: font-medium text-sm text-gray-700
- **Body**: text-sm text-gray-600
- **Steps**: font-medium text-base

### Spacing
- **Panel Gap**: 24px (gap-6)
- **Section Spacing**: 16px (space-y-4)
- **Card Padding**: 16px (p-4)
- **Modal Padding**: 24px (p-6)

### Components
- **Step Cards**: Elevated with shadow, rounded-lg, hover effect
- **Tabs**: Underline style with active indicator
- **Buttons**:
  - Primary: bg-violet-600 hover:bg-violet-700
  - Secondary: border with hover effect
  - Danger: bg-red-600 hover:bg-red-700
- **Inputs**: Rounded-lg, focus:ring-2 focus:ring-violet-500

## 📱 Responsive Behavior

### Large Screens (>1200px)
- Left Panel: 320px fixed
- Right Panel: Flexible
- Step Details: 400px when visible

### Medium Screens (768px - 1200px)
- Left Panel: 280px
- Right Panel: Flexible
- Step Details: Overlay on mobile

### Small Screens (<768px)
- Stack vertically
- Full-width panels
- Collapsible sections

## ✨ Interactions

### Step Management
1. **Add Step**: Click "+ Interview" or "+ Todo" → Creates step → Opens details panel
2. **Edit Step**: Click step in list → Opens details panel
3. **Reorder**: Drag step card → Visual indicator → Drop to reorder
4. **Delete**: Click delete → Confirm dialog → Remove step

### Tab Navigation
1. **Click Tab**: Switch content in right panel
2. **Active Tab**: Blue underline indicator
3. **Badge**: Show count (e.g., "Assignments (5)")

### Step Details
1. **Auto-show**: When step created or selected
2. **Update**: Changes reflect immediately in step list
3. **Close**: Click "Close" or click outside

### Save Workflow
1. **Validate**: Check required fields
2. **Create Nodes**: Convert steps to backend nodes
3. **Create Integrations**: If enabled, create interviews/todos
4. **Success**: Show detailed success message with IDs
5. **Close Modal**: Return to workflow list

## 🚀 Benefits

✅ **Clear Organization**: Tabs separate concerns
✅ **Always Visible Steps**: Main workflow always in view
✅ **Better UX**: Focused editing with details panel
✅ **Scalable**: Easy to add new tabs/features
✅ **Professional**: Clean, modern interface
✅ **Efficient**: Less scrolling, faster editing

---

**Ready to implement this design?** 🎨
