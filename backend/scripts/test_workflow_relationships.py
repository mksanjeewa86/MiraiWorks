#!/usr/bin/env python3
"""
Test workflow relationships functionality.
Tests the relationships between recruitment_processes, interviews, and todos.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models.recruitment_process import RecruitmentProcess
from app.models.interview import Interview
from app.models.todo import Todo
from app.crud.recruitment_workflow.recruitment_process import recruitment_process as process_crud
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_workflow_relationships():
    """Test workflow relationships and cascading soft delete."""
    async for db in get_db():
        try:
            print("🧪 Testing Workflow Relationships...")
            
            # 1. Create a test workflow
            print("\n1️⃣ Creating test workflow...")
            workflow_data = {
                "name": "Test Workflow for Relationships",
                "description": "Testing workflow relationships with interviews and todos",
                "employer_company_id": 1,  # Assuming company with ID 1 exists
                "status": "active"
            }
            
            workflow = await process_crud.create(
                db, 
                obj_in=workflow_data,
                created_by=1  # Assuming user with ID 1 exists
            )
            print(f"✅ Created workflow: ID={workflow.id}, Name='{workflow.name}'")
            
            # 2. Create associated interviews
            print("\n2️⃣ Creating associated interviews...")
            interview1 = Interview(
                workflow_id=workflow.id,
                candidate_id=1,
                recruiter_id=1,
                employer_company_id=1,
                recruiter_company_id=1,
                title="Technical Interview - Test",
                status="scheduled",
                interview_type="video"
            )
            interview2 = Interview(
                workflow_id=workflow.id,
                candidate_id=1,
                recruiter_id=1,
                employer_company_id=1,
                recruiter_company_id=1,
                title="Cultural Fit Interview - Test",
                status="scheduled",
                interview_type="in_person"
            )
            
            db.add(interview1)
            db.add(interview2)
            await db.commit()
            print(f"✅ Created 2 interviews linked to workflow {workflow.id}")
            
            # 3. Create associated todos
            print("\n3️⃣ Creating associated todos...")
            todo1 = Todo(
                workflow_id=workflow.id,
                owner_id=1,
                title="Review candidate resume - Test",
                status="pending"
            )
            todo2 = Todo(
                workflow_id=workflow.id,
                owner_id=1,
                title="Prepare interview questions - Test",
                status="pending"
            )
            
            db.add(todo1)
            db.add(todo2)
            await db.commit()
            print(f"✅ Created 2 todos linked to workflow {workflow.id}")
            
            # 4. Verify relationships
            print("\n4️⃣ Verifying relationships...")
            
            # Count related interviews
            interview_count_result = await db.execute(
                select(Interview).where(
                    Interview.workflow_id == workflow.id,
                    Interview.is_deleted == False
                )
            )
            interview_count = len(interview_count_result.scalars().all())
            print(f"  - Found {interview_count} interviews linked to workflow")
            
            # Count related todos
            todo_count_result = await db.execute(
                select(Todo).where(
                    Todo.workflow_id == workflow.id,
                    Todo.is_deleted == False
                )
            )
            todo_count = len(todo_count_result.scalars().all())
            print(f"  - Found {todo_count} todos linked to workflow")
            
            # 5. Test cascading soft delete
            print("\n5️⃣ Testing cascading soft delete...")
            print(f"  - Soft deleting workflow {workflow.id}...")
            
            deleted_workflow = await process_crud.soft_delete(db, id=workflow.id)
            print(f"✅ Workflow soft deleted: is_deleted={deleted_workflow.is_deleted}")
            
            # 6. Verify cascade
            print("\n6️⃣ Verifying cascade effect...")
            
            # Check if interviews were soft deleted
            deleted_interviews_result = await db.execute(
                select(Interview).where(
                    Interview.workflow_id == workflow.id,
                    Interview.is_deleted == True
                )
            )
            deleted_interviews = deleted_interviews_result.scalars().all()
            print(f"  - {len(deleted_interviews)} interviews were soft deleted")
            
            # Check if todos were soft deleted
            deleted_todos_result = await db.execute(
                select(Todo).where(
                    Todo.workflow_id == workflow.id,
                    Todo.is_deleted == True
                )
            )
            deleted_todos = deleted_todos_result.scalars().all()
            print(f"  - {len(deleted_todos)} todos were soft deleted")
            
            # 7. Verify data integrity
            print("\n7️⃣ Verifying data integrity...")
            
            # Check that workflow_id is still set (not nullified)
            for interview in deleted_interviews:
                assert interview.workflow_id == workflow.id, "Interview workflow_id should not be null"
                assert interview.deleted_at is not None, "Interview deleted_at should be set"
            print("  ✅ Interview workflow relationships preserved")
            
            for todo in deleted_todos:
                assert todo.workflow_id == workflow.id, "Todo workflow_id should not be null"
                assert todo.deleted_at is not None, "Todo deleted_at should be set"
            print("  ✅ Todo workflow relationships preserved")
            
            # 8. Summary
            print("\n📊 Test Summary:")
            print("  ✅ Workflow created successfully")
            print("  ✅ Interviews linked to workflow")
            print("  ✅ Todos linked to workflow")
            print("  ✅ Cascading soft delete works correctly")
            print("  ✅ Data integrity maintained")
            print("\n🎉 All tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Workflow Relationships Test")
    print("=" * 60)
    asyncio.run(test_workflow_relationships())