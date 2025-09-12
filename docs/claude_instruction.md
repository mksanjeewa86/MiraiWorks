You are my senior full-stack pair programmer. I already have (or will initialize if missing) a React + TypeScript frontend and a FastAPI backend with PostgreSQL, containerized via Docker Compose. Your job: implement a production-ready chat window with the exact behavior and test coverage below. Do not generate filler; produce only what is required to satisfy the acceptance criteria. Keep code idiomatic, typed, and clean.

Scope & Rules

In scope: messaging features only.
Explicitly out of scope: phone/video call features (do not add buttons, code paths, or stubs for calls).
Use WebSockets for realtime (FastAPI websockets or WebSocketRoute) and Postgres for persistence.
Strict typing everywhere ("strict": true in TS; type hints + mypy for Python).

Functional Requirements (must all work)
Send message
From message input in Conversation tab, send text messages to the selected contact/conversation.
Persist, broadcast realtime to both participants, and optimistically render.
Realtime message view
When either party sends a message, the other sees it instantly without refresh (WebSocket fan-out).
Realtime update without refresh
New messages, read receipts (optional but preferred), and conversation list preview update live.
Default open last conversation
On chat window open (route /chat), auto-select and load the most recently active conversation, focus the message input, and scroll to the latest message.
Two tabs: Conversation / Contacts
Tab 1: Conversation (thread view, composer, attachments/emoji).
Tab 2: Contacts (searchable list).
Contacts hover → “Send message”
On hover, show Send message button. On click:
Switch to Conversation tab.
Open (or create) conversation with that contact.
Focus the message input.
Emoji support
Emoji picker in composer; insert at caret; send as Unicode; render properly.
File send / receive
Attach any file type (images/docs/video/etc.).
Show attachment chips/thumbnails (image preview inline; others as file name + size).

Receiver can download or view (where browser-supported) on click.

Enforce safe content type & size checks; store in object storage or local volume (configurable).

Email notification (settings-based)

If user’s “message notifications: on” setting is enabled, send email when a new message is received and the user is not currently on the conversation.

Debounce/bundle to avoid spam (e.g., one email per conversation per X minutes).

In-app notification

Show toast/badge/unread indicators for new messages; if the chat window is open but a different conversation is selected, surface a subtle desktop/browser notification (when permission granted).

Search

Single search box that can filter by: email, name, company name, message content.

Works across Contacts and Conversations.

Supports partial matches; highlight matches in results.

Non-Functional & Architecture

Backend entities: User(id, name, email, company), Conversation(id, participant_ids, last_message_at), Message(id, conversation_id, sender_id, text, attachments[], created_at), Attachment(id, message_id, filename, content_type, size, storage_url, checksum), UserSettings(user_id, message_notifications_email:boolean).

APIs:

REST: auth me, list/create conversations, list messages (paginated), upload/download attachments (signed URLs if needed), search endpoint, settings get/update.

WebSocket: join user channel, subscribe to conversation channels, events: message.new, conversation.updated, typing.start/stop (optional), read.receipt (optional).

Security: authenticated routes, per-conversation authorization, attachment access control, CSRF for REST, rate limits on send/search/upload.

Performance: infinite scroll for messages, lazy attachment preview, sensible indexes on search fields.

Frontend UX Details

Chat layout: left sidebar (Conversations + unread badges + search), main panel (thread), top bar (participant info), bottom composer (emoji + attachment + send).

Conversation tab: sticky composer at bottom; auto-scroll to bottom on new message; preserve scroll position when loading older history.

Contacts tab: list with avatar, name, company, email; hover shows Send message.

Default open last conversation behavior must be deterministic and tested.

Keyboard: Enter to send (Shift+Enter newline).

Error states and retry for failed sends/uploads.

Tests & Quality Gates (REQUIRED)

Playwright E2E in e2e/ (must run headless in CI):

Loads /chat, verifies last conversation auto-opens, input focused, scrolled to bottom.

Send text message; appears instantly in sender UI; appears in receiver UI via WebSocket without reload.

Contacts hover displays Send message; clicking switches to Conversation tab, opens the right contact, focuses input.

Emoji insert into composer and send; renders correctly on both sides.

File upload (image and non-image): preview or download link visible; receiver can download/view.

Search by email, name, company, and message text; results filter correctly; highlights shown.

Notification: with a different conversation selected, receiving a message shows toast/badge; if permission granted, browser notification appears.

Settings: enable “message notifications: email”; send a message while user is not in that conversation; assert a mocked email send occurred (via test double or capture in backend logs).

Unit/Integration tests:

Backend: message creation, attachment validation, search query behavior, WebSocket fan-out, permissions.

Frontend: store/reducer/hooks for conversations/messages, search utilities, attachment helpers.

Type checks:

frontend: tsc --noEmit with strict mode.

backend: mypy --strict.

Lint/format:

eslint + prettier for frontend, ruff/black for backend.

Build logs (must be visible in CI and stored as artifacts):

Frontend build (vite build) and backend build/packaging.

Docker logs check:

In CI, after docker compose up -d, tail and assert health checks pass.

Export container logs as artifacts; fail CI on obvious errors (tracebacks, unhandled rejections).

CI pipeline (GitHub Actions or similar):

Jobs: typecheck, lint, backend-tests, frontend-tests, e2e-playwright, docker-build-run, collect-logs.

Cache dependencies; run services via docker-compose.ci.yml with seeded users/conversations.

Observability & DevX

Add structured logging (JSON) for message send, ws broadcast, email notification attempts.

Health endpoints and WebSocket ping/pong.

Seed script to create demo users, contacts, and a few conversations + attachments.

Deliverables

Production-ready code implementing all features above.

Playwright tests fulfilling all E2E scenarios.

Unit/integration tests with good coverage for critical paths.

Docker Compose for local + CI; scripts to run migrations and seed.

CI configuration with artifacts for build logs and docker logs.

Developer README with run/test commands and troubleshooting.

Acceptance Criteria (must all pass)

All functional requirements behave exactly as specified.

Playwright suite is green in CI headless mode.

Type checks (tsc, mypy) pass with strict settings.

Lint/format pass.

Docker images build and run; health checks green; logs uploaded.

Search returns correct results across email, name, company, message.

No UI for phone/video calling exists anywhere.

Now proceed to implement and wire everything end-to-end, updating only the necessary files, and provide concise commit messages per logical change.