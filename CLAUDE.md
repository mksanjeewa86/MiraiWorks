# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MiraiWorks is a modern HR & recruitment management platform built with FastAPI (Python) backend and React/TypeScript frontend. The system supports candidates, recruiters, and employers with real-time messaging, calendar sync, resume building, and secure interview scheduling.

## Architecture

This is a microservices-oriented monorepo with the following structure:
- `backend/` - FastAPI application with SQLAlchemy, MySQL, Redis, Celery
- `frontend/` - React + TypeScript + Tailwind CSS application 
- `platform/` - Docker infrastructure services (MySQL, Redis, MinIO, ClamAV, Mailpit)
- `docs/` - Living documentation that must stay synchronized with code

## Development Commands

### Backend Development
```bash
# From backend/ directory
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Run tests
pytest
pytest --cov=app --cov-report=html

# Run worker processes (background tasks)
celery -A app.workers.queue worker --loglevel=info
```

### Frontend Development
```bash
# From frontend/ directory  
npm install
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # ESLint
npm run typecheck    # TypeScript checking
npm test             # Vitest unit tests
npm run test:e2e     # Playwright end-to-end tests
```

### Infrastructure
```bash
# From platform/ directory
docker-compose up -d     # Start all services
docker-compose down      # Stop all services
docker-compose logs -f   # View logs

# From project root
./scripts/dev-up.sh      # Start development environment
./scripts/lint.sh        # Lint all code
```

## Key Technical Patterns

### Security & RBAC Implementation
- **Company Scoping**: Every request must validate user belongs to correct company context
- **Role-Based Access**: Use `@requires_permission` decorators from `utils/permissions.py`
- **Input Validation**: All API inputs validated through Pydantic schemas
- **2FA Enforcement**: Required for all admin users via email verification codes
- **Audit Logging**: Use `audit_service.py` for tracking admin actions

### Messaging System Constraints
- **Allowed Communications**:
  - Candidate ↔ Recruiter (direct)
  - Employer ↔ Recruiter (direct)
- **Blocked Communications**:
  - Candidate ↔ Employer (must go through Recruiter)
- **File Security**: All uploads go through ClamAV virus scanning before availability

### Real-time Features
- WebSocket connections managed in `routers/messaging_ws.py`
- Use Redis pub/sub for horizontal scaling of real-time features
- Message delivery receipts and typing indicators supported

### External Integrations
- **Calendar Sync**: Bi-directional with Google Calendar and Microsoft Graph APIs
- **Storage**: MinIO S3-compatible storage with presigned URLs
- **Email**: Mailpit for development, configurable SMTP for production
- **SSO**: Google and Microsoft OAuth (only for existing users, no auto-provisioning)

## Environment Configuration

### Required Environment Variables
All configuration comes from environment variables (no hardcoded values):

**Backend (.env):**
- `DB_URL` - MySQL connection string
- `REDIS_URL` - Redis connection
- `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET` - MinIO configuration
- `CLAMAV_HOST`, `CLAMAV_PORT` - Antivirus service
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM` - Email configuration
- `JWT_SECRET`, `JWT_ACCESS_TTL_MIN`, `JWT_REFRESH_TTL_DAYS` - Auth tokens
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` - SSO
- `MS_OAUTH_CLIENT_ID`, `MS_OAUTH_CLIENT_SECRET` - SSO

**Frontend (.env):**
- `VITE_API_URL` - Backend API base URL
- `VITE_WS_URL` - WebSocket URL for real-time features

## Testing Requirements

### Backend Tests (`pytest`)
- Unit tests for all services and utilities
- Integration tests for API endpoints with company scoping
- WebSocket real-time messaging tests
- Mock external services (SMTP, S3, ClamAV) in test environment
- Coverage requirement: ≥80%

### Frontend Tests
- **Unit/Component**: Vitest + React Testing Library
- **End-to-End**: Playwright for critical user journeys
- Test authentication flows, real-time messaging, calendar integration

## Implementation Phases

The project follows a phased development approach:

1. **Phase 0**: Core configuration, database setup, RBAC foundation
2. **Phase 1**: Authentication, user management, admin capabilities  
3. **Phase 2**: Real-time messaging with file upload security
4. **Phase 3**: Calendar integrations and interview scheduling
5. **Phase 4**: Resume builder with PDF generation
6. **Phase 5**: Role-specific dashboards and public website
7. **Phase 6**: CI/CD pipeline and security hardening

## Code Quality Standards

### Backend
- Use SQLAlchemy ORM exclusively (no raw SQL)
- Pydantic schemas for all API request/response validation
- Async/await patterns throughout
- Dependency injection for database sessions and external services
- Comprehensive error handling with appropriate HTTP status codes

### Frontend  
- TypeScript strict mode enabled
- Component composition over inheritance
- Custom hooks for business logic
- Proper error boundaries and loading states
- Accessible UI components following WCAG guidelines

## Documentation Requirements

Keep `docs/` folder synchronized with code changes:
- `ARCHITECTURE.md` - High-level system design
- `API.md` - OpenAPI/Swagger documentation  
- `MESSAGING_RULES.md` - Communication flow constraints
- `SECURITY.md` - Security implementation details
- `ADR/` - Architecture Decision Records

## CI/CD Pipeline

GitHub Actions workflows:
- **ci.yml**: Run tests, linting, type checking for both backend and frontend
- **docs-check.yml**: Ensure documentation stays current with API changes
- Coverage gates and quality checks must pass before merge

## Development Workflow

1. Never commit secrets or API keys
2. Use feature branches with descriptive names
3. Keep commits small and focused
4. Update tests and documentation in the same PR as code changes
5. All admin actions must generate audit log entries
6. Validate RBAC and company scoping on new endpoints
7. Test real-time features across multiple browser sessions
8. Verify file upload security flow (upload → scan → availability)