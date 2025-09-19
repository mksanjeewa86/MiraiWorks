# Recruitment Process Feature Plan

## Overview
- Empower employers to model vacancy-specific recruitment workflows using configurable interview and todo nodes displayed in an interactive block diagram.
- Recruiters execute the workflow on behalf of employers once connected to the vacancy; candidates participate only when prompted and can track personal progress.
- Enforce strict role-based permissions: employers own creation and maintenance, recruiters update execution data, candidates view or submit requested artifacts.

## Goals & Success Metrics
- Reduce manual coordination between employers and recruiters by giving a single source of truth for candidate progress.
- Provide candidates with transparent status updates to decrease support tickets by 30%.
- Ensure recruiters close 90% of assigned nodes within SLA through automated reminders.
- Maintain full auditability of decisions and outcomes for compliance reviews.

## Key Actors & Capabilities
- **Employer Admin**: Create/clone/activate processes per vacancy, add or reorder nodes, configure transitions, override node outcomes, deactivate processes, export reports.
- **Recruiter**: View assigned vacancies and processes, record interview results, upload artifacts, mark todos complete, request employer decisions, cannot alter structure.
- **Candidate**: View personal process timeline, upload requested files, confirm availability, cannot modify nodes or results.
- **System Services**: Trigger notifications, enforce state machine rules, log audits, generate analytics snapshots.

## Domain Model
- **Process** (`id`, `vacancy_id`, `owner_employer_id`, `version`, `status`, `activated_at`, `archived_at`).
- **ProcessNode** (`id`, `process_id`, `sequence`, `type`, `title`, `description`, `instructions`, `expected_duration`, `gating_rule`, `auto_advance`, `created_by`, `updated_by`).
- **NodeOutcomeDefinition** (`id`, `node_id`, `label`, `status_change`, `next_sequence`, `color`).
- **CandidateProcess** (`id`, `candidate_id`, `process_id`, `current_node_id`, `status`, `started_at`, `completed_at`, `terminated_at`).
- **NodeResult** (`id`, `candidate_process_id`, `node_id`, `recorded_by`, `recorded_role`, `outcome_label`, `notes`, `attachments`, `recorded_at`).
- **NodeTodoSubmission** (`id`, `candidate_process_id`, `node_id`, `submitted_by`, `payload`, `submitted_at`, `validated_at`).
- **ProcessAuditLog** (`id`, `entity_type`, `entity_id`, `action`, `actor_id`, `actor_role`, `changes`, `created_at`).
- **RecruiterConnection** (`id`, `employer_id`, `recruiter_id`, `vacancy_id`, `status`, `activated_at`).

## State Machines
- **Process Status**: `Draft` Å® `Active` Å® (`Completed` | `Cancelled`); `Draft` may go to `Archived`; only employers transition states.
- **Candidate Process Status**: `Not Started` Å® `In Progress` Å® (`Hired` | `Rejected` | `Withdrawn`); employers can override to `On Hold`.
- **Node Execution Status** per candidate: `Pending`, `Scheduled`, `In Progress`, `Awaiting Candidate`, `Awaiting Employer`, `Completed`, `Failed`, `Skipped`.
- Transition guards ensure sequence integrity: cannot advance to node N+1 until node N has terminal status or `auto_advance` is true.

## Business Rules
- Processes must contain at least one node and at least one interview node when `vacancy.requiresInterview = true`.
- Employers cannot delete an active node if any candidate has started it; instead, they mark it inactive and add a replacement (versioning).
- Recruiters may propose outcome changes, but employer approval is required for terminal decisions (`Hired`, `Rejected`).
- Candidate submissions exceeding file size or missing required metadata reject with actionable validation messages.
- When a candidate fails an interview, the process either terminates or branches according to configured `NodeOutcomeDefinition`.

## UI & UX Flow
- **Process Builder**: Drag-and-drop canvas using React Flow (or similar). Inline configuration drawer for node details, outcome routing, SLA timers. Validation badges display unresolved issues.
- **Execution Dashboard**: Swimlane or block layout showing nodes with aggregate candidate counts per status. Selecting a node opens detail panel for recruiters/employers.
- **Candidate Timeline**: Linear list with icons; upcoming steps collapsed with estimated dates; completed steps show recruiter notes once employer approves sharing.
- **Edit Mode Safeguards**: Editing an active process prompts for versioning; users choose `Apply to new candidates` or `Apply immediately` (with warnings about in-flight impacts).

## Permissions Matrix
- `Process CRUD`: Employer only.
- `Node Structure Edit`: Employer only (requires `Active` Å® `Draft` transition or versioning flow).
- `Node Result Update`: Recruiter (owns notes, scheduling, attachments); Employer (override or final decision) with audit log.
- `Candidate Submission`: Candidate within permitted nodes; automatically shared with recruiter.
- `Process Visibility`: Employer + connected recruiters (all candidates); candidate sees personal data only.

## Notifications & Integrations
- Email/SMS/in-app notifications for node assignment, upcoming interviews, overdue todos, and final decisions.
- Calendar integration optional via recruiter OAuth (Google/Microsoft) to auto-create interview events.
- Webhook events (`process.activated`, `node.result.recorded`, `candidate.status.changed`) for downstream analytics and CRM sync.

## Data Retention & Compliance
- Retain NodeResults and attachments for minimum 24 months; support GDPR deletion per candidate (pseudonymize personal data, retain aggregated metrics).
- Provide export of candidate journey for compliance audits (PDF/CSV).
- Log every structural change with diff of before/after values; expose read-only audit stream to employer compliance role.

## Edge Cases & Safeguards
- Handle recruiter reassignment mid-process (transfer ownership, reassign upcoming nodes).
- Support candidate reactivation after withdrawal (resume at same node if employer approves).
- Allow parallel branches by duplicating nodes with same sequence number; UI must clarify concurrency and completion rules.
- Prevent infinite loops by limiting total nodes per process (configurable max, e.g., 25).
- Gracefully handle deleted recruiter accounts by reassigning tasks to employer admin.

## Analytics & Reporting
- Dashboard metrics: time-in-stage averages, drop-off rate per node, recruiter workload, vacancy fill time.
- Exportable CSV for HR analytics team; consider embedding charts within employer portal.
- Feed anonymized aggregates to recommendation engine for future process templates.

## Scenario Tests
- `Employer Creates Process Template`: Employer drafts three-node process, validates missing required fields, activates after resolving issues.
- `Recruiter Executes Interview Flow`: Recruiter schedules first interview, records result, triggers auto-advance to coding test todo, uploads evaluation file, employer reviews.
- `Candidate Submits Todo`: Candidate receives coding assignment, uploads solution within SLA, recruiter marks review complete, employer approves progression.
- `Process Versioning With Active Candidates`: Employer clones active process, modifies second interview, applies changes to new candidates only; in-flight candidates continue original version.
- `Failure Branch Handling`: Candidate fails second interview, system routes to employer decision node, employer records rejection, notifications fire to candidate and recruiter.
- `Recruiter Reassignment`: Original recruiter removed, new recruiter takes over, receives backlog of pending nodes, preserves audit trail.
- `Candidate Withdraws`: Candidate withdraws during todo; system marks process `Withdrawn`, releases recruiter tasks, sends summary to employer.

## Endpoint Specifications
- `POST /vacancies/{vacancyId}/processes`: Create process; payload includes `name`, `description`, initial nodes; validates employer ownership; returns new process with version.
- `PUT /processes/{processId}`: Update metadata; rejects if active without versioning flag; audit log entry required.
- `POST /processes/{processId}/nodes`: Append node; request body contains `type`, `title`, `sequence`, `gating_rule`, `outcomes`.
- `PATCH /processes/{processId}/nodes/{nodeId}`: Modify node details or outcomes; supports partial updates; prevents sequence collision.
- `DELETE /processes/{processId}/nodes/{nodeId}`: Soft-delete node (mark inactive); fails if node has results.
- `PATCH /candidate-processes/{candidateProcessId}/nodes/{nodeId}/result`: Recruiter or employer post outcome; payload includes `status`, `notes`, `attachments`, `next_action`.
- `POST /candidate-processes/{candidateProcessId}/nodes/{nodeId}/submission`: Candidate uploads todo artifact; server validates file type/size; triggers recruiter notification.
- `POST /processes/{processId}/activate`: Employer sets process to `Active`; enforces validation completeness.
- `POST /candidate-processes/{candidateProcessId}/advance`: Employer overrides to move candidate forward/backward; logs reason.

## Endpoint Test Coverage
- `POST /vacancies/{id}/processes`: Verify success for valid employer, failure for unauthorized recruiter, validation for missing nodes, duplication prevention for existing active process.
- `PUT /processes/{id}`: Ensure version increment when editing active process, reject unauthorized role, confirm audit entry emitted.
- `POST /processes/{id}/nodes`: Validate unique sequence enforcement, auto-resequence option, rejection when exceeding node limit.
- `PATCH /processes/{id}/nodes/{nodeId}`: Test partial updates, outcome routing changes, guard against removing final path to completion.
- `DELETE /processes/{id}/nodes/{nodeId}`: Confirm soft-delete flag set, ensure active candidates block destructive removal, verify audit trail.
- `PATCH /candidate-processes/{id}/nodes/{nodeId}/result`: Recruiter success path, employer override path, reject candidate attempt, enforce required outcome label.
- `POST /candidate-processes/{id}/nodes/{nodeId}/submission`: Validate file upload constraints, duplicate submission handling, recruiter notification side effects.
- `POST /processes/{id}/activate`: Test activation prevents when unresolved validation errors exist; ensure notification events queue.
- `POST /candidate-processes/{id}/advance`: Confirm employer-only access, enforce state machine rules, ensure history record created.

## Non-Functional Requirements
- Backend must process node updates under 250 ms p95; heavy operations (analytics) run async.
- All API calls require auth tokens with role claims; enforce vacancy-level authorization checks.
- Provide feature flag to roll out per employer; support blue/green deployment of builder UI.
- Ensure diagram rendering supports accessibility (keyboard drag/drop, ARIA labels, high-contrast mode).

## Rollout Plan
- Phase 1: Internal beta with one employer; monitor audit logs, gather feedback on builder UX.
- Phase 2: Expand to 10 employers; enable recruiter notifications, capture metrics.
- Phase 3: General availability; publish documentation, provide training materials, track adoption KPIs.

## Open Questions
- Do we require SLA timers per node, and if so should overdue nodes auto-escalate to employer?
- Should candidates be able to request rescheduling within the platform, or does that remain manual communication?
- How do we handle third-party assessment integrations (e.g., coding test vendors) within todo nodes?
