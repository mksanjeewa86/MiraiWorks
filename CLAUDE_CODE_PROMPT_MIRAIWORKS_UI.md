
# Claude Code Prompt — Upgrade MiraiWorks UI (Login, Side Menu, Dashboards)

You are a senior front-end engineer. Refactor and enhance the MiraiWorks SPA UI to a modern, responsive design with clear UX for candidates, recruiters, and employers.

## Tech & Libraries
- React + TypeScript + Vite + TailwindCSS  
- shadcn/ui components (Buttons, Cards, Dialog, Dropdown, Sheet, Tabs, Avatar, Badge, Toast)  
- lucide-react icons  
- recharts (for simple charts)  
- React Router  
- React Hook Form + Zod for validation  
- Axios (already in `services/api.ts`) with JWT interceptor  
- Do not hardcode. Read from APIs or `VITE_*` envs only.

## Global Design
- Create an **app shell** with a **sticky top navbar**, **collapsible side menu**, and **content area**.
- Support **light/dark** themes (Tailwind + `data-theme` class).  
- Typography scale, spacing, and radii consistent (e.g., rounded-2xl, shadow-sm).  
- Add **loading skeletons**, empty states, and error states for all pages.
- Keyboard accessible and screen-reader friendly (ARIA, focus rings).

## File Targets & Structure (frontend)
Update/create files under `frontend/src/`:

```
app/
  router.tsx
  providers.tsx
layout/
  AppLayout.tsx
  Sidebar.tsx
  Topbar.tsx
components/common/
  Brand.tsx
  SearchInput.tsx
  StatCard.tsx
  DataTable.tsx
  EmptyState.tsx
  LoadingSkeleton.tsx
  ConfirmDialog.tsx
components/auth/
  LoginForm.tsx
  TwoFactorForm.tsx
  PasswordResetRequest.tsx
components/dashboard/
  CandidateOverview.tsx
  RecruiterOverview.tsx
  EmployerOverview.tsx
  ActivityFeed.tsx
  Charts.tsx
components/messaging/
  ConversationList.tsx
  ChatPanel.tsx
  MessageInput.tsx
components/calendar/
  CalendarView.tsx
components/interviews/
  InterviewList.tsx
  ProposalTimeline.tsx
components/resumes/
  ResumeBuilderForm.tsx
  ResumePreview.tsx
pages/login/index.tsx
pages/dashboard/index.tsx
pages/messaging/index.tsx
pages/calendar/index.tsx
pages/interviews/index.tsx
pages/resumes/index.tsx
pages/admin/index.tsx
styles/
  theme.css
```

## Tasks

### 1) App Shell & Navigation
- Implement `AppLayout.tsx` with:
  - **Topbar**: brand logo “MiraiWorks”, global search, notifications bell, user avatar menu (Profile, Settings, Logout).
  - **Sidebar** (collapsible & responsive):
    - Candidate: Dashboard, Jobs, Messages, Calendar, Interviews, Resume, Settings
    - Recruiter: Dashboard, Candidates, Messages, Calendar, Interviews, Companies, Settings
    - Employer: Dashboard, Positions, Messages (no direct candidate messaging), Calendar, Interviews, Settings
  - Mobile: use shadcn **Sheet** for slide-in menu.
- Active route highlighting; tooltips on collapsed menu.
- Add **role-based** menu items and **route guards** in `router.tsx`.

### 2) Auth Pages
- `pages/login/index.tsx`:
  - Card center layout with brand, welcome text.
  - `LoginForm` (email, password) + **SSO buttons** (Google/Outlook).
  - If admin, show **2FA step** (`TwoFactorForm`) after password.
  - “Forgot password” opens `PasswordResetRequest` dialog (submits request; success toast).
- Validation via **Zod**; error messages under fields; disable button while submitting.

### 3) Dashboards (Role-Based)
- `pages/dashboard/index.tsx` detects role and renders:
  - **CandidateOverview**: Active applications, Interviews (upcoming), Messages unread, Resume completeness %, simple line chart of application activity.
  - **RecruiterOverview**: Pipeline stats (New candidates this week, Interviews scheduled, Offers sent), bar chart of pipeline stages, activity feed.
  - **EmployerOverview**: Open positions, candidates per position, interview schedule, funnel conversion, pie chart of sources.
- Use reusable **StatCard** and `Charts.tsx` wrappers.

### 4) Core Screens
- **Messaging**: 2-pane layout. Left: `ConversationList` (search, badges). Right: `ChatPanel` with bubble messages, file preview, `MessageInput` (attachments, emoji, send).
- **Calendar**: `CalendarView` (month/week/day), list of upcoming events, Create/Reschedule dialogs.
- **Interviews**: list + detail; **Casual/Main** chips; `ProposalTimeline` with actions (propose, accept, decline, reschedule); link to meeting join when scheduled.
- **Resume Builder**: multi-step form (`ResumeBuilderForm`), live `ResumePreview`, actions: Save, Render PDF, Share via email.

### 5) States & Feedback
- Each page needs:
  - **LoadingSkeleton** (skeletons for cards/tables)
  - **EmptyState** component (icon + text + primary CTA)
  - **Error state** with retry
- Global **Toast** notifications for success/error.

### 6) Theming & Tailwind
- Update `tailwind.config.js` with brand tokens (no hardcodes in code):
  - Primary `#6C63FF`, Accent `#22C55E`, Muted `#64748B`.
- Use Tailwind utility classes; keep consistent spacing (`p-6`, `gap-6`) and `rounded-2xl`.
- Dark mode: `data-theme="dark"` on `<html>` toggled by user menu.

### 7) API Wiring (no mocks)
- All lists and counts must call existing API services (`authService`, `notificationService`, `messagingService`, etc.).
- `api.ts` must auto-refresh JWT on 401.
- Pull **unread notifications** count for the topbar bell; click opens a dropdown list (link to related page).

### 8) Accessibility & Quality
- Focus management on dialogs.
- Semantic headings and landmarks.
- Keyboard: Tab/Shift+Tab through interactive elements; Enter/Escape where expected.

### 9) Testing
- Vitest + React Testing Library:
  - Smoke tests for each page.
  - Form validation on Login/2FA/Reset.
  - Sidebar toggling; route guard behavior.
- Playwright happy-path e2e:
  - Login → Dashboard (per role)  
  - Navigate to Messaging → send message  
  - Calendar create/edit event  
  - Resume render action

## Acceptance Criteria
- The app looks like a modern SaaS: clean spacing, clear hierarchy, polished states.
- Collapsible sidebar works on desktop; sheet drawer on mobile.
- Login/2FA/SSO flows are implemented with real API calls & error handling.
- Role-based dashboards render correct metrics and charts.
- All pages have loading, empty, and error states.
- No hardcoded data; everything from API or `VITE_*`.
- Light/dark mode works end-to-end.

## Deliverables
- Updated components/pages as listed.
- Tailwind theme tokens and minimal brand styling.
- Tests (unit + e2e) passing.
- Short README section with screenshots and how to run UI locally.
