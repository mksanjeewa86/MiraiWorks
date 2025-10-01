# Calendar System Migration Plan

## Current State Analysis

### Existing Tables
- **`synced_events`** - External calendar events (Google/Outlook sync)
- **`holidays`** - Holiday data (recently added)
- **No dedicated internal events table**

### Current Event Sources
1. External calendar events (`synced_events` table)
2. Holidays (`holidays` table)
3. Test events (in-memory storage for development)

## Migration Goals

### 1. Create Unified Calendar Events Table
Create a new `calendar_events` table to store all internal calendar events.

### 2. Consolidate Event Display
Modify calendar endpoints to properly handle all event types:
- Internal events (`calendar_events`)
- External events (`synced_events`)
- Holidays (`holidays`)

## Database Schema Changes

### New Table: `calendar_events`
```sql
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
    is_all_day BOOLEAN DEFAULT FALSE,
    location VARCHAR(255),
    event_type VARCHAR(50) DEFAULT 'event', -- 'event', 'meeting', 'task', etc.
    status VARCHAR(20) DEFAULT 'confirmed', -- 'confirmed', 'tentative', 'cancelled'
    creator_id INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    recurrence_rule VARCHAR(255), -- For recurring events
    parent_event_id INTEGER REFERENCES calendar_events(id), -- For recurring instances
    timezone VARCHAR(50) DEFAULT 'UTC'
);
```

### Indexes to Add
```sql
CREATE INDEX idx_calendar_events_start_datetime ON calendar_events(start_datetime);
CREATE INDEX idx_calendar_events_creator_id ON calendar_events(creator_id);
CREATE INDEX idx_calendar_events_status ON calendar_events(status);
CREATE INDEX idx_calendar_events_event_type ON calendar_events(event_type);
```

## File Changes Required

### 1. Backend Model
- **Create**: `backend/app/models/calendar_event.py`
- Define SQLAlchemy model for `calendar_events` table

### 2. Backend Schema
- **Create**: `backend/app/schemas/calendar_event.py`
- Pydantic schemas for request/response
- Event type and status enums

### 3. Backend CRUD
- **Create**: `backend/app/crud/calendar_event.py`
- CRUD operations for calendar events
- Date range queries, filtering by type/status

### 4. Backend Service
- **Create**: `backend/app/services/calendar_service.py`
- Business logic for calendar operations
- Event creation, updating, deletion
- Recurring event handling

### 5. Backend Endpoints
- **Modify**: `backend/app/endpoints/calendar.py`
- Add CRUD endpoints for internal events
- Consolidate event retrieval from all sources
- Remove in-memory test storage

### 6. Database Migration
- **Create**: `backend/alembic/versions/add_calendar_events_table.py`
- Alembic migration script

### 7. Frontend Types
- **Modify**: `frontend/src/types/calendar.ts`
- Add types for internal calendar events
- Update existing event interfaces

### 8. Frontend API
- **Create**: `frontend/src/api/calendar.ts`
- API client for calendar event operations

### 9. Frontend Components
- **Modify**: `frontend/src/components/calendar/CalendarView.tsx`
- Remove test event handling
- Update event creation flow

## Migration Steps

### Phase 1: Database Setup
1. Create new `calendar_events` table migration
2. Run migration to add table and indexes
3. Verify table structure

### Phase 2: Backend Implementation
1. Create model, schema, and CRUD files
2. Implement calendar service logic
3. Add new API endpoints
4. Update existing calendar endpoint to use new table
5. Remove in-memory test storage

### Phase 3: Frontend Updates
1. Update TypeScript types
2. Create calendar API client
3. Update calendar components
4. Test event creation/editing flows

### Phase 4: Testing & Validation
1. Test all calendar operations
2. Verify event display from all sources
3. Test recurring events (if implemented)
4. Performance testing with large datasets

### Phase 5: Cleanup
1. Remove old test event code
2. Update documentation
3. Add proper error handling
4. Optimize queries if needed

## API Endpoints to Add

```
GET    /api/calendar/events          - Get all calendar events
POST   /api/calendar/events          - Create new event
GET    /api/calendar/events/{id}     - Get specific event
PUT    /api/calendar/events/{id}     - Update event
DELETE /api/calendar/events/{id}     - Delete event
GET    /api/calendar/events/range    - Get events in date range
POST   /api/calendar/events/bulk     - Create multiple events
```

## Event Type Integration

### Current Event Sources (Post-Migration)
1. **Internal Events**: `calendar_events` table
   - User-created events
   - Meetings, appointments, tasks
   - Company events

2. **External Events**: `synced_events` table
   - Google Calendar sync
   - Outlook sync
   - Other provider integrations

3. **System Events**: `holidays` table
   - National holidays
   - Company holidays
   - Special dates

### Event ID Prefixing
- Internal events: `event-{id}`
- External events: `sync-{id}`
- Holidays: `holiday-{id}`
- Test events: Remove completely

## Considerations

### Data Migration
- No existing data migration needed (new table)
- Test events are temporary and can be discarded

### Performance
- Add proper indexing for date-based queries
- Consider pagination for large date ranges
- Optimize calendar view queries

### Permissions
- Add user-based event permissions
- Support for shared/public events
- Calendar access control

### Recurring Events
- Consider implementing basic recurrence rules
- Store recurring patterns in `recurrence_rule` field
- Create individual instances or calculate on-the-fly

## Rollback Plan
If migration issues occur:
1. Drop `calendar_events` table
2. Revert endpoint changes to use in-memory storage
3. Restore previous calendar component state

## Testing Strategy
- Unit tests for new CRUD operations
- Integration tests for calendar endpoints
- Frontend component testing
- End-to-end calendar workflow testing

---

**Status**: Planning Phase
**Next Step**: Create database migration file
**Estimated Effort**: 2-3 development days
**Priority**: Medium