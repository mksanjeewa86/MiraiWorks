"""CRUD operations for MBTI personality test."""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.mbti_test import MBTITest, MBTIQuestion
from app.schemas.mbti import MBTITestSubmit, MBTITestStart
from app.utils.constants import MBTITestStatus, MBTIType


class CRUDMBTITest(CRUDBase[MBTITest, dict, dict]):
    """CRUD operations for MBTI tests."""

    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[MBTITest]:
        """Get MBTI test by user ID."""
        query = select(MBTITest).where(MBTITest.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def create_or_get_test(
        self, db: AsyncSession, *, user_id: int, test_data: MBTITestStart
    ) -> MBTITest:
        """Create a new test or get existing one for user."""
        existing_test = await self.get_by_user_id(db, user_id=user_id)
        
        if existing_test:
            # Reset if completed, allow to retake
            if existing_test.status == MBTITestStatus.COMPLETED.value:
                existing_test.status = MBTITestStatus.IN_PROGRESS.value
                existing_test.answers = {}
                existing_test.mbti_type = None
                existing_test.extraversion_introversion_score = None
                existing_test.sensing_intuition_score = None
                existing_test.thinking_feeling_score = None
                existing_test.judging_perceiving_score = None
                existing_test.started_at = datetime.utcnow()
                existing_test.completed_at = None
                existing_test.updated_at = datetime.utcnow()
                
                await db.commit()
                await db.refresh(existing_test)
                return existing_test
            else:
                # Return existing in-progress test
                return existing_test
        
        # Create new test
        test = MBTITest(
            user_id=user_id,
            status=MBTITestStatus.IN_PROGRESS.value,
            answers={},
            started_at=datetime.utcnow(),
            test_version="1.0"
        )
        
        db.add(test)
        await db.commit()
        await db.refresh(test)
        return test

    async def submit_answer(
        self, 
        db: AsyncSession, 
        *, 
        test: MBTITest, 
        question_id: int, 
        answer: str
    ) -> MBTITest:
        """Submit an answer for a question."""
        if not test.answers:
            test.answers = {}
        
        test.answers[str(question_id)] = answer
        test.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(test)
        return test

    async def complete_test(
        self, db: AsyncSession, *, test: MBTITest, answers: Dict[int, str]
    ) -> MBTITest:
        """Complete the MBTI test and calculate results."""
        # Update answers
        test.answers = {str(k): v for k, v in answers.items()}
        
        # Calculate dimension scores
        scores = await self._calculate_dimension_scores(db, answers)
        
        test.extraversion_introversion_score = scores["E_I"]
        test.sensing_intuition_score = scores["S_N"] 
        test.thinking_feeling_score = scores["T_F"]
        test.judging_perceiving_score = scores["J_P"]
        
        # Calculate MBTI type
        test.mbti_type = test.calculate_mbti_type()
        
        # Update status and timing
        test.status = MBTITestStatus.COMPLETED.value
        test.completed_at = datetime.utcnow()
        test.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(test)
        return test

    async def _calculate_dimension_scores(
        self, db: AsyncSession, answers: Dict[int, str]
    ) -> Dict[str, int]:
        """Calculate dimension scores from answers."""
        # Get all questions
        questions = await self.get_all_questions(db)
        question_map = {q.id: q for q in questions}
        
        # Initialize dimension counts
        dimension_counts = {
            "E_I": {"E": 0, "I": 0},
            "S_N": {"S": 0, "N": 0},
            "T_F": {"T": 0, "F": 0},
            "J_P": {"J": 0, "P": 0}
        }
        
        # Count answers for each dimension
        for question_id, answer in answers.items():
            question = question_map.get(int(question_id))
            if not question:
                continue
            
            # Determine which trait this answer represents
            if answer == "A":
                trait = question.option_a_trait
            else:  # answer == "B"
                trait = question.option_b_trait
            
            # Increment count for this trait
            dimension = question.dimension
            if dimension in dimension_counts and trait in dimension_counts[dimension]:
                dimension_counts[dimension][trait] += 1
        
        # Calculate scores (0-100, where higher = second trait)
        scores = {}
        for dimension, counts in dimension_counts.items():
            total = counts[list(counts.keys())[0]] + counts[list(counts.keys())[1]]
            if total == 0:
                scores[dimension] = 50  # Default to middle
            else:
                # For E_I: I score, for S_N: N score, etc.
                second_trait = list(counts.keys())[1]  # I, N, F, P
                scores[dimension] = int((counts[second_trait] / total) * 100)
        
        return scores

    async def get_test_progress(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get test progress for a user."""
        test = await self.get_by_user_id(db, user_id=user_id)
        if not test:
            return None
        
        total_questions = await self.get_question_count(db)
        answered = len(test.answers) if test.answers else 0
        
        return {
            "status": test.status,
            "completion_percentage": test.completion_percentage,
            "current_question": answered + 1 if answered < total_questions else total_questions,
            "total_questions": total_questions,
            "started_at": test.started_at
        }


class CRUDMBTIQuestion(CRUDBase[MBTIQuestion, dict, dict]):
    """CRUD operations for MBTI questions."""

    async def get_all_active(
        self, db: AsyncSession, *, version: str = "1.0"
    ) -> List[MBTIQuestion]:
        """Get all active questions for a version."""
        query = select(MBTIQuestion).where(
            and_(
                MBTIQuestion.is_active == True,
                MBTIQuestion.version == version
            )
        ).order_by(MBTIQuestion.question_number)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_questions_for_test(
        self, db: AsyncSession, *, language: str = "ja", version: str = "1.0"
    ) -> List[Dict[str, Any]]:
        """Get formatted questions for the test interface."""
        questions = await self.get_all_active(db, version=version)
        
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                "id": q.id,
                "question_number": q.question_number,
                "dimension": q.dimension,
                "question_text": q.question_text_ja if language == "ja" else q.question_text_en,
                "option_a": q.option_a_ja if language == "ja" else q.option_a_en,
                "option_b": q.option_b_ja if language == "ja" else q.option_b_en
            })
        
        return formatted_questions

    async def bulk_create_questions(
        self, db: AsyncSession, questions_data: List[Dict[str, Any]]
    ) -> List[MBTIQuestion]:
        """Bulk create MBTI questions."""
        questions = []
        for data in questions_data:
            question = MBTIQuestion(**data)
            questions.append(question)
            db.add(question)
        
        await db.commit()
        for question in questions:
            await db.refresh(question)
        
        return questions

    async def get_question_count(self, db: AsyncSession, *, version: str = "1.0") -> int:
        """Get total number of active questions."""
        questions = await self.get_all_active(db, version=version)
        return len(questions)


# Create instances
mbti_test = CRUDMBTITest(MBTITest)
mbti_question = CRUDMBTIQuestion(MBTIQuestion)