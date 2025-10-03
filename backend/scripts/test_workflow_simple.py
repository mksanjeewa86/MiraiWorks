#!/usr/bin/env python3
"""
Simple workflow relationship tests that can run without database.
Tests basic functionality to ensure the setup is working.
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Module Imports...")
    
    try:
        from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewInfo
        print("  ✅ Interview schemas imported successfully")
    except Exception as e:
        print(f"  ❌ Interview schema import failed: {e}")
        return False
    
    try:
        from app.schemas.todo import TodoCreate, TodoUpdate, TodoRead
        print("  ✅ Todo schemas imported successfully")
    except Exception as e:
        print(f"  ❌ Todo schema import failed: {e}")
        return False
    
    try:
        from app.crud.recruitment_workflow.recruitment_process import recruitment_process
        print("  ✅ CRUD operations imported successfully")
    except Exception as e:
        print(f"  ❌ CRUD import failed: {e}")
        return False
    
    return True

def test_schema_workflow_id():
    """Test that schemas support workflow_id without database."""
    print("\n🧪 Testing Schema Workflow ID Support...")
    
    try:
        from app.schemas.interview import InterviewCreate, InterviewUpdate
        from app.schemas.todo import TodoCreate, TodoUpdate
        
        # Test InterviewCreate
        interview_data = InterviewCreate(
            candidate_id=1,
            recruiter_id=1,
            employer_company_id=1,
            workflow_id=123,
            title="Test Interview"
        )
        assert interview_data.workflow_id == 123
        print("  ✅ InterviewCreate supports workflow_id")
        
        # Test InterviewUpdate
        interview_update = InterviewUpdate(workflow_id=456)
        assert interview_update.workflow_id == 456
        print("  ✅ InterviewUpdate supports workflow_id")
        
        # Test TodoCreate
        todo_data = TodoCreate(
            title="Test Todo",
            workflow_id=789
        )
        assert todo_data.workflow_id == 789
        print("  ✅ TodoCreate supports workflow_id")
        
        # Test TodoUpdate
        todo_update = TodoUpdate(workflow_id=101112)
        assert todo_update.workflow_id == 101112
        print("  ✅ TodoUpdate supports workflow_id")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Schema test failed: {e}")
        return False

def test_optional_workflow_id():
    """Test that workflow_id is optional."""
    print("\n🧪 Testing Optional Workflow ID...")
    
    try:
        from app.schemas.interview import InterviewCreate
        from app.schemas.todo import TodoCreate
        
        # Test without workflow_id
        interview_data = InterviewCreate(
            candidate_id=1,
            recruiter_id=1,
            employer_company_id=1,
            title="Test Interview"
        )
        assert interview_data.workflow_id is None
        print("  ✅ InterviewCreate works without workflow_id")
        
        todo_data = TodoCreate(title="Test Todo")
        assert todo_data.workflow_id is None
        print("  ✅ TodoCreate works without workflow_id")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Optional workflow_id test failed: {e}")
        return False

def test_crud_method_exists():
    """Test that CRUD soft_delete method exists."""
    print("\n🧪 Testing CRUD Method Existence...")
    
    try:
        from app.crud.recruitment_workflow.recruitment_process import recruitment_process
        
        assert hasattr(recruitment_process, 'soft_delete')
        print("  ✅ recruitment_process has soft_delete method")
        
        # Check method signature
        import inspect
        signature = inspect.signature(recruitment_process.soft_delete)
        params = list(signature.parameters.keys())
        assert 'db' in params
        assert 'id' in params
        print("  ✅ soft_delete method has correct signature")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CRUD method test failed: {e}")
        return False

def test_database_connection():
    """Test database connection availability."""
    print("\n🧪 Testing Database Connection...")
    
    try:
        from app.database import engine
        print("  ✅ Database engine imported successfully")
        
        # Note: Not actually connecting to avoid test database requirement
        print("  ℹ️  Database connection not tested (requires test DB)")
        return True
        
    except Exception as e:
        print(f"  ❌ Database connection test failed: {e}")
        return False

def main():
    """Run all simple tests."""
    print("=" * 60)
    print("Simple Workflow Tests (No Database Required)")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Schema Workflow ID", test_schema_workflow_id),
        ("Optional Workflow ID", test_optional_workflow_id),
        ("CRUD Methods", test_crud_method_exists),
        ("Database Setup", test_database_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<10} {test_name}")
    
    print("-" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All simple tests passed!")
        print("\n📋 Next Steps:")
        print("  1. Set up test database for full testing")
        print("  2. Run: python3 scripts/verify_workflow_schema.py")
        print("  3. Run: python3 scripts/test_schemas_only.py")
        print("  4. For full pytest: Set up test database first")
        
        print("\n🔧 To run pytest with database:")
        print("  1. Ensure test database exists:")
        print("     mysql -u hrms -phrms -e 'CREATE DATABASE IF NOT EXISTS miraiworks_test;'")
        print("  2. Set environment:")
        print("     export ENVIRONMENT=test")
        print("  3. Run tests:")
        print("     PYTHONPATH=. python3 -m pytest app/tests/test_workflow_relationships.py -v")
        
        return True
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)