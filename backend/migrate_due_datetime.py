"""
Direct SQL migration script to merge due_date and due_time into due_datetime
This bypasses Alembic and applies the schema changes directly.
"""
import os

from sqlalchemy import create_engine, inspect, text

# Get database URL from environment or use default for docker
DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+aiomysql://miraiworks:miraiworks@db:3306/miraiworks"
).replace("+aiomysql", "+pymysql")

print("Connecting to database...")
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

# Get current columns
columns = {col["name"]: col for col in inspector.get_columns("todos")}
print("\nCurrent columns in 'todos' table:")
for name in sorted(columns.keys()):
    if "due" in name:
        col = columns[name]
        print(f"  {name}: {col['type']} (nullable={col['nullable']})")

# Check current state
has_due_date = "due_date" in columns
has_due_time = "due_time" in columns
has_due_datetime = "due_datetime" in columns

print("\nCurrent state:")
print(f"  has due_date: {has_due_date}")
print(f"  has due_time: {has_due_time}")
print(f"  has due_datetime: {has_due_datetime}")

with engine.begin() as conn:
    if has_due_datetime and (has_due_date or has_due_time):
        print("\n⚠️  INCONSISTENT STATE DETECTED!")
        print(
            "Both old and new columns exist. This migration was probably partially applied."
        )
        print("Dropping due_datetime to start fresh...")
        conn.execute(text("ALTER TABLE todos DROP COLUMN due_datetime"))
        has_due_datetime = False
        print("✓ Dropped due_datetime column")

    if not has_due_datetime and (has_due_date or has_due_time):
        print("\n📝 Applying migration: merge due_date + due_time → due_datetime")

        # Step 1: Add due_datetime column
        print("  1. Adding due_datetime column...")
        conn.execute(
            text(
                """
            ALTER TABLE todos
            ADD COLUMN due_datetime DATETIME NULL
        """
            )
        )
        print("  ✓ Added due_datetime column")

        # Step 2: Migrate data
        print("  2. Migrating data...")
        result = conn.execute(
            text(
                """
            UPDATE todos
            SET due_datetime = CASE
                WHEN due_date IS NOT NULL AND due_time IS NOT NULL THEN
                    CAST(CONCAT(due_date, ' ', due_time) AS DATETIME)
                WHEN due_date IS NOT NULL AND due_time IS NULL THEN
                    CAST(CONCAT(due_date, ' 23:59:59') AS DATETIME)
                ELSE NULL
            END
        """
            )
        )
        print(f"  ✓ Migrated {result.rowcount} rows")

        # Step 3: Drop old columns
        if has_due_time:
            print("  3. Dropping due_time column...")
            conn.execute(text("ALTER TABLE todos DROP COLUMN due_time"))
            print("  ✓ Dropped due_time column")

        if has_due_date:
            print("  4. Dropping due_date column...")
            conn.execute(text("ALTER TABLE todos DROP COLUMN due_date"))
            print("  ✓ Dropped due_date column")

        print("\n✅ Migration completed successfully!")

    elif has_due_datetime and not has_due_date and not has_due_time:
        print("\n✅ Migration already applied - nothing to do")

    else:
        print("\n⚠️  Unexpected state - manual intervention required")

# Verify final state
inspector = inspect(engine)
columns = {col["name"]: col for col in inspector.get_columns("todos")}
print("\nFinal columns in 'todos' table:")
for name in sorted(columns.keys()):
    if "due" in name:
        col = columns[name]
        print(f"  {name}: {col['type']} (nullable={col['nullable']})")

print("\nDone!")
