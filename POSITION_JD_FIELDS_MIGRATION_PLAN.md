# Position JD Fields Migration Plan

## Overview
This document outlines the migration plan to add comprehensive job description fields from JD.md to the positions functionality in MiraiWorks.

**Created**: 2025-10-22
**Status**: Planning Phase
**Target Version**: TBD

---

## Analysis of JD.md Structure

### Identified Field Categories

#### 1. **Company Information**
- Company name (already exists via `company_id` relationship)
- Company HP/Website
- Stock market listing (e.g., "東証グロース上場")
- Representative/CEO name
- Founded year (exists in CompanyProfile)
- Employee count (exists in CompanyProfile)
- Capital amount
- Average age
- Main shareholders
- Business description/About company

#### 2. **Job Overview Sections**
- Job summary (職務概要) - similar to existing `summary`
- Job details (職務詳細) - part of existing `description`
- Product/Service being worked on (製品)
- Assigned tasks (担当業務)

#### 3. **Technical Environment** (新規フィールド必要)
- Programming languages/technologies
- Frameworks
- Infrastructure
- Database
- Development process/methodology
- Test coverage
- IDE/Tools

#### 4. **Company Features/Culture** (新規フィールド必要)
- Company mission/vision
- Business model description
- Company history
- Market position

#### 5. **Requirements** (既存フィールド拡張)
- Required skills (応募条件スキル【必須】)
- Preferred skills (応募条件スキル【尚可】)
- Soft skills (応募条件ソフト面)

#### 6. **Work Details** (新規フィールド必要)
- Department/Team (配属部署)
- Career plan (キャリアプラン)
- Work location with detailed address
- Transportation/Access
- Work hours with flexibility details
- Break time
- Overtime hours (average per month)

#### 7. **Compensation Details** (既存フィールド拡張)
- Salary range (existing)
- Fixed overtime allowance details
- Bonus structure
- Raise schedule (昇給)

#### 8. **Employment Terms** (新規フィールド必要)
- Employment type (雇用形態)
- Trial period details
- Contract period

#### 9. **Holidays & Leave** (新規フィールド必要)
- Annual holidays count
- Weekend schedule
- Paid leave
- Special leaves (年末年始休暇, リフレッシュ休暇, etc.)

#### 10. **Benefits & Welfare** (既存フィールド拡張)
- Detailed benefits list
- Book purchase subsidy
- Certification support
- Health checkups
- Stock options
- Dress code

#### 11. **Insurance** (新規フィールド必要)
- Health insurance
- Pension
- Workers compensation
- Employment insurance

#### 12. **Selection Process** (新規フィールド必要)
- Selection flow (書類選考 → 面接 → 内定)
- Interview stages
- Aptitude tests

---

## Proposed New Database Fields

### A. Position Model Extensions

#### Technical Environment Fields
```python
# New fields for position model
tech_stack: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    # Example: ["TypeScript", "Vue.js", "Ruby on Rails"]

frontend_tech: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
backend_tech: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
infrastructure: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
database_tech: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

development_process: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Description of dev methodology (Agile, Scrum, etc.)

test_coverage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # e.g., "rspec 94%"

ide_tools: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
```

#### Work Environment & Schedule Fields
```python
assigned_team: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 配属部署 details

career_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    # キャリアプラン description

detailed_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Full address with building name

transportation_access: Mapped[str | None] = mapped_column(Text, nullable=True)
    # e.g., "東京メトロ東西線「飯田橋」駅より徒歩3分"

work_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # e.g., "9:00～18:00／10:00～19:00"

flex_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
flex_time_details: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # e.g., "コアタイム：11時00分～15時00分"

break_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Default: 60

average_overtime_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Average per month
```

#### Compensation Details Extensions
```python
base_salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Separated from fixed overtime

fixed_overtime_allowance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 固定残業手当

fixed_overtime_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # e.g., 45 hours

bonus_structure: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # e.g., "決算賞与", "年2回"

raise_schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # e.g., "年1回"
```

#### Employment Terms Fields
```python
employment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full_time")
    # 正社員, 契約社員, etc.

trial_period_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
trial_period_conditions: Mapped[str | None] = mapped_column(String(500), nullable=True)

contract_period: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # For contract positions
```

#### Holidays & Leave Fields
```python
annual_holidays: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # e.g., 120

weekend_schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # e.g., "完全週休2日制(土日祝日)"

paid_leave_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

special_leaves: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    # ["年末年始休暇", "リフレッシュ休暇", "慶弔特別休暇", etc.]
```

#### Insurance Fields
```python
health_insurance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
pension_insurance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
workers_compensation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
employment_insurance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

#### Selection Process Fields
```python
selection_process: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    # ["書類選考", "一次面接", "適性検査", "二次面接", "最終面接", "内定"]

interview_stages_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
has_aptitude_test: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
aptitude_test_details: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

#### Extended Benefits Fields
```python
book_purchase_support: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
certification_support: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
health_checkup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
stock_options_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
stock_options_details: Mapped[str | None] = mapped_column(String(500), nullable=True)
dress_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # e.g., "私服勤務（内勤時）"

business_trip_allowance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
```

---

## Migration Steps

### Phase 1: Database Schema Changes

#### Step 1.1: Create Alembic Migration
```bash
cd backend
docker exec -it miraiworks_backend alembic revision --autogenerate -m "add_jd_fields_to_positions"
```

#### Step 1.2: Review Generated Migration
- Review `backend/alembic/versions/[hash]_add_jd_fields_to_positions.py`
- Verify all new columns are included
- Add any custom SQL for data transformations if needed

#### Step 1.3: Add Indexes
Add indexes for frequently queried fields:
```python
Index("idx_positions_flex_time", "flex_time"),
Index("idx_positions_remote_flex", "remote_type", "flex_time"),
Index("idx_positions_employment_type", "employment_type"),
```

#### Step 1.4: Run Migration
```bash
docker exec -it miraiworks_backend alembic upgrade head
```

### Phase 2: Backend Code Updates

#### Step 2.1: Update Position Model (`backend/app/models/position.py`)
- Add all new Mapped fields as listed above
- Update `__table_args__` with new indexes
- Add validation properties if needed

#### Step 2.2: Update Position Schemas (`backend/app/schemas/position.py`)

Add new enums:
```python
class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    CONTRACT = "contract"
    PART_TIME = "part_time"
    TEMPORARY = "temporary"
    DISPATCH = "dispatch"

class WeekendSchedule(str, Enum):
    TWO_DAYS_OFF = "two_days_off"  # 完全週休2日制
    TWO_DAYS_OFF_VARIABLE = "two_days_off_variable"  # 週休2日制
    ONE_DAY_OFF = "one_day_off"
    SHIFT = "shift"
```

Update `PositionBase` schema:
```python
class PositionBase(BaseModel):
    # ... existing fields ...

    # Technical environment
    tech_stack: list[str] | None = None
    frontend_tech: list[str] | None = None
    backend_tech: list[str] | None = None
    infrastructure: list[str] | None = None
    database_tech: list[str] | None = None
    development_process: Optional[str] = None
    test_coverage: Optional[str] = None
    ide_tools: list[str] | None = None

    # Work environment
    assigned_team: Optional[str] = None
    career_plan: Optional[str] = None
    detailed_address: Optional[str] = None
    transportation_access: Optional[str] = None
    work_hours: Optional[str] = None
    flex_time: bool = False
    flex_time_details: Optional[str] = None
    break_time_minutes: Optional[int] = Field(None, ge=0, le=180)
    average_overtime_hours: Optional[int] = Field(None, ge=0, le=200)

    # Compensation details
    base_salary_min: Optional[int] = Field(None, ge=0)
    fixed_overtime_allowance: Optional[int] = Field(None, ge=0)
    fixed_overtime_hours: Optional[int] = Field(None, ge=0, le=60)
    bonus_structure: Optional[str] = None
    raise_schedule: Optional[str] = None

    # Employment terms
    employment_type: str = "full_time"
    trial_period_months: Optional[int] = Field(None, ge=0, le=12)
    trial_period_conditions: Optional[str] = None
    contract_period: Optional[str] = None

    # Holidays
    annual_holidays: Optional[int] = Field(None, ge=0, le=365)
    weekend_schedule: Optional[str] = None
    paid_leave_days: Optional[int] = Field(None, ge=0, le=40)
    special_leaves: list[str] | None = None

    # Insurance
    health_insurance: bool = True
    pension_insurance: bool = True
    workers_compensation: bool = True
    employment_insurance: bool = True

    # Selection process
    selection_process: list[str] | None = None
    interview_stages_count: Optional[int] = Field(None, ge=0, le=10)
    has_aptitude_test: bool = False
    aptitude_test_details: Optional[str] = None

    # Extended benefits
    book_purchase_support: bool = False
    certification_support: bool = False
    health_checkup: bool = True
    stock_options_available: bool = False
    stock_options_details: Optional[str] = None
    dress_code: Optional[str] = None
    business_trip_allowance: bool = False
```

#### Step 2.3: Update CRUD Operations (`backend/app/crud/position.py`)
- No changes needed (generic CRUD handles new fields automatically)
- Consider adding search/filter methods for new fields if needed

#### Step 2.4: Update Services (`backend/app/services/position_service.py`)
- Add business logic for validating new fields
- Add helper methods for formatting/parsing complex fields

#### Step 2.5: Update Endpoints (`backend/app/endpoints/positions.py`)
- Endpoints should work automatically with updated schemas
- Add query parameters for filtering by new fields if needed

### Phase 3: Frontend Code Updates

#### Step 3.1: Update TypeScript Types (`frontend/src/types/position.ts`)
```typescript
export interface Position {
  // ... existing fields ...

  // Technical environment
  tech_stack?: string[];
  frontend_tech?: string[];
  backend_tech?: string[];
  infrastructure?: string[];
  database_tech?: string[];
  development_process?: string;
  test_coverage?: string;
  ide_tools?: string[];

  // Work environment
  assigned_team?: string;
  career_plan?: string;
  detailed_address?: string;
  transportation_access?: string;
  work_hours?: string;
  flex_time?: boolean;
  flex_time_details?: string;
  break_time_minutes?: number;
  average_overtime_hours?: number;

  // Compensation details
  base_salary_min?: number;
  fixed_overtime_allowance?: number;
  fixed_overtime_hours?: number;
  bonus_structure?: string;
  raise_schedule?: string;

  // Employment terms
  employment_type?: string;
  trial_period_months?: number;
  trial_period_conditions?: string;
  contract_period?: string;

  // Holidays
  annual_holidays?: number;
  weekend_schedule?: string;
  paid_leave_days?: number;
  special_leaves?: string[];

  // Insurance
  health_insurance?: boolean;
  pension_insurance?: boolean;
  workers_compensation?: boolean;
  employment_insurance?: boolean;

  // Selection process
  selection_process?: string[];
  interview_stages_count?: number;
  has_aptitude_test?: boolean;
  aptitude_test_details?: string;

  // Extended benefits
  book_purchase_support?: boolean;
  certification_support?: boolean;
  health_checkup?: boolean;
  stock_options_available?: boolean;
  stock_options_details?: string;
  dress_code?: string;
  business_trip_allowance?: boolean;
}
```

#### Step 3.2: Update Position Forms
Create new form sections in position creation/edit forms:
- Technical Environment section
- Work Schedule & Location section
- Compensation Details section
- Employment Terms section
- Benefits & Welfare section
- Selection Process section

#### Step 3.3: Update Position Display Components
Update position detail view to display new fields in organized sections:
- `components/positions/PositionDetail.tsx`
- `components/positions/PositionCard.tsx`
- `components/positions/PositionTechStack.tsx` (new)
- `components/positions/PositionWorkDetails.tsx` (new)

#### Step 3.4: Update API Client (`frontend/src/api/positions.ts`)
- API should work automatically with updated types
- Add filters for new fields if needed

### Phase 4: Testing

#### Step 4.1: Backend Tests
```bash
# Create test file
backend/tests/test_position_jd_fields.py

# Test areas:
- Model field validation
- Schema serialization/deserialization
- CRUD operations with new fields
- API endpoints with new fields
```

#### Step 4.2: Frontend Tests
- Test form validation for new fields
- Test display of new fields
- Test filtering/searching with new fields

#### Step 4.3: Integration Tests
- Test end-to-end position creation with all new fields
- Test position editing
- Test position display in various contexts

### Phase 5: Data Migration (Optional)

If you have existing positions and want to populate some fields:

```sql
-- Example: Set default values for insurance fields
UPDATE positions
SET
  health_insurance = true,
  pension_insurance = true,
  workers_compensation = true,
  employment_insurance = true
WHERE health_insurance IS NULL;

-- Set default employment type
UPDATE positions
SET employment_type = 'full_time'
WHERE employment_type IS NULL AND status != 'archived';
```

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review this migration plan with team
- [ ] Identify which fields are MVP vs future enhancements
- [ ] Create tickets for each phase
- [ ] Backup production database

### Phase 1: Database
- [ ] Create Alembic migration
- [ ] Review migration file
- [ ] Test migration on development database
- [ ] Run migration on staging
- [ ] Verify schema changes
- [ ] Add indexes

### Phase 2: Backend
- [ ] Update Position model
- [ ] Update Position schemas
- [ ] Add enums for new field types
- [ ] Update CRUD (if needed)
- [ ] Update services (if needed)
- [ ] Write unit tests
- [ ] Test API endpoints

### Phase 3: Frontend
- [ ] Update TypeScript types
- [ ] Create/update form components
- [ ] Create/update display components
- [ ] Update API client
- [ ] Add validation
- [ ] Write component tests

### Phase 4: Testing
- [ ] Backend unit tests
- [ ] Backend integration tests
- [ ] Frontend component tests
- [ ] E2E tests
- [ ] Manual testing

### Phase 5: Deployment
- [ ] Deploy to staging
- [ ] QA testing on staging
- [ ] Run data migration scripts (if needed)
- [ ] Deploy to production
- [ ] Monitor for errors
- [ ] Document new fields for users

---

## Risk Assessment

### High Risk
- **Database migration failure**: Mitigate by testing on staging first, having rollback plan
- **Performance impact**: Many new fields could slow queries - addressed by adding indexes

### Medium Risk
- **Data loss**: Ensure backups before migration
- **Frontend/Backend version mismatch**: Deploy backend first, ensure backward compatibility

### Low Risk
- **Form complexity**: Too many fields might overwhelm users - consider progressive disclosure
- **Field validation conflicts**: Thoroughly test validation rules

---

## Rollback Plan

If issues arise after deployment:

1. **Database Rollback**:
   ```bash
   docker exec -it miraiworks_backend alembic downgrade -1
   ```

2. **Code Rollback**:
   - Revert to previous Git commit
   - Redeploy previous version

3. **Data Recovery**:
   - Restore from backup if data corruption occurs

---

## Timeline Estimate

- **Phase 1 (Database)**: 1-2 days
- **Phase 2 (Backend)**: 3-4 days
- **Phase 3 (Frontend)**: 5-7 days
- **Phase 4 (Testing)**: 3-4 days
- **Phase 5 (Deployment)**: 1 day

**Total**: 13-18 working days (approximately 3-4 weeks)

---

## Notes

### Optional Enhancements
Consider these additional features in future iterations:

1. **JD Template System**: Create templates for common job types (engineer, designer, etc.)
2. **AI-Powered JD Generation**: Use AI to suggest field values based on job title
3. **Multi-language Support**: Support Japanese and English job descriptions
4. **JD Preview**: Show how the job posting will look before publishing
5. **Import from External Sources**: Import JDs from other platforms

### Field Priority
Consider implementing in stages:

**Stage 1 (MVP)**:
- Technical environment fields
- Work schedule fields
- Extended compensation fields

**Stage 2**:
- Selection process fields
- Detailed benefits fields

**Stage 3**:
- Insurance fields (if not standard)
- Optional/nice-to-have fields

---

## References

- Original JD: `JD.md`
- Position Model: `backend/app/models/position.py`
- Position Schema: `backend/app/schemas/position.py`
- Architecture Rules: `CLAUDE.md`
- Testing Guidelines: `.github/copilot-instructions.md`

---

**Document Version**: 1.0
**Last Updated**: 2025-10-22
**Author**: Claude Code Migration Planning
**Status**: Ready for Review
