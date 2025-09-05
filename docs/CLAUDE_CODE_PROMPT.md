
# Claude Code Prompt — HR & Recruitment Management System (FastAPI + MySQL + React/TS + Tailwind)

You are an expert full‑stack engineer. You will implement production‑quality code in **this repository layout** (already created). Use **FastAPI, SQLAlchemy, Alembic, Pydantic, Redis, Celery/Dramatiq**, and **React + TypeScript + Tailwind**. Local infra: **MySQL**, **Redis**, **MinIO (S3)**, **ClamAV (clamd)**, and **Mailpit** via `platform/docker-compose.yml`. **No hardcoded values** in the frontend; only consume **real APIs**. Keep **tests**, **docs**, and **types** in sync.

**Architecture & files**: See `PROJECT_STRUCTURE_UPDATED.md` at repo root for exact folders and responsibilities. Respect that structure strictly.

---

## Ground Rules (do not skip)
1. **Security & RBAC**
   - SQLAlchemy ORM only; validate and sanitize all inputs (Pydantic).
   - Enforce **company scoping + RBAC** on every handler via `dependencies.py` and `utils/permissions.py`.
   - Implement **2FA over email code** for all admins & super admin on login.
   - **SSO (Google/Outlook)**: allow only if account already exists (no auto‑provision).
   - Add **audit logs** for all admin actions; append‑only table.
   - Rate‑limit auth; lockouts after repeated failures.
2. **Storage & Files**
   - Use **MinIO (S3)** presigned uploads. After upload, run **ClamAV scan**. Only then mark files as available.
   - Store metadata (`sha256`, `size`, `mime`, `virus_status`) in `Attachment`.
3. **Real‑time**
   - WebSocket endpoints in `routers/messaging_ws.py`. Use **Redis pub/sub** for fan‑out.
4. **Calendars**
   - Implement **Google Calendar** and **Microsoft Graph** wrappers in `services/calendar_service.py` with **read/write + webhooks** for sync.
5. **Resume Builder**
   - Jinja2 → HTML → **WeasyPrint** → PDF; store on S3; share via signed URL; email via Mailpit in dev.
6. **Interview Scheduling**
   - Two proposal flows (Candidate→Recruiter→Employer and Employer→Recruiter→Candidate). Support propose/accept/decline/cancel/reschedule; keep sync with external calendars.
7. **Testing & Docs**
   - Backend: **pytest** with fakes for SMTP/S3/clamd and WebSocket tests.
   - Frontend: **Vitest + RTL**, plus **Playwright** e2e for happy paths.
   - Keep `docs/*` updated in the same PR; CI fails on drift.
8. **Environment**
   - Read all settings from `.env` files; expose frontend env via `VITE_*`. No hardcoded URLs, IDs, or secrets.

---

## Implementation Plan (phased tasks)

### Phase 0 — Scaffolding & Config
- [ ] Fill `backend/app/config.py` (Pydantic Settings) and `backend/app/main.py` (lifespan: connect Redis, init S3 client, warm ClamAV check).
- [ ] Implement `database.py` (async engine, sessions), `alembic/env.py`, base migration.
- [ ] Add global error handlers, CORS, gzip.
- [ ] Create `utils/constants.py` enums (roles, message types, company types) and `rbac.py` mappings.

### Phase 1 — Auth & Users
- [ ] Models: `User`, `Company`, `Role`, `UserRole`, `RefreshToken`, `PasswordResetRequest`, `OauthAccount`.
- [ ] Routes: `routers/auth.py` (login, refresh, logout, 2FA verify, SSO callbacks, password reset request/approve).
- [ ] Admin abilities: super admin creates recruiter/employer admins; admins create users only in their company; CSV import via `pandas` in `csv_import_service.py`.
- [ ] Notifications generated on password reset requests; shown in `notifications` feed.
- [ ] Tests: `test_auth.py`, `test_users.py`, `test_notifications.py`.

### Phase 2 — Messaging (real‑time + files)
- [ ] Schema: `Conversation`, `ConversationParticipant`, `Message`, `Attachment`.
- [ ] Rules: Candidate↔Recruiter allowed; Candidate↔Employer **blocked**; Employer↔Recruiter allowed.
- [ ] REST: `routers/messaging.py` for conversation list/create, message history, file upload (S3 presigned → antivirus flow).
- [ ] WS: `routers/messaging_ws.py`; join on conversation; Redis pub/sub; typing indicators; delivery receipts.
- [ ] Tests: `test_messaging.py` (REST + WS), `test_security.py` (rule enforcement).

### Phase 3 — Calendar & Interview Scheduling
- [ ] Integrations: `services/calendar_service.py` for Google & MS Graph; list/create/update/delete events; webhook handlers in `routers/calendar.py`.
- [ ] Interview Models: `Interview`, `InterviewProposal` (with proposer role, start/end, status).
- [ ] Flow: propose → accept/decline → finalize; reschedule and cancel; calendar sync on changes.
- [ ] Tests: `test_calendar.py`, `test_interviews.py`.

### Phase 4 — Resume Builder
- [ ] Schema: `Resume` (json_data, pdf_key, version).
- [ ] Routes: `routers/resumes.py` (save JSON, render PDF, email/share link).
- [ ] Service: `resume_service.py` using WeasyPrint + Jinja2.
- [ ] Tests: `test_resumes.py`.

### Phase 5 — Dashboards & Public Website
- [ ] Dashboards per role (candidate, employer, recruiter): KPIs, charts, notifications.
- [ ] Public SPA (candidate‑focused) with animated sections; feature list; “100% free for candidates”.
- [ ] Tests: component + e2e smoke for main nav and guards.

### Phase 6 — CI & Hardening
- [ ] GitHub Actions `ci.yml` to run backend/frontend tests and docs checker.
- [ ] Add `SECURITY.md` items: rate limiting, headers, secure cookies for refresh, CSRF considerations on non‑idempotent routes for web, etc.

---

## API Contracts (key excerpts)

### Auth
- `POST /api/auth/login` → `{ access_token, refresh_token, require_2fa }`
- `POST /api/auth/2fa/verify` → `{ access_token, refresh_token }`
- `POST /api/auth/refresh`
- `POST /api/auth/password-reset/request` (public)
- `POST /api/auth/password-reset/approve` (admin only)
- `GET /api/auth/sso/google/start` / `GET /api/auth/sso/google/callback`
- `GET /api/auth/sso/outlook/start` / `GET /api/auth/sso/outlook/callback`

### Messaging
- `GET /api/messaging/conversations?scope=...`
- `POST /api/messaging/conversations` → `{ id }` (server validates participant rules)
- `GET /api/messaging/conversations/{id}/messages`
- `POST /api/messaging/conversations/{id}/messages` (text)
- `POST /api/messaging/conversations/{id}/attachments/presign` → `{ url, fields }`
- `POST /api/messaging/attachments/{id}/scan-complete` (worker marks clean/blocked)
- `WS /ws/conversations/{id}` (join, send, receive, typing, receipts)

### Calendar & Interviews
- `POST /api/calendar/accounts` (link Google/MS)
- `GET /api/calendar/events` (range)
- `POST /api/calendar/events` (create) / `PATCH /api/calendar/events/{id}` / `DELETE ...`
- `POST /api/interviews/{id}/proposals` (create by role)
- `POST /api/interviews/{id}/proposals/{pid}/accept`
- `POST /api/interviews/{id}/proposals/{pid}/decline`
- `POST /api/interviews/{id}/cancel`
- Webhooks: `/api/calendar/webhooks/google`, `/api/calendar/webhooks/microsoft`

### Resume
- `POST /api/resumes` (save JSON) / `GET /api/resumes/{id}`
- `POST /api/resumes/{id}/render` → PDF on S3 + return signed URL
- `POST /api/resumes/{id}/share` (email to recruiter/company)

### Users
- `POST /api/admin/users/bulk` (CSV → pandas) → activation emails
- `PATCH /api/admin/users/{id}` / `DELETE` / `POST /api/admin/users/{id}/hold-login`

---

## Frontend Requirements
- Vite + React + TS + Tailwind; components under `src/components/*` and pages under `src/pages/*`.
- Global API module `services/api.ts` with Axios interceptors (JWT refresh, 401 handling).
- Real‑time messaging with native `WebSocket` using `VITE_WS_URL`.
- Calendar view (month/week/day), Interview proposal UI, Resume builder form + PDF preview.
- Use icon set of your choice (e.g., Lucide/Remix/Phosphor).

---

## Deliverables per Task
- Updated code files following the repo structure.
- **Unit/integration tests** and **updated docs** (`docs/*`) in the same changeset.
- Short **CHANGES** section in PR description including any new envs or migrations.

---

## Acceptance Criteria (definition of done)
- All routes protected with RBAC and company scoping; messaging rules enforced.
- File uploads blocked until **virus_status == clean**.
- WebSocket chat updates appear instantly across sessions.
- Calendar events reflect changes in both product and Google/MS calendars.
- Resume renders to PDF and can be shared and emailed (Mailpit visible in dev).
- CSV import creates users and sends activation emails.
- CI green: backend+frontend tests and docs checker pass. Coverage ≥ 80%.
- No hardcoded frontend values; all come from APIs or `VITE_*` envs.

---

### Execution
Start with **Phase 0**, submit code, tests, and docs. I will review and ask you to proceed to the next phase. Keep commits small and self‑contained. Avoid placeholders—ship working code.
