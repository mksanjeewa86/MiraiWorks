
# MiraiWorks — Project Structure (FastAPI + MySQL + React/TS + Tailwind)

> All-in-one HR & recruitment platform with real-time messaging, calendar sync (Google/Microsoft), resume builder (PDF + share), interview scheduling (two-way proposals), **Online Interview Service (Zoom-like)** with transcription (文字起こし) & summarization (要約), strict RBAC, SSO, 2FA, CSV import, MinIO S3 storage, antivirus scanning, Mail catcher, and full tests/docs.

```
MiraiWorks/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── rbac.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── company.py
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── candidate.py
│   │   │   ├── resume.py
│   │   │   ├── message.py
│   │   │   ├── attachment.py
│   │   │   ├── interview.py
│   │   │   ├── interview_proposal.py
│   │   │   ├── calendar_integration.py
│   │   │   ├── notification.py
│   │   │   ├── auth.py
│   │   │   ├── audit.py
│   │   │   └── meeting.py                 # NEW: meetings + artifacts + interview_type
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── company.py
│   │   │   ├── candidate.py
│   │   │   ├── resume.py
│   │   │   ├── message.py
│   │   │   ├── interview.py
│   │   │   ├── calendar.py
│   │   │   ├── notification.py
│   │   │   └── meeting.py                 # NEW: DTOs for meetings/transcripts/summaries
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── companies.py
│   │   │   ├── candidates.py
│   │   │   ├── resumes.py
│   │   │   ├── messaging.py
│   │   │   ├── messaging_ws.py
│   │   │   ├── interviews.py
│   │   │   ├── calendar.py
│   │   │   ├── notifications.py
│   │   │   ├── dashboard.py
│   │   │   ├── meetings.py                # NEW: REST for meetings lifecycle
│   │   │   └── meetings_ws.py             # NEW: WebRTC signaling & in-call chat
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── sso_service.py
│   │   │   ├── user_service.py
│   │   │   ├── csv_import_service.py
│   │   │   ├── storage_service.py
│   │   │   ├── antivirus_service.py
│   │   │   ├── email_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── messaging_service.py
│   │   │   ├── interview_service.py
│   │   │   ├── calendar_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── security_service.py
│   │   │   ├── audit_service.py
│   │   │   ├── meeting_service.py         # NEW: room lifecycle, ACLs, recording hooks
│   │   │   ├── rtc_service.py             # NEW: ICE servers (coturn), tokens, SFU option
│   │   │   └── transcribe_service.py      # NEW: 文字起こし + 要約 orchestration
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── permissions.py
│   │   │   ├── validators.py
│   │   │   ├── time.py
│   │   │   └── constants.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   ├── auth.py
│   │   │   └── logging.py
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── queue.py
│   │   │   ├── jobs_email.py
│   │   │   ├── jobs_calendar.py
│   │   │   ├── jobs_files.py
│   │   │   └── jobs_meetings.py           # NEW: recordings→S3, virus scan, STT+summary
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_users.py
│   │   │   ├── test_candidates.py
│   │   │   ├── test_resumes.py
│   │   │   ├── test_messaging.py
│   │   │   ├── test_interviews.py
│   │   │   ├── test_calendar.py
│   │   │   ├── test_notifications.py
│   │   │   ├── test_security.py
│   │   │   └── test_meetings.py           # NEW: REST + signaling + ACLs
│   │   ├── alembic/
│   │   │   ├── versions/
│   │   │   ├── env.py
│   │   │   └── alembic.ini
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── Dockerfile
│   ├── scripts/
│   │   ├── init-db.sql
│   │   ├── seed-data.sql
│   │   └── dev-tools.sh
│   └── docker/
│       └── (optional) uwsgi.ini
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── router.tsx
│   │   │   └── providers.tsx
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── auth/
│   │   │   ├── messaging/
│   │   │   ├── calendar/
│   │   │   ├── resumes/
│   │   │   ├── interviews/
│   │   │   ├── meeting/                    # NEW: VideoGrid, Controls, ChatPanel, FileShare, Consent
│   │   │   └── dashboard/
│   │   ├── pages/
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── messaging/
│   │   │   ├── calendar/
│   │   │   ├── interviews/
│   │   │   ├── resumes/
│   │   │   ├── admin/
│   │   │   └── meetings/                   # NEW: /meetings/:id
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── authService.ts
│   │   │   ├── messagingService.ts
│   │   │   ├── calendarService.ts
│   │   │   ├── resumeService.ts
│   │   │   ├── interviewService.ts
│   │   │   ├── meetingService.ts           # NEW: tokens, artifacts, consent
│   │   │   ├── notificationService.ts
│   │   │   └── userService.ts
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── styles/
│   │   ├── tests/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── env.d.ts
│   │   └── vite.config.ts
│   ├── .env.example
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
│
├── platform/
│   ├── docker-compose.yml                  # add coturn + optional STT container
│   ├── .env.example
│   └── README.md
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SETUP.md
│   ├── SECURITY.md
│   ├── MESSAGING_RULES.md
│   ├── CALENDAR_INTEGRATIONS.md
│   ├── RESUME_BUILDER.md
│   ├── INTERVIEW_FLOW.md                   # casual vs main; observer rules
│   ├── MEETINGS.md                         # NEW: Online Interview Service details
│   └── TRANSCRIPTION_SUMMARY.md            # NEW: STT & summary pipeline
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── docs-check.yml
│
├── scripts/
│   ├── dev-up.sh
│   └── lint.sh
│
├── .env.example
├── README.md
└── LICENSE
```

## Interview Types
- **Casual** (Candidate ↔ Recruiter)
- **Main** (Candidate ↔ Employer, recruiter optional observer/organizer)

## Online Interview Service (Highlights)
- WebRTC with **coturn** (TURN/STUN); WS signaling; in-call chat; file share; screen share; virtual background; expression viewer.
- Recording → S3 (MinIO) → antivirus scan → transcripts (文字起こし) → summaries (要約) → attach to interview.
- **Consent required** for recording/transcription; stored with the meeting; RBAC-enforced access.
- Integrated with Calendar & Notifications; artifacts visible on candidate/employer/recruiter dashboards per role.
