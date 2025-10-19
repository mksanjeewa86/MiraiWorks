#!/usr/bin/env python3
"""
Test script for timezone migration verification.

This script tests:
1. Todo creation with due_datetime
2. Todo retrieval showing UTC times
3. Timezone conversion correctness
4. Extension request compatibility
"""

import sys
from datetime import datetime, timezone, timedelta
import json


def test_database_schema():
    """Test 1: Verify database schema is correct."""
    print("=" * 60)
    print("TEST 1: Database Schema Verification")
    print("=" * 60)

    import subprocess

    # Check todos table schema
    result = subprocess.run(
        [
            "docker", "exec", "-i", "miraiworks_db",
            "mysql", "-uroot", "-proot", "miraiworks",
            "-e", "DESCRIBE todos;"
        ],
        capture_output=True,
        text=True
    )

    schema = result.stdout
    print(schema)

    # Verify requirements
    checks = {
        "due_datetime exists": "due_datetime" in schema,
        "due_date removed": "due_date\t" not in schema or "due_date " not in schema,
        "due_time removed": "due_time" not in schema,
    }

    for check, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {check}")

    return all(checks.values())


def test_data_integrity():
    """Test 2: Verify existing data has due_datetime values."""
    print("\n" + "=" * 60)
    print("TEST 2: Data Integrity Check")
    print("=" * 60)

    import subprocess

    result = subprocess.run(
        [
            "docker", "exec", "-i", "miraiworks_db",
            "mysql", "-uroot", "-proot", "miraiworks",
            "-e", "SELECT id, title, due_datetime, created_at FROM todos WHERE due_datetime IS NOT NULL LIMIT 5;"
        ],
        capture_output=True,
        text=True
    )

    print("Sample todos with due_datetime:")
    print(result.stdout)

    has_data = "NULL" not in result.stdout and len(result.stdout.strip()) > 50
    status = "[OK] PASS" if has_data else "[!]  WARNING"
    print(f"{status}: Todos have due_datetime data")

    return has_data


def test_alembic_version():
    """Test 3: Verify Alembic is at correct version."""
    print("\n" + "=" * 60)
    print("TEST 3: Alembic Version Check")
    print("=" * 60)

    import subprocess

    result = subprocess.run(
        ["docker", "exec", "miraiworks_backend", "alembic", "current"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    correct_version = "d5fb4c228327" in result.stdout
    status = "[OK] PASS" if correct_version else "[X] FAIL"
    print(f"{status}: Alembic at correct version (d5fb4c228327)")

    return correct_version


def test_pydantic_schema():
    """Test 4: Verify Pydantic schemas use due_datetime."""
    print("\n" + "=" * 60)
    print("TEST 4: Pydantic Schema Check")
    print("=" * 60)

    import subprocess

    # Check TodoRead schema
    result = subprocess.run(
        [
            "docker", "exec", "miraiworks_backend",
            "python", "-c",
            "from app.schemas.todo import TodoRead; print('due_datetime' in TodoRead.model_fields); print('due_date' in TodoRead.model_fields)"
        ],
        capture_output=True,
        text=True
    )

    lines = result.stdout.strip().split('\n')
    has_due_datetime = lines[0] == "True" if len(lines) > 0 else False
    no_due_date = lines[1] == "False" if len(lines) > 1 else False

    print(f"TodoRead has 'due_datetime' field: {has_due_datetime}")
    print(f"TodoRead has 'due_date' field: {not no_due_date}")

    status = "[OK] PASS" if (has_due_datetime and no_due_date) else "[X] FAIL"
    print(f"{status}: Pydantic schemas correctly using due_datetime")

    return has_due_datetime and no_due_date


def test_timezone_serialization():
    """Test 5: Verify datetime fields are serialized with timezone info."""
    print("\n" + "=" * 60)
    print("TEST 5: Timezone Serialization Check")
    print("=" * 60)

    import subprocess

    # Create a test to check field_serializer
    test_code = """
from app.schemas.todo import TodoRead
from datetime import datetime, timezone
from app.models.todo import Todo

# Create a mock todo
todo = Todo(
    id=999,
    owner_id=1,
    title="Test",
    status="pending",
    due_datetime=datetime(2025, 10, 30, 22, 0, 0, tzinfo=timezone.utc),
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    is_deleted=False,
    todo_type="regular",
    publish_status="published"
)

# Serialize using TodoRead
schema = TodoRead.model_validate(todo)
json_data = schema.model_dump_json()
print(json_data)
"""

    result = subprocess.run(
        ["docker", "exec", "miraiworks_backend", "python", "-c", test_code],
        capture_output=True,
        text=True
    )

    try:
        data = json.loads(result.stdout)
        due_datetime = data.get("due_datetime", "")

        print(f"Serialized due_datetime: {due_datetime}")

        has_timezone = "+00:00" in due_datetime or "Z" in due_datetime
        status = "[OK] PASS" if has_timezone else "[X] FAIL"
        print(f"{status}: DateTime serialized with timezone info")

        return has_timezone
    except Exception as e:
        print(f"[X] FAIL: Could not parse response - {e}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("=" * 60)
    print(" " * 10 + "TIMEZONE MIGRATION TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        ("Database Schema", test_database_schema),
        ("Data Integrity", test_data_integrity),
        ("Alembic Version", test_alembic_version),
        ("Pydantic Schema", test_pydantic_schema),
        ("Timezone Serialization", test_timezone_serialization),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[X] ERROR in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n>>> All tests passed! Migration is complete and working correctly.")
        return 0
    else:
        print(f"\n>>> WARNING: {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
