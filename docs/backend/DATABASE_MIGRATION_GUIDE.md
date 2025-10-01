# Database Migration: Jobs to Positions

**Last Updated**: October 2025


## Overview
This migration renames the `jobs` and `job_applications` tables to `positions` and `position_applications` respectively, along with updating all related indexes and foreign keys.

## Files Created
- `alembic/versions/002_rename_jobs_to_positions.py` - Main migration script
- `scripts/verify_migration.py` - Post-migration verification script
- `scripts/README_MIGRATION.md` - This documentation

## Pre-Migration Checklist
- [ ] Backup your database
- [ ] Ensure development environment is set up
- [ ] Stop any running application instances
- [ ] Test on a copy of production data first

## Running the Migration

### Step 1: Backup Database
```bash
# Example for MySQL
mysqldump -u username -p database_name > backup_before_migration.sql
```

### Step 2: Run Migration
```bash
cd backend
python -m alembic upgrade head
```

### Step 3: Verify Migration
```bash
cd backend
python scripts/verify_migration.py
```

### Step 4: Test New Endpoints
```bash
# Test positions endpoint
python -m pytest app/tests/test_positions.py -v

# Test backward compatibility
python -m pytest app/tests/test_jobs.py -v
```

## What the Migration Does

### Tables Renamed
- `jobs` → `positions`
- `job_applications` → `position_applications`

### Columns Updated
- `position_applications.job_id` → `position_applications.position_id`

### Indexes Renamed
- `idx_jobs_*` → `idx_positions_*`
- `idx_applications_job_status` → `idx_applications_position_status`

### Foreign Keys Updated
- All foreign key constraints updated to reference new table/column names

## Rollback Instructions

If you need to rollback the migration:

```bash
cd backend
python -m alembic downgrade -1
```

This will:
1. Rename tables back to original names
2. Restore original column names
3. Restore original indexes
4. Restore original foreign key constraints

## Verification Points

The verification script checks:
- ✅ New tables exist (`positions`, `position_applications`)
- ✅ Old tables are removed (`jobs`, `job_applications`)
- ✅ Data is preserved (row counts match)
- ✅ Foreign key relationships work
- ✅ New indexes are created
- ✅ Old indexes are removed

## Troubleshooting

### Migration Fails
1. Check database connection
2. Ensure you have proper permissions
3. Check for conflicting migrations (multiple heads)
4. Verify table structure matches expected schema

### Verification Fails
1. Check the verification script output for specific errors
2. Manually verify table existence: `SHOW TABLES;`
3. Check foreign key constraints: `SHOW CREATE TABLE position_applications;`
4. Verify indexes: `SHOW INDEX FROM positions;`

### Rollback Issues
1. Ensure no application is using the new table names
2. Check for any custom code that might prevent rollback
3. Manual rollback may be required if automatic rollback fails

## Post-Migration Steps

After successful migration:
1. ✅ Update application configuration if needed
2. ✅ Test all API endpoints
3. ✅ Update frontend to use new API structure
4. ✅ Run full test suite
5. ✅ Deploy to staging environment
6. ✅ Perform user acceptance testing

## Support

If you encounter issues:
1. Check the migration logs
2. Run the verification script for detailed diagnostics
3. Consult the main migration documentation in `JOBS_TO_POSITIONS_MIGRATION.md`
