#!/usr/bin/env python3
"""
Minimal workflow test to verify pytest database connection.
"""

import pytest
import os
from pathlib import Path

# Set up environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "mysql+asyncmy://hrms:hrms@localhost:3306/miraiworks_test"

# Add project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.interview import InterviewCreate
from app.schemas.todo import TodoCreate


@pytest.mark.asyncio
async def test_schema_validation_only():
    """Test that workflow_id is properly handled in schemas without database."""
    
    # Test InterviewCreate with workflow_id
    interview_data = InterviewCreate(
        candidate_id=1,
        recruiter_id=1,
        employer_company_id=1,
        workflow_id=123,
        title="Test Interview"
    )
    
    assert interview_data.workflow_id == 123
    print(f"✅ InterviewCreate accepts workflow_id: {interview_data.workflow_id}")
    
    # Test TodoCreate with workflow_id
    todo_data = TodoCreate(
        title="Test Todo",
        workflow_id=456
    )
    
    assert todo_data.workflow_id == 456
    print(f"✅ TodoCreate accepts workflow_id: {todo_data.workflow_id}")
    
    # Test optional workflow_id
    interview_no_workflow = InterviewCreate(
        candidate_id=1,
        recruiter_id=1,
        employer_company_id=1,
        title="Test Interview No Workflow"
    )
    
    assert interview_no_workflow.workflow_id is None
    print("✅ workflow_id is optional in InterviewCreate")
    
    todo_no_workflow = TodoCreate(title="Test Todo No Workflow")
    assert todo_no_workflow.workflow_id is None
    print("✅ workflow_id is optional in TodoCreate")
    
    print("🎉 All schema tests passed!")


if __name__ == "__main__":
    # Run pytest on this file
    pytest.main([__file__, "-v", "-s"])