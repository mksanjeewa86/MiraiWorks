# Jobs to Positions Migration Plan

## Overview

This document outlines the comprehensive migration plan to rename the "jobs" system to "positions" throughout the MiraiWorks application while maintaining proper separation between admin/posting functions and public job viewing.

## Current State Analysis

### Backend Structure
- **Database**: `jobs` table with complete job posting data
- **API**: `/api/jobs/` endpoints for all job operations
- **Models**: `Job`, `JobApplication`, `CompanyProfile` classes
- **Schemas**: `job.py` with comprehensive Pydantic models
- **CRUD**: `job.py` with all database operations
- **Tests**: `test_jobs.py` for API testing

### Frontend Structure
- **Admin Interface**: `/positions` page with mock data for job management
- **Public Interface**: `/jobs` page consuming backend jobs API
- **API Client**: `jobsApi` for backend communication

## Migration Strategy

### Phase 1: Backend Database Migration

#### 1.1 Database Table Rename
```sql
-- Rename main table
ALTER TABLE jobs RENAME TO positions;

-- Rename application table
ALTER TABLE job_applications RENAME TO position_applications;

-- Update foreign key references
ALTER TABLE position_applications
CHANGE COLUMN job_id position_id int NOT NULL;

-- Update indexes
DROP INDEX idx_jobs_company_status;
CREATE INDEX idx_positions_company_status ON positions(company_id, status);

DROP INDEX idx_jobs_published;
CREATE INDEX idx_positions_published ON positions(published_at, status);

DROP INDEX idx_jobs_location_type;
CREATE INDEX idx_positions_location_type ON positions(country, city, job_type);

DROP INDEX idx_jobs_experience_remote;
CREATE INDEX idx_positions_experience_remote ON positions(experience_level, remote_type);

DROP INDEX idx_jobs_featured_status;
CREATE INDEX idx_positions_featured_status ON positions(is_featured, status, published_at);

-- Update application indexes
DROP INDEX idx_applications_job_status;
CREATE INDEX idx_applications_position_status ON position_applications(position_id, status);
```

#### 1.2 Model Refactoring
**File**: `backend/app/models/position.py` (renamed from job.py)

```python
class Position(Base):
    __tablename__ = "positions"

    # All existing fields remain the same
    # Update relationships:
    applications = relationship(
        "PositionApplication", back_populates="position", cascade="all, delete-orphan"
    )

class PositionApplication(Base):
    __tablename__ = "position_applications"

    position_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("positions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationship updates
    position = relationship("Position", back_populates="applications")
```

### Phase 2: Backend API Migration

#### 2.1 Schema Updates
**File**: `backend/app/schemas/position.py` (renamed from job.py)

```python
# Rename all schemas while maintaining functionality:
class PositionStatus(str, Enum):  # was JobStatus
class PositionType(str, Enum):    # was JobType
class PositionBase(BaseModel):    # was JobBase
class PositionCreate(BaseModel):  # was JobCreate
class PositionUpdate(BaseModel):  # was JobUpdate
class PositionInfo(BaseModel):    # was JobInfo

# Application schemas
class PositionApplicationBase(BaseModel):   # was JobApplicationBase
class PositionApplicationCreate(BaseModel): # was JobApplicationCreate
class PositionApplicationInfo(BaseModel):   # was JobApplicationInfo

# Response schemas
class PositionListResponse(BaseModel):     # was JobListResponse
class PositionSearchResponse(BaseModel):   # was JobSearchResponse
class PositionStatsResponse(BaseModel):    # was JobStatsResponse
```

#### 2.2 CRUD Layer Updates
**File**: `backend/app/crud/position.py` (renamed from job.py)

```python
from app.models.position import Position, PositionApplication
from app.schemas.position import PositionCreate, PositionUpdate

class CRUDPosition(CRUDBase[Position, PositionCreate, PositionUpdate]):
    # Rename all methods while maintaining functionality
    async def get_published_positions(self, db: AsyncSession, **kwargs):
        # was get_published_jobs

    async def get_positions_by_status(self, db: AsyncSession, **kwargs):
        # was get_jobs_by_status

    async def get_popular_positions(self, db: AsyncSession, **kwargs):
        # was get_popular_jobs

position = CRUDPosition(Position)  # was job = CRUDJob(Job)
```

#### 2.3 API Endpoints Migration
**File**: `backend/app/endpoints/positions.py` (renamed from jobs.py)

```python
# Single unified endpoint with permission-based filtering

@router.get("/positions", response_model=PositionListResponse)
async def get_positions(
    # Search and filter parameters
    search: Optional[str] = Query(None, description="Search in title, description, company"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
    salary_min: Optional[int] = Query(None, description="Minimum salary filter"),
    salary_max: Optional[int] = Query(None, description="Maximum salary filter"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    status: Optional[str] = Query(None, description="Filter by status"),

    # Pagination
    skip: int = Query(0, ge=0, description="Number of positions to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of positions to return"),

    # Access control
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    """
    Get positions with different access levels:
    - Public access: only published positions with filtered data
    - Admin access: all positions with full data including sensitive fields
    """

    # Determine access level
    is_admin_access = current_user and (current_user.is_admin or current_user.company_id)

    if not is_admin_access:
        # Public access: force published status and filter sensitive data
        status = "published"
        positions = await position_crud.get_published_positions(
            db=db, search=search, location=location, job_type=job_type,
            experience_level=experience_level, salary_min=salary_min,
            salary_max=salary_max, company_id=company_id, skip=skip, limit=limit
        )
        # Filter response to exclude sensitive admin data
        filtered_positions = [
            {
                "id": p.id,
                "title": p.title,
                "company_name": p.company.name if p.company else None,
                "location": p.location,
                "job_type": p.job_type,
                "experience_level": p.experience_level,
                "remote_type": p.remote_type,
                "description": p.description,
                "requirements": p.requirements,
                "salary_range_display": p.salary_range_display if p.show_salary else None,
                "published_at": p.published_at,
                "application_deadline": p.application_deadline,
                "is_featured": p.is_featured,
                "is_urgent": p.is_urgent,
                # Exclude: salary_min/max, application_count, view_count, etc.
            }
            for p in positions
        ]
        return PositionListResponse(positions=filtered_positions, total=len(filtered_positions))
    else:
        # Admin access: full data with company filtering for non-admin users
        if not current_user.is_admin and current_user.company_id:
            company_id = current_user.company_id  # Force user's company only

        positions = await position_crud.get_positions_by_filters(
            db=db, search=search, location=location, job_type=job_type,
            experience_level=experience_level, salary_min=salary_min,
            salary_max=salary_max, company_id=company_id, status=status,
            skip=skip, limit=limit
        )
        return PositionListResponse(positions=positions, total=len(positions))

@router.post("/positions", response_model=PositionInfo)
async def create_position(
    position_in: PositionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new position (admin/employer only)"""

@router.get("/positions/{position_id}", response_model=PositionInfo)
async def get_position(
    position_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get position by ID with access-level appropriate data"""

@router.put("/positions/{position_id}", response_model=PositionInfo)
async def update_position(
    position_id: int,
    position_in: PositionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update position (admin/employer only)"""

@router.delete("/positions/{position_id}")
async def delete_position(
    position_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete position (admin only)"""
```

### Phase 3: Frontend Migration

#### 3.1 API Client Updates
**File**: `frontend/src/api/positions.ts` (unified API client)

```typescript
import type { ApiResponse, Position, PositionCreate, PositionUpdate } from '@/types';
import { API_CONFIG } from '@/config/api';

// Unified positions API for both admin and public access
export const positionsApi = {
  // Public access (no authentication required)
  getPublic: async (filters?: {
    search?: string;
    location?: string;
    job_type?: string;
    experience_level?: string;
    salary_min?: number;
    salary_max?: number;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ positions: Position[]; total: number }>> => {
    const url = new URL(`${API_CONFIG.BASE_URL}/api/positions`);

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          url.searchParams.set(key, value.toString());
        }
      });
    }

    const response = await fetch(url.toString(), {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  // Admin access (authentication required)
  getAll: async (filters?: {
    search?: string;
    location?: string;
    job_type?: string;
    experience_level?: string;
    status?: string;
    company_id?: number;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ positions: Position[]; total: number }>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_CONFIG.BASE_URL}/api/positions`);

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          url.searchParams.set(key, value.toString());
        }
      });
    }

    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  getById: async (id: number, isAuthenticated: boolean = false): Promise<ApiResponse<Position>> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (isAuthenticated) {
      const token = localStorage.getItem('accessToken');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    const response = await fetch(`${API_CONFIG.BASE_URL}/api/positions/${id}`, {
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  create: async (positionData: PositionCreate): Promise<ApiResponse<Position>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/positions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(positionData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  update: async (id: number, positionData: PositionUpdate): Promise<ApiResponse<Position>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/positions/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(positionData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  delete: async (id: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/positions/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return { data: undefined, success: true };
  },
};

// Legacy jobsApi for backward compatibility (remove after migration)
export const jobsApi = {
  getPublic: positionsApi.getPublic,
  getById: (id: number) => positionsApi.getById(id, false),
  search: (query: string, filters?: any) =>
    positionsApi.getPublic({ search: query, ...filters }),
};
```

#### 3.2 Frontend Page Updates
**File**: `frontend/src/app/positions/page.tsx`

```typescript
// Update to use real backend data via positionsApi
import { positionsApi } from '@/api/positions';
import type { Position } from '@/types/position';

function PositionsPageContent() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        setLoading(true);
        setError('');

        // Use admin API with authentication for full position data
        const response = await positionsApi.getAll({
          // Include filters for status, company, etc.
          limit: 50
        });
        setPositions(response.data.positions);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch positions');
        console.error('Failed to fetch positions:', err);
        setPositions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
  }, []);

  // Remove all mock data - now uses real backend data
  // Keep existing UI components but remove mockPositions array
}
```

**File**: `frontend/src/app/jobs/page.tsx`

```typescript
// Update to use new positionsApi but for public access
import { positionsApi } from '@/api/positions';
import type { Position } from '@/types/position';

function JobsPageContent() {
  const [jobs, setJobs] = useState<Position[]>([]);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        setError('');

        const filters = {
          search: searchQuery || undefined,
          location: selectedLocation !== 'all' ? selectedLocation : undefined,
          job_type: selectedType !== 'all' ? selectedType : undefined,
          limit: 50
        };

        // Use public API (no authentication) - gets filtered data
        const response = await positionsApi.getPublic(filters);
        setJobs(response.data.positions || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
        console.error('Failed to fetch jobs:', err);
        setJobs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [searchQuery, selectedLocation, selectedType]);

  // Rest of component remains the same - just data source changed
}
```

### Phase 4: Testing Migration

#### 4.1 Backend Test Updates
**File**: `backend/app/tests/test_positions.py` (renamed from test_jobs.py)

```python
# Update all test functions and fixtures
def test_create_position():  # was test_create_job
def test_get_positions():    # was test_get_jobs
def test_update_position():  # was test_update_job
def test_delete_position():  # was test_delete_job

# Add compatibility tests
def test_jobs_api_backward_compatibility():
    """Test that /api/jobs endpoints still work"""

def test_public_job_viewing():
    """Test that public job viewing works via /api/jobs"""
```

#### 4.2 Integration Tests
```python
def test_full_position_workflow():
    """Test complete position lifecycle from creation to application"""

def test_frontend_backend_integration():
    """Test that frontend can consume both positions and jobs APIs"""
```

### Phase 5: Database Migration Scripts

#### 5.1 Alembic Migration
**File**: `backend/alembic/versions/xxx_rename_jobs_to_positions.py`

```python
def upgrade():
    # Rename tables
    op.rename_table('jobs', 'positions')
    op.rename_table('job_applications', 'position_applications')

    # Update foreign key column names
    op.alter_column('position_applications', 'job_id', new_column_name='position_id')

    # Recreate indexes with new names
    op.drop_index('idx_jobs_company_status')
    op.create_index('idx_positions_company_status', 'positions', ['company_id', 'status'])

    # Update all other indexes similarly

def downgrade():
    # Reverse all changes for rollback capability
```

#### 5.2 Data Migration Verification
```python
def verify_migration():
    """Verify data integrity after migration"""
    # Check row counts match
    # Verify foreign key relationships
    # Test API endpoints
```

### Phase 6: Configuration and Deployment

#### 6.1 Environment Variables
```bash
# Update any job-related environment variables
POSITION_UPLOAD_PATH=/uploads/positions  # was JOB_UPLOAD_PATH
MAX_POSITIONS_PER_COMPANY=50            # was MAX_JOBS_PER_COMPANY
```

#### 6.2 File Structure Updates
```
backend/app/
├── models/
│   ├── position.py (renamed from job.py)
│   └── ...
├── schemas/
│   ├── position.py (renamed from job.py)
│   └── ...
├── crud/
│   ├── position.py (renamed from job.py)
│   └── ...
├── endpoints/
│   ├── positions.py (renamed from jobs.py)
│   └── ...
├── tests/
│   ├── test_positions.py (renamed from test_jobs.py)
│   └── ...
└── workers/
    ├── positions_files.py (renamed from jobs_files.py)
    └── ...

frontend/src/
├── api/
│   ├── positions.ts (new)
│   ├── jobs.ts (updated for public use only)
│   └── ...
├── types/
│   ├── position.ts (new)
│   ├── job.ts (updated for public use only)
│   └── ...
└── app/
    ├── positions/ (admin - updated to use real API)
    ├── jobs/ (public - unchanged)
    └── ...
```

## Implementation Checklist

### Pre-Migration
- [ ] Backup production database
- [ ] Create feature branch
- [ ] Set up testing environment
- [ ] Document current API endpoints

### Database Migration
- [ ] Create Alembic migration script
- [ ] Test migration on development database
- [ ] Verify data integrity after migration
- [ ] Update database indexes and constraints

### Backend Code Migration
- [ ] Rename model files and classes
- [ ] Update schema files and classes
- [ ] Migrate CRUD operations
- [ ] Update API endpoints with dual routing
- [ ] Update all imports and references

### Frontend Code Migration
- [ ] Create new positions API client
- [ ] Update positions page to use real backend data
- [ ] Update job types and interfaces
- [ ] Test both admin and public interfaces

### Testing
- [ ] Update all existing tests
- [ ] Add backward compatibility tests
- [ ] Add integration tests
- [ ] Test migration rollback procedures

### Documentation
- [ ] Update API documentation
- [ ] Update deployment guides
- [ ] Create migration runbook
- [ ] Update user documentation

### Deployment
- [ ] Deploy to staging environment
- [ ] Run comprehensive tests
- [ ] Deploy to production with rollback plan
- [ ] Monitor for issues
- [ ] Deprecation notices for old endpoints

## Backward Compatibility Strategy

### Immediate Support (6 months)
- All `/api/jobs` endpoints continue to work
- Frontend jobs page continues to function
- Existing mobile apps continue to work

### Deprecation Period (6-12 months)
- Add deprecation warnings to `/api/jobs` responses
- Update documentation to recommend `/api/positions`
- Notify external API consumers

### Final Migration (12+ months)
- Remove deprecated `/api/jobs` admin endpoints
- Keep `/api/jobs` public viewing endpoints for semantic clarity
- Complete migration to positions terminology

## Risk Mitigation

### Data Loss Prevention
- Complete database backup before migration
- Test migration on production copy
- Rollback scripts ready
- Data verification procedures

### API Compatibility
- Dual routing during transition
- Gradual deprecation process
- Clear migration timeline
- External consumer notification

### Testing Coverage
- 100% test coverage for new endpoints
- Integration tests for both interfaces
- Load testing for public job search
- User acceptance testing

## Success Metrics

### Technical Metrics
- Zero data loss during migration
- 100% API backward compatibility during transition
- All tests passing after migration
- No performance degradation

### Business Metrics
- No disruption to job posting workflow
- No disruption to job searching functionality
- Successful migration of all existing data
- User satisfaction maintained

## Timeline

### Week 1-2: Preparation
- Database analysis and migration script creation
- Backend code refactoring
- Test environment setup

### Week 3-4: Implementation
- Database migration execution
- Backend API implementation
- Frontend updates

### Week 5-6: Testing
- Comprehensive testing
- Performance validation
- User acceptance testing

### Week 7-8: Deployment
- Staging deployment
- Production deployment
- Monitoring and optimization

## Notes

- This migration maintains semantic clarity: "positions" for job management, "jobs" for public job search
- Backward compatibility ensures no disruption to existing integrations
- The migration follows the project's architectural guidelines strictly
- All changes maintain the existing security and performance characteristics