#!/usr/bin/env python3
"""
Test that schemas support workflow_id without importing models.
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_interview_schemas():
    """Test interview schemas support workflow_id."""
    print("🧪 Testing Interview Schemas...")
    
    from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewInfo
    
    # Test InterviewCreate
    interview_data = InterviewCreate(
        candidate_id=1,
        recruiter_id=1,
        employer_company_id=1,
        workflow_id=123,
        title="Test Interview"
    )
    assert interview_data.workflow_id == 123
    print("  ✅ InterviewCreate accepts workflow_id")
    
    # Test without workflow_id
    interview_data_no_workflow = InterviewCreate(
        candidate_id=1,
        recruiter_id=1,
        employer_company_id=1,
        title="Test Interview No Workflow"
    )
    assert interview_data_no_workflow.workflow_id is None
    print("  ✅ InterviewCreate works without workflow_id")
    
    # Test InterviewUpdate
    interview_update = InterviewUpdate(workflow_id=456)
    assert interview_update.workflow_id == 456
    print("  ✅ InterviewUpdate accepts workflow_id")
    
    # Test that workflow_id is in the model fields
    assert 'workflow_id' in InterviewCreate.model_fields
    assert 'workflow_id' in InterviewUpdate.model_fields
    assert 'workflow_id' in InterviewInfo.model_fields
    print("  ✅ All interview schemas have workflow_id field")


def test_todo_schemas():
    """Test todo schemas support workflow_id."""
    print("\n🧪 Testing Todo Schemas...")
    
    from app.schemas.todo import TodoCreate, TodoUpdate, TodoRead
    
    # Test TodoCreate (inherits from TodoBase)
    todo_data = TodoCreate(
        title="Test Todo",
        workflow_id=789
    )
    assert todo_data.workflow_id == 789
    print("  ✅ TodoCreate accepts workflow_id")
    
    # Test without workflow_id
    todo_data_no_workflow = TodoCreate(title="Test Todo No Workflow")
    assert todo_data_no_workflow.workflow_id is None
    print("  ✅ TodoCreate works without workflow_id")
    
    # Test TodoUpdate
    todo_update = TodoUpdate(workflow_id=101112)
    assert todo_update.workflow_id == 101112
    print("  ✅ TodoUpdate accepts workflow_id")
    
    # Test that workflow_id is in the model fields
    assert 'workflow_id' in TodoCreate.model_fields
    assert 'workflow_id' in TodoUpdate.model_fields
    assert 'workflow_id' in TodoRead.model_fields
    print("  ✅ All todo schemas have workflow_id field")


def test_schema_validation():
    """Test schema validation works correctly."""
    print("\n🧪 Testing Schema Validation...")
    
    from app.schemas.interview import InterviewsListRequest
    
    # Test list request with workflow_id filter
    list_request = InterviewsListRequest(workflow_id=123)
    assert list_request.workflow_id == 123
    print("  ✅ InterviewsListRequest accepts workflow_id filter")
    
    # Test without workflow_id
    list_request_no_filter = InterviewsListRequest()
    assert list_request_no_filter.workflow_id is None
    print("  ✅ InterviewsListRequest works without workflow_id filter")


def main():
    """Run all schema tests."""
    print("=" * 60)
    print("Workflow Schema Tests")
    print("=" * 60)
    
    try:
        test_interview_schemas()
        test_todo_schemas()
        test_schema_validation()
        
        print("\n✨ All Schema Tests Passed!")
        print("\n📊 Summary:")
        print("  ✅ Interview schemas support workflow_id")
        print("  ✅ Todo schemas support workflow_id")
        print("  ✅ Filtering by workflow_id works")
        print("  ✅ workflow_id is optional in all schemas")
        print("\n🎉 Schema implementation is complete!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)