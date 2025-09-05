
# HR & Recruitment Management System — UPDATED Project Structure (FastAPI + MySQL + React/TS + Tailwind)

> This updates your previous layout to add: real‑time messaging with brokered rules, calendar (Google/Microsoft) bi‑directional sync, resume builder with PDF & share, interview scheduling with two‑way proposals, strict RBAC, SSO (Google/Outlook), admin‑only password reset workflow, 2FA by email code for all admins, CSV bulk user import (pandas), virus scanning (ClamAV) before any upload, MinIO S3 for storage, Mailpit mailcatcher, Redis for websockets/broadcast & task queue, complete tests, and docs-as-code.

```
HR-Recruitment-Management-System/
│
├── backend/                                      # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                               # FastAPI app entry point (lifespan events register scanners, queues)
│   │   ├── config.py                             # Pydantic Settings; NO hardcoded values
│   │   ├── database.py                           # SQLAlchemy + MySQL engine/session, alembic_base
│   │   ├── dependencies.py                       # Common deps (auth, db, current_user, permissions)
│   │   ├── rbac.py                               # Role & permission mapping
│   │   │
│   │   ├── models/                               # SQLAlchemy models (normalized)
│   │   │   ├── __init__.py
│   │   │   ├── company.py                        # Company(id, name, type=[RECRUITER|EMPLOYER], ...)
│   │   │   ├── user.py                           # User(id, company_id?, email, is_active, is_admin, require_2fa, ...)
│   │   │   ├── role.py                           # Role(id, name); UserRole(user_id, role_id, scope)
│   │   │   ├── candidate.py                      # Candidate(user_id PK/FK, profile fields)
│   │   │   ├── resume.py                         # Resume(id, candidate_id, json_data, pdf_key, version)
│   │   │   ├── message.py                        # Conversation(id, participants[m2m], type), Message(id, conv_id, ...)
│   │   │   ├── attachment.py                     # Attachment(id, owner_id, s3_key, mime, sha256, size, virus_status)
│   │   │   ├── interview.py                      # Interview(id, candidate_id, employer_company_id, recruiter_company_id, ...)
│   │   │   ├── interview_proposal.py             # Proposed slots (by candidate or employer via recruiter)
│   │   │   ├── calendar_integration.py           # ExternalCalendarAccount, SyncedEvent
│   │   │   ├── notification.py                   # Notification(id, user_id, type, payload, seen_at)
│   │   │   ├── auth.py                           # RefreshToken, PasswordResetRequest, OauthAccount
│   │   │   └── audit.py                          # AuditLog(id, actor_id, action, entity, diff, ip, ua)
│   │   │
│   │   ├── schemas/                              # Pydantic models (request/response DTOs)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                           # Login, 2FA, SSO, PasswordResetRequest
│   │   │   ├── user.py                           # Create/Update user, CSV import responses
│   │   │   ├── company.py
│   │   │   ├── candidate.py
│   │   │   ├── resume.py
│   │   │   ├── message.py
│   │   │   ├── interview.py
│   │   │   ├── calendar.py
│   │   │   ├── notification.py
│   │   │   └── common.py                         # Enums, pagination, metadata
│   │   │
│   │   ├── routers/                              # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                           # Email+password, SSO (Google/MS), 2FA (email code), refresh, logout
│   │   │   ├── users.py                          # Super/recruiter/employer admin user mgmt, CSV import
│   │   │   ├── companies.py                      # Company CRUD (super admin)
│   │   │   ├── candidates.py                     # Candidate profile, resume, applications
│   │   │   ├── resumes.py                        # Resume builder (HTML->PDF), share/email links
│   │   │   ├── messaging.py                      # Conversations, rules enforced; file upload -> virus scan
│   │   │   ├── messaging_ws.py                   # WebSocket endpoints; Redis pub/sub
│   │   │   ├── interviews.py                     # Propose/accept/cancel/reschedule flow
│   │   │   ├── calendar.py                       # Google/Microsoft Calendar (read/write, webhooks)
│   │   │   ├── notifications.py                  # Notification feed (real‑time & REST)
│   │   │   └── dashboard.py                      # Stats for each role
│   │   │
│   │   ├── services/                             # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py                   # JWT, hashing, 2FA codes, session TTL (30 days)
│   │   │   ├── sso_service.py                    # OAuth2 Google/MS; allow-login-only-if-email-exists
│   │   │   ├── user_service.py                   # Admin CRUD, temp hold login, delete
│   │   │   ├── csv_import_service.py             # pandas-based CSV -> users
│   │   │   ├── storage_service.py                # MinIO S3 client (presigned), folders by tenant
│   │   │   ├── antivirus_service.py              # ClamAV scan via clamd (quarantine on detect)
│   │   │   ├── email_service.py                  # SMTP via Mailpit in dev (switchable in prod)
│   │   │   ├── resume_service.py                 # Build PDF (WeasyPrint) from Jinja2 template
│   │   │   ├── messaging_service.py              # Conversation routing rules + broker logic
│   │   │   ├── interview_service.py              # Two‑way proposals, acceptance rules
│   │   │   ├── calendar_service.py               # Google/Microsoft Graph API wrappers
│   │   │   ├── notification_service.py           # Create/dispatch notifications (WS + email)
│   │   │   ├── security_service.py               # Rate limit, brute force, IP allowlist for admin
│   │   │   └── audit_service.py                  # Diff capture & append-only audit records
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── permissions.py                    # Decorators/helpers for RBAC checks
│   │   │   ├── validators.py                     # Input validators & sanitizers
│   │   │   ├── time.py                           # TZ handling (Asia/Tokyo default override by user)
│   │   │   └── constants.py                      # Enums: roles, companies, message types, etc.
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   ├── auth.py                           # Bearer auth, session checks, company scoping
│   │   │   └── logging.py
│   │   │
│   │   ├── workers/                              # Background tasks (Celery/Dramatiq)
│   │   │   ├── __init__.py
│   │   │   ├── queue.py                          # Broker connection (Redis)
│   │   │   ├── jobs_email.py                     # password reset, notifications, resume share
│   │   │   ├── jobs_calendar.py                  # push/pull sync
│   │   │   └── jobs_files.py                     # virus scan, pdf generation
│   │   │
│   │   ├── tests/                                # Backend tests (pytest)
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py                       # Test DB, factories, fake SMTP, fake S3, fake ClamAV
│   │   │   ├── test_auth.py
│   │   │   ├── test_users.py
│   │   │   ├── test_candidates.py
│   │   │   ├── test_resumes.py
│   │   │   ├── test_messaging.py                 # WS & REST
│   │   │   ├── test_interviews.py
│   │   │   ├── test_calendar.py
│   │   │   ├── test_notifications.py
│   │   │   └── test_security.py
│   │   │
│   │   ├── alembic/
│   │   │   ├── versions/
│   │   │   ├── env.py
│   │   │   └── alembic.ini
│   │   │
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── Dockerfile
│   │
│   ├── scripts/
│   │   ├── init-db.sql                           # Create utf8mb4 collations, base schema
│   │   ├── seed-data.sql
│   │   └── dev-tools.sh                          # helpers: create superadmin, etc.
│   │
│   └── docker/                                   # Backend-only docker helpers
│       └── uwsgi.ini (if needed later)
│
├── frontend/                                     # React + TS + Tailwind
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── router.tsx
│   │   │   └── providers.tsx
│   │   ├── components/
│   │   │   ├── common/                           # Button, Input, Modal, Table, Navbar, Sidebar, Toast, Avatar
│   │   │   ├── auth/                             # Login, 2FA, SSO buttons, PasswordResetRequest
│   │   │   ├── messaging/                        # ConversationList, ChatPanel, MessageInput, FilePreview
│   │   │   ├── calendar/                         # CalendarView (month/week/day), Picker, SlotCard
│   │   │   ├── resumes/                          # ResumeForm, ResumePreview, ResumeShareDialog
│   │   │   ├── interviews/                       # ProposeDatesForm, ProposalTimeline
│   │   │   └── dashboard/                        # StatsCard, Chart, Activity
│   │   ├── pages/
│   │   │   ├── login/                            # Modern login page
│   │   │   ├── dashboard/                        # CandidateDashboard / EmployerDashboard / RecruiterDashboard
│   │   │   ├── messaging/                        # /messages
│   │   │   ├── calendar/                         # /calendar
│   │   │   ├── interviews/                       # /interviews
│   │   │   ├── resumes/                          # /resume-builder
│   │   │   ├── admin/                            # UserManagement, CompanyManagement, SystemNotifications
│   │   │   └── website/                          # Public SPA (candidate-focused landing)
│   │   ├── services/
│   │   │   ├── api.ts                            # Axios w/ interceptors; base URL from VITE_API_URL
│   │   │   ├── authService.ts
│   │   │   ├── messagingService.ts               # uses WebSocket for live updates
│   │   │   ├── calendarService.ts
│   │   │   ├── resumeService.ts
│   │   │   ├── interviewService.ts
│   │   │   ├── notificationService.ts
│   │   │   └── userService.ts
│   │   ├── store/                                # Context or Redux
│   │   │   ├── auth/
│   │   │   ├── notifications/
│   │   │   └── index.ts
│   │   ├── hooks/                                # useAuth, useApi, usePermissions, useRealtime
│   │   ├── types/                                # auth, user, company, message, interview, resume, api
│   │   ├── utils/                                # helpers, formatters, validators
│   │   ├── styles/                               # Tailwind + component CSS
│   │   ├── tests/                                # Vitest + RTL
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── env.d.ts                              # types for import.meta.env (VITE_*)
│   │   └── vite.config.ts
│   ├── .env.example
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
│
├── platform/                                     # Infra shared services (docker-compose)
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md
│
├── docs/                                         # Docs-as-code (kept in sync)
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SETUP.md
│   ├── SECURITY.md
│   ├── MESSAGING_RULES.md                        # Brokered messaging constraints
│   ├── CALENDAR_INTEGRATIONS.md
│   ├── RESUME_BUILDER.md
│   ├── INTERVIEW_FLOW.md
│   └── ADR/                                      # Architecture Decision Records
│       └── ADR-0001-use-minio-and-clamav.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml                                # backend+frontend test, lint, typecheck, coverage gate
│       └── docs-check.yml                        # fails PR if docs drift on API or schema
│
├── scripts/                                      # Repo-level helpers
│   ├── dev-up.sh                                 # docker compose up
│   └── lint.sh
│
├── .env.example                                  # top-level orchestrator env
├── README.md
└── LICENSE
```
## Messaging Rules (Enforced)
- Candidate ↔ Recruiter: allowed direct messaging.
- Candidate ↔ Employer: **NOT allowed** (blocked at router/service).
- Employer ↔ Recruiter: allowed.
- Conversations are scoped to `company_id` pairs; ACLs checked per message.
- All uploads (chat files, resumes) -> presigned S3 (MinIO) -> **scan with ClamAV** before marking `virus_status="clean"`.
- Real-time via WebSocket; horizontal scale uses Redis pub/sub.

## Interview Scheduling
- Two proposal flows:
  1) Candidate → Recruiter → Employer (fix/confirm)
  2) Employer → Recruiter → Candidate
- Both sides can cancel/reschedule; calendar sync updates external events.

## Auth & Login
- Email+password for all users.
- **Admins (all companies) + Super Admin must pass 2FA**: 6-digit code emailed.
- Password reset: only Company Admin or Super Admin can finalize; requests come from Login page (creates Notification + Email).
- Session TTL: 30 days (refresh token). If no login within window → auto-expire.
- SSO (Google, Outlook) **only if email already exists**; otherwise block auto-provisioning.

## Public Website
- Single Page App focused on candidates: features, free usage, animated & colorful.

---

## Key .env (combined)
```
# backend
DB_URL=mysql+asyncmy://root:root@mysql:3306/hrms?charset=utf8mb4
REDIS_URL=redis://redis:6379/0
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=hrms
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
SMTP_HOST=mailpit
SMTP_PORT=1025
SMTP_FROM=noreply@hrms.local
JWT_SECRET=change_me
JWT_ACCESS_TTL_MIN=15
JWT_REFRESH_TTL_DAYS=30
FORCE_2FA_FOR_ADMINS=true
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
MS_OAUTH_CLIENT_ID=...
MS_OAUTH_CLIENT_SECRET=...
APP_BASE_URL=http://localhost:5173

# frontend (Vite)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## platform/docker-compose.yml (services)
- **backend** (uvicorn) — depends on mysql, redis, clamav, minio, mailpit
- **frontend** (vite dev server / nginx in prod)
- **mysql** (8.x) with utf8mb4, performance options
- **redis** for pub/sub + tasks
- **minio** + **minio-console** (browser)
- **clamav** (clamd + freshclam)
- **mailpit** (mail catcher UI)
- **worker** (Celery/Dramatiq) for email, calendar sync, file scan, pdf build

## Testing
- Backend: pytest + coverage; WS tests; fake SMTP/S3/clamd.
- Frontend: Vitest + React Testing Library; Playwright e2e.
- CI: GitHub Actions runs full suite; blocks if docs drift or coverage < threshold.

## Security
- SQLAlchemy ORM (no raw queries); input validation (Pydantic).
- RBAC middleware; company scoping checks on every request.
- Rate limiting on auth endpoints; lockouts for brute-force.
- Signed URLs for S3; server-side virus scanning before “available=true”.
- Comprehensive audit log; immutable append-only table.
```

