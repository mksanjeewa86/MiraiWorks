#!/usr/bin/env python3
"""
Working pytest for workflow relationships using existing fixtures.
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
from app.crud.recruitment_workflow.recruitment_process import recruitment_process


@pytest.mark.asyncio
async def test_workflow_relationships_working(
    db_session: AsyncSession,
    test_company,
    test_user
):
    """Test workflow relationships with correct fixture names."""
    
    # Create workflow
    workflow_data = {
        "name": "Working Test Workflow", 
        "description": "Testing with correct fixtures",
        "employer_company_id": test_company.id,
        "status": "active"
    }
    
    workflow = await recruitment_process.create(
        db_session,
        obj_in=workflow_data,
        created_by=test_user.id
    )
    
    assert workflow is not None
    assert workflow.name == "Working Test Workflow"
    print(f"✅ Created workflow: {workflow.id}")
    
    # Test InterviewCreate schema with workflow_id
    interview_data = InterviewCreate(
        candidate_id=test_user.id,
        recruiter_id=test_user.id,
        employer_company_id=test_company.id,
        workflow_id=workflow.id,
        title="Working Test Interview"
    )
    
    assert interview_data.workflow_id == workflow.id
    print(f"✅ InterviewCreate accepts workflow_id: {interview_data.workflow_id}")
    
    # Test TodoCreate schema with workflow_id
    todo_data = TodoCreate(
        title="Working Test Todo",
        workflow_id=workflow.id
    )
    
    assert todo_data.workflow_id == workflow.id
    print(f"✅ TodoCreate accepts workflow_id: {todo_data.workflow_id}")
    
    print("🎉 All workflow relationship tests passed!")


if __name__ == "__main__":
    # Run pytest on this file
    pytest.main([__file__, "-v", "-s"])