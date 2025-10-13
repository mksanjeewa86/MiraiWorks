# MiraiWorks AI Development Guidelines

## Project Overview
MiraiWorks is a comprehensive HR management system built with FastAPI (backend) and Next.js (frontend), featuring recruitment workflows, candidate management, and interview scheduling capabilities.

## Core Architecture

### Backend Structure (`backend/app/`)
- `models/`: SQLAlchemy models ONLY - database schema definitions
- `schemas/`: Pydantic schemas + enums - ALL type definitions and validation
- `crud/`: Database operations ONLY - SQLAlchemy queries
- `endpoints/`: HTTP routing logic ONLY - FastAPI routes
- `services/`: Business logic and orchestration
- `utils/`: Shared utilities

### Frontend Structure (`frontend/src/`)
- `api/`: API client functions ONLY
- `components/`: React components (props interfaces stay inline)
- `contexts/`: React contexts
- `hooks/`: Custom React hooks
- `types/`: TypeScript type definitions ONLY
- `app/`: Next.js app router pages

## Critical Patterns & Conventions

### Backend Patterns
1. **Layer Separation**:
   - Database models → `models/`
   - Type definitions → `schemas/`
   - Database queries → `crud/`
   - HTTP routing → `endpoints/`
   - Business logic → `services/`

2. **Testing Requirements**:
   - 100% test coverage for endpoints
   - Test files in `app/tests/`
   - Comprehensive scenarios (auth, validation, edge cases)
   - Example: `backend/app/tests/test_exam_endpoint.py`

### Frontend Patterns
1. **Type Management**:
   - ALL shared types in `types/` folder
   - Props interfaces stay in component files
   - Group domain types (e.g., `types/user.ts`, `types/interview.ts`)

2. **API Organization**:
   - Endpoints alphabetically ordered in `api/config.ts`
   - API functions grouped by domain in `api/` folder
   - Use via hooks, never direct API calls in components

## Development Workflow

### Environment Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Testing Commands
```bash
# Backend Tests
cd backend
PYTHONPATH=. python -m pytest app/tests/ -v --cov=app

# Frontend Tests
cd frontend
npm run test
npm run typecheck
npm run lint
```

### Database Operations
- Migrations handled by Alembic
- Access test database with test credentials:
  - Admin: admin@miraiworks.com
  - Company Admin: admin@techcorp.jp
  - Recruiter: recruiter1@techcorp.jp
  - Password: Any password works in demo mode

## Key Integration Points

### Authentication Flow
1. JWT token-based auth with refresh tokens
2. 2FA support built-in
3. Role-based access control (RBAC)
4. Endpoints require `Authorization` header

### External Dependencies
- Redis for caching and sessions
- MinIO/S3 for file storage
- PostgreSQL for production database
- SQLite available for development

## Common Pitfalls

### Backend
- Don't define enums in models (use `schemas/`)
- Don't write queries in endpoints (use `crud/`)
- Don't mix business logic with HTTP routing
- Example violation:
  ```python
  # ❌ Don't do this in endpoints
  @router.get("/jobs")
  async def get_jobs(db: AsyncSession):
      result = await db.execute(select(Job))  # Move to crud!
  ```

### Frontend
- Don't define shared types in components
- Don't make API calls directly in components
- Keep business logic in hooks/services
- Example violation:
  ```typescript
  // ❌ Don't do this in components
  useEffect(() => {
    fetch('/api/users')  // Use API client via hooks!
      .then(res => res.json())
      .then(setUsers);
  }, []);
  ```

## Cross-Component Communication

1. **Frontend-Backend Integration**:
   - API client in `frontend/src/api/`
   - Type definitions shared via OpenAPI schema
   - Error handling standardized through `ApiResponse` type

2. **State Management**:
   - React Context for global state
   - Custom hooks for data fetching
   - Redis for session state
   - MinIO/S3 for file storage

## Project-Specific Conventions
1. **File Organization**:
   - Feature-first organization in both frontend and backend
   - Test files adjacent to implementation
   - Types centralized in dedicated folders

2. **Naming Conventions**:
   - Backend: Snake case for Python
   - Frontend: Camel case for TypeScript
   - Database: Snake case for columns
   - API endpoints: Kebab case for URLs