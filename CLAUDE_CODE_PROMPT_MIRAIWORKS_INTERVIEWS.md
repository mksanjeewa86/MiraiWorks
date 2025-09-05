
# Claude Code Prompt — MiraiWorks (with Online Interview Service)

You are an expert full-stack engineer. Implement MiraiWorks as specified in the repo structure above. Use **FastAPI, SQLAlchemy, Alembic, Redis (pub/sub & queue), MinIO (S3), ClamAV, Mailpit**, and **React + TypeScript + Tailwind**. Real-time via **WebSocket**; media via **WebRTC** with **coturn**. Read configs from `.env` only. Keep tests and docs updated.

## New Module: Online Interview Service
- Two types: **casual** (Candidate↔Recruiter) and **main** (Candidate↔Employer, recruiter observer possible).
- Features: video, chat, screen share, file share, background change, expression viewer, **transcription (文字起こし)**, **summarization (要約)**.
- Security: consent flags, RBAC on participants and artifacts, antivirus scan on all files.

## Phases (delta from existing)
### Phase 3.5 — Online Interview Service (WebRTC + Transcription)
- Models: Meeting, MeetingParticipant, MeetingRecording, MeetingTranscript, MeetingSummary with `interview_type` in {casual, main}.
- REST: `/api/meetings` (create/end), `/api/meetings/{id}/tokens` (ICE & join), `/api/meetings/{id}/consent`, `/api/meetings/{id}/artifacts`.
- WS: `/ws/meetings/{id}` for signaling (offer/answer/candidate), presence, in-call chat & reactions.
- Services: `meeting_service.py`, `rtc_service.py` (coturn tokens), `transcribe_service.py` (文字起こし + 要約).
- Workers: `jobs_meetings.py` → S3 recording, antivirus, STT & summary generation.
- Frontend: `components/meeting/*` + `pages/meetings/*` with video grid, controls, chat, file share, consent UI.
- Tests: unit (signaling/permissions), integration (REST), e2e (join → talk → end & artifacts).

## Acceptance Criteria (Online Interview Service)
- Casual and Main interviews enforce correct participants and permissions.
- Meetings work behind NAT using coturn; tokens delivered securely.
- Recording/transcription/summaries only when consented; artifacts accessible per RBAC with signed URLs.
- Artifacts appear in the relevant interview timeline and dashboards.
- CI green with updated docs.

Begin with models + REST/WS skeletons and minimal UI that can place/join calls locally with coturn in docker-compose. Then add recording/STT/summary as a follow-up PR.
