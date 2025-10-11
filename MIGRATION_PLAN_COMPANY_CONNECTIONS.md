# Migration Plan: User Connections → Company Connections

## 📋 Executive Summary

**Goal**: Migrate from individual user-to-user connections to company-based connections where:
- Users/Companies connect with Companies (not individual users)
- Any user from a connected company can interact with users from the other connected entity
- Example: Candidate A → Company B means any user in Company B can message Candidate A

---

## 🎯 New Connection Model

### Connection Types

1. **User-to-Company Connection**
   - Individual user (e.g., Candidate) → Company
   - All users in that company can interact with the individual

2. **Company-to-Company Connection**
   - Company A → Company B
   - All users in Company A can interact with all users in Company B

### Use Cases

```
✅ Candidate A connects with Recruitment Company A
   → Any recruiter in Company A can message Candidate A

✅ Recruitment Company B connects with Employer Company A
   → Any user in Company B can interact with any user in Company A

✅ Individual Freelancer connects with Agency Company
   → All agents can interact with the freelancer
```

---

## 📊 Database Schema Design

### New Table: `company_connections`

```sql
CREATE TABLE company_connections (
    id INT PRIMARY KEY AUTO_INCREMENT,

    -- Source entity (can be user or company)
    source_type ENUM('user', 'company') NOT NULL COMMENT 'Type of source entity',
    source_user_id INT NULL COMMENT 'If source is a user',
    source_company_id INT NULL COMMENT 'If source is a company',

    -- Target entity (always a company)
    target_company_id INT NOT NULL COMMENT 'Target company',

    -- Connection metadata
    is_active BOOLEAN DEFAULT TRUE,
    connection_type VARCHAR(50) DEFAULT 'standard' COMMENT 'standard, partnership, etc',

    -- Permissions (for future expansion)
    can_message BOOLEAN DEFAULT TRUE,
    can_view_profile BOOLEAN DEFAULT TRUE,
    can_assign_tasks BOOLEAN DEFAULT FALSE,

    -- Creation tracking
    creation_type VARCHAR(20) NOT NULL DEFAULT 'manual' COMMENT 'manual, automatic, api',
    created_by INT NULL COMMENT 'User who created this connection',

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (source_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (source_company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (target_company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_source_user (source_user_id, is_active),
    INDEX idx_source_company (source_company_id, is_active),
    INDEX idx_target_company (target_company_id, is_active),
    INDEX idx_created_by (created_by),

    -- Constraints
    CONSTRAINT chk_source_entity CHECK (
        (source_type = 'user' AND source_user_id IS NOT NULL AND source_company_id IS NULL) OR
        (source_type = 'company' AND source_company_id IS NOT NULL AND source_user_id IS NULL)
    ),
    CONSTRAINT unique_user_company_connection UNIQUE (source_user_id, target_company_id),
    CONSTRAINT unique_company_connection UNIQUE (source_company_id, target_company_id)
);
```

### Keep `user_connections` for Direct User Connections (Optional)

For backward compatibility or special cases where direct user-to-user connections are needed:

```sql
-- Keep the existing table but mark it as legacy
ALTER TABLE user_connections
ADD COLUMN is_legacy BOOLEAN DEFAULT TRUE COMMENT 'Legacy connection from old system';
```

---

## 🔄 Migration Strategy

### Phase 1: Preparation (Week 1)

#### 1.1 Create New Schema
- ✅ Create `company_connections` table
- ✅ Add migration script with rollback capability
- ✅ Test on development database

#### 1.2 Implement New Models
```python
# backend/app/models/company_connection.py
class CompanyConnection(Base):
    """Company-based connections for messaging and interactions."""
    __tablename__ = "company_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Source entity
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    source_company_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("companies.id"))

    # Target company
    target_company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    can_message: Mapped[bool] = mapped_column(Boolean, default=True)
    can_view_profile: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    source_user: Mapped["User | None"] = relationship("User", foreign_keys=[source_user_id])
    source_company: Mapped["Company | None"] = relationship("Company", foreign_keys=[source_company_id])
    target_company: Mapped["Company"] = relationship("Company", foreign_keys=[target_company_id])
```

---

### Phase 2: Data Migration (Week 2)

#### 2.1 Analyze Existing Connections

```sql
-- Query to analyze existing connections
SELECT
    uc.id,
    u1.id as user1_id,
    u1.email as user1_email,
    u1.company_id as user1_company,
    u2.id as user2_id,
    u2.email as user2_email,
    u2.company_id as user2_company,
    uc.is_active,
    uc.creation_type
FROM user_connections uc
JOIN users u1 ON uc.user_id = u1.id
JOIN users u2 ON uc.connected_user_id = u2.id
ORDER BY uc.created_at;
```

#### 2.2 Migration Logic

```python
# backend/scripts/migrate_to_company_connections.py
async def migrate_user_connections_to_company_connections(db: AsyncSession):
    """
    Migrate existing user connections to new company connection model.

    Rules:
    1. If both users are in the same company → Skip (internal connection)
    2. If user1 has no company and user2 has company → User-to-Company
    3. If both users have different companies → Company-to-Company
    4. If neither has a company → Keep as legacy user connection
    """

    # Get all existing connections
    result = await db.execute(
        select(UserConnection)
        .options(
            selectinload(UserConnection.user),
            selectinload(UserConnection.connected_user)
        )
    )
    old_connections = result.scalars().all()

    migrated_count = 0
    skipped_count = 0
    legacy_count = 0

    for conn in old_connections:
        user1 = conn.user
        user2 = conn.connected_user

        # Same company - skip (internal connection)
        if user1.company_id and user1.company_id == user2.company_id:
            skipped_count += 1
            continue

        # User1 no company, User2 has company → User-to-Company
        if not user1.company_id and user2.company_id:
            new_conn = CompanyConnection(
                source_type='user',
                source_user_id=user1.id,
                target_company_id=user2.company_id,
                is_active=conn.is_active,
                creation_type=conn.creation_type,
                created_by=conn.created_by,
                created_at=conn.created_at
            )
            db.add(new_conn)
            migrated_count += 1

        # User2 no company, User1 has company → User-to-Company
        elif not user2.company_id and user1.company_id:
            new_conn = CompanyConnection(
                source_type='user',
                source_user_id=user2.id,
                target_company_id=user1.company_id,
                is_active=conn.is_active,
                creation_type=conn.creation_type,
                created_by=conn.created_by,
                created_at=conn.created_at
            )
            db.add(new_conn)
            migrated_count += 1

        # Both have companies → Company-to-Company
        elif user1.company_id and user2.company_id:
            # Check if connection already exists
            existing = await db.execute(
                select(CompanyConnection).where(
                    or_(
                        and_(
                            CompanyConnection.source_company_id == user1.company_id,
                            CompanyConnection.target_company_id == user2.company_id
                        ),
                        and_(
                            CompanyConnection.source_company_id == user2.company_id,
                            CompanyConnection.target_company_id == user1.company_id
                        )
                    )
                )
            )
            if not existing.scalar_one_or_none():
                new_conn = CompanyConnection(
                    source_type='company',
                    source_company_id=user1.company_id,
                    target_company_id=user2.company_id,
                    is_active=conn.is_active,
                    creation_type=conn.creation_type,
                    created_by=conn.created_by,
                    created_at=conn.created_at
                )
                db.add(new_conn)
                migrated_count += 1

        # Both have no company → Keep as legacy
        else:
            legacy_count += 1

    await db.commit()

    return {
        'migrated': migrated_count,
        'skipped': skipped_count,
        'legacy': legacy_count
    }
```

---

### Phase 3: Backend Implementation (Week 3)

#### 3.1 New Service Layer

```python
# backend/app/services/company_connection_service.py
class CompanyConnectionService:
    """Service for managing company-based connections."""

    async def can_users_interact(
        self,
        db: AsyncSession,
        user1_id: int,
        user2_id: int
    ) -> bool:
        """
        Check if two users can interact based on company connections.

        Returns True if:
        1. Same company
        2. User1 is connected to User2's company
        3. User2 is connected to User1's company
        4. User1's company is connected to User2's company
        """

        # Get both users with companies
        result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id.in_([user1_id, user2_id]))
        )
        users = result.scalars().all()

        if len(users) != 2:
            return False

        user1, user2 = users[0], users[1]

        # Same company - always allowed
        if user1.company_id and user1.company_id == user2.company_id:
            return True

        # Check company connections
        query = select(CompanyConnection).where(
            CompanyConnection.is_active == True,
            or_(
                # User1 → Company2
                and_(
                    CompanyConnection.source_type == 'user',
                    CompanyConnection.source_user_id == user1_id,
                    CompanyConnection.target_company_id == user2.company_id
                ),
                # User2 → Company1
                and_(
                    CompanyConnection.source_type == 'user',
                    CompanyConnection.source_user_id == user2_id,
                    CompanyConnection.target_company_id == user1.company_id
                ),
                # Company1 ↔ Company2
                and_(
                    CompanyConnection.source_type == 'company',
                    or_(
                        and_(
                            CompanyConnection.source_company_id == user1.company_id,
                            CompanyConnection.target_company_id == user2.company_id
                        ),
                        and_(
                            CompanyConnection.source_company_id == user2.company_id,
                            CompanyConnection.target_company_id == user1.company_id
                        )
                    )
                )
            )
        )

        result = await db.execute(query)
        connection = result.scalar_one_or_none()

        return connection is not None

    async def connect_user_to_company(
        self,
        db: AsyncSession,
        user_id: int,
        company_id: int,
        created_by: int
    ) -> CompanyConnection:
        """Connect an individual user to a company."""

        # Check if already connected
        existing = await db.execute(
            select(CompanyConnection).where(
                CompanyConnection.source_user_id == user_id,
                CompanyConnection.target_company_id == company_id
            )
        )

        if existing.scalar_one_or_none():
            raise ValueError("Connection already exists")

        connection = CompanyConnection(
            source_type='user',
            source_user_id=user_id,
            target_company_id=company_id,
            is_active=True,
            creation_type='manual',
            created_by=created_by
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        return connection

    async def connect_companies(
        self,
        db: AsyncSession,
        company1_id: int,
        company2_id: int,
        created_by: int
    ) -> CompanyConnection:
        """Connect two companies together."""

        if company1_id == company2_id:
            raise ValueError("Cannot connect a company to itself")

        # Check if already connected (either direction)
        existing = await db.execute(
            select(CompanyConnection).where(
                CompanyConnection.source_type == 'company',
                or_(
                    and_(
                        CompanyConnection.source_company_id == company1_id,
                        CompanyConnection.target_company_id == company2_id
                    ),
                    and_(
                        CompanyConnection.source_company_id == company2_id,
                        CompanyConnection.target_company_id == company1_id
                    )
                )
            )
        )

        if existing.scalar_one_or_none():
            raise ValueError("Connection already exists")

        connection = CompanyConnection(
            source_type='company',
            source_company_id=company1_id,
            target_company_id=company2_id,
            is_active=True,
            creation_type='manual',
            created_by=created_by
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        return connection

    async def get_connected_users(
        self,
        db: AsyncSession,
        user_id: int
    ) -> list[User]:
        """
        Get all users that the given user can interact with.
        Based on company connections.
        """

        # Get user with company
        result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return []

        connected_company_ids = []

        # Get companies user is connected to (as individual)
        user_conns = await db.execute(
            select(CompanyConnection.target_company_id).where(
                CompanyConnection.source_type == 'user',
                CompanyConnection.source_user_id == user_id,
                CompanyConnection.is_active == True
            )
        )
        connected_company_ids.extend([row[0] for row in user_conns.fetchall()])

        # Get companies user's company is connected to
        if user.company_id:
            company_conns = await db.execute(
                select(
                    case(
                        (CompanyConnection.source_company_id == user.company_id,
                         CompanyConnection.target_company_id),
                        else_=CompanyConnection.source_company_id
                    ).label('company_id')
                ).where(
                    CompanyConnection.source_type == 'company',
                    or_(
                        CompanyConnection.source_company_id == user.company_id,
                        CompanyConnection.target_company_id == user.company_id
                    ),
                    CompanyConnection.is_active == True
                )
            )
            connected_company_ids.extend([row[0] for row in company_conns.fetchall()])

        # Get users from connected companies
        if not connected_company_ids:
            return []

        users_result = await db.execute(
            select(User)
            .where(
                User.company_id.in_(connected_company_ids),
                User.is_active == True,
                User.id != user_id
            )
            .options(selectinload(User.company))
            .order_by(User.first_name, User.last_name)
        )

        return users_result.scalars().all()

company_connection_service = CompanyConnectionService()
```

#### 3.2 Update Message Validation

```python
# backend/app/endpoints/messages.py
async def validate_messaging_permission(
    db: AsyncSession, sender_id: int, recipient_id: int
):
    """Validate that sender can message recipient using company connections."""

    # Check if users can interact based on company connections
    can_interact = await company_connection_service.can_users_interact(
        db, sender_id, recipient_id
    )

    if not can_interact:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only message users from connected companies"
        )
```

---

### Phase 4: API Endpoints (Week 4)

#### 4.1 New Endpoints

```python
# backend/app/endpoints/company_connections.py
router = APIRouter()

@router.post("/company-connections/user-to-company")
async def connect_user_to_company(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect current user to a company."""
    connection = await company_connection_service.connect_user_to_company(
        db, current_user.id, company_id, current_user.id
    )
    return {"message": "Connected successfully", "connection_id": connection.id}

@router.post("/company-connections/company-to-company")
async def connect_companies(
    company1_id: int,
    company2_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect two companies (admin only)."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    connection = await company_connection_service.connect_companies(
        db, company1_id, company2_id, current_user.id
    )
    return {"message": "Companies connected successfully", "connection_id": connection.id}

@router.get("/company-connections/my-connections")
async def get_my_company_connections(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all company connections for current user."""
    users = await company_connection_service.get_connected_users(db, current_user.id)
    return {"users": users, "total": len(users)}
```

---

### Phase 5: Frontend Updates (Week 5)

#### 5.1 Update Connection UI

```typescript
// frontend/src/api/companyConnections.ts
export const companyConnectionsApi = {
  async connectToCompany(companyId: number): Promise<ApiResponse<{ connection_id: number }>> {
    const response = await apiClient.post('/api/company-connections/user-to-company', {
      company_id: companyId
    });
    return { data: response.data, success: true };
  },

  async connectCompanies(company1Id: number, company2Id: number): Promise<ApiResponse<{ connection_id: number }>> {
    const response = await apiClient.post('/api/company-connections/company-to-company', {
      company1_id: company1Id,
      company2_id: company2Id
    });
    return { data: response.data, success: true };
  },

  async getConnectedUsers(): Promise<ApiResponse<User[]>> {
    const response = await apiClient.get('/api/company-connections/my-connections');
    return { data: response.data.users, success: true };
  }
};
```

#### 5.2 Update Messages Page

```typescript
// Update contacts loading to use new company connections
const loadContacts = async () => {
  const response = await companyConnectionsApi.getConnectedUsers();
  setContacts(response.data);
};
```

---

## 🧪 Testing Strategy

### Unit Tests
- ✅ Test company connection creation
- ✅ Test user-to-company connection
- ✅ Test company-to-company connection
- ✅ Test interaction permission checking
- ✅ Test duplicate connection prevention

### Integration Tests
- ✅ Test message sending with company connections
- ✅ Test connection listing
- ✅ Test permission validation

### Migration Tests
```python
async def test_migration_user_to_company():
    """Test migration of user connection to company connection."""
    # Create old connection
    old_conn = UserConnection(user_id=1, connected_user_id=2)

    # Run migration
    await migrate_user_connections_to_company_connections(db)

    # Verify new connection exists
    new_conn = await db.execute(
        select(CompanyConnection).where(
            CompanyConnection.source_user_id == 1
        )
    )
    assert new_conn.scalar_one_or_none() is not None
```

---

## 📅 Timeline

| Phase | Duration | Deliverables |
|-------|----------|-------------|
| **Phase 1: Preparation** | Week 1 | Schema design, new models, migration scripts |
| **Phase 2: Data Migration** | Week 2 | Migration script, data validation |
| **Phase 3: Backend** | Week 3 | Service layer, CRUD operations |
| **Phase 4: API** | Week 4 | New endpoints, update existing endpoints |
| **Phase 5: Frontend** | Week 5 | UI updates, API integration |
| **Phase 6: Testing** | Week 6 | Comprehensive testing, bug fixes |
| **Phase 7: Deployment** | Week 7 | Staging deployment, production rollout |

---

## 🚨 Rollback Plan

### If Migration Fails

1. **Keep Old Table**
   - Don't drop `user_connections` table immediately
   - Keep for 30 days after successful migration

2. **Feature Flag**
   ```python
   USE_COMPANY_CONNECTIONS = os.getenv('USE_COMPANY_CONNECTIONS', 'false') == 'true'

   if USE_COMPANY_CONNECTIONS:
       # Use new system
       can_interact = await company_connection_service.can_users_interact(db, u1, u2)
   else:
       # Use old system
       can_interact = await user_connection_service.are_users_connected(db, u1, u2)
   ```

3. **Rollback Script**
   ```python
   async def rollback_to_user_connections():
       """Rollback from company connections to user connections."""
       # Recreate user connections from company connections
       # Drop company_connections table
       # Re-enable old code paths
   ```

---

## ✅ Success Criteria

1. **✅ All existing user connections migrated successfully**
2. **✅ No data loss during migration**
3. **✅ Message sending works with new system**
4. **✅ Performance equal or better than old system**
5. **✅ All tests passing (unit, integration, E2E)**
6. **✅ Documentation updated**
7. **✅ Zero downtime deployment**

---

## 📝 Next Steps

1. **Review this plan** with team
2. **Approve database schema** design
3. **Set up development environment** for testing
4. **Create detailed task breakdown** in project management tool
5. **Assign responsibilities** to team members
6. **Begin Phase 1** implementation

---

## 🔗 Related Documents

- Current user_connections schema: `backend/app/models/user_connection.py`
- Message validation: `backend/app/endpoints/messages.py`
- User connection service: `backend/app/services/user_connection_service.py`

---

**Last Updated**: 2025-10-11
**Status**: Planning Phase
**Version**: 1.0
