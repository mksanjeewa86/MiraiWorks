"""CRUD operations for question banks."""

import random

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.question_bank import QuestionBank, QuestionBankItem
from app.schemas.question_bank import (
    QuestionBankCreate,
    QuestionBankItemCreate,
    QuestionBankItemUpdate,
    QuestionBankUpdate,
)


class CRUDQuestionBank(CRUDBase[QuestionBank, QuestionBankCreate, QuestionBankUpdate]):
    """CRUD operations for question banks."""

    async def get_banks(
        self,
        db: AsyncSession,
        *,
        company_id: int | None = None,
        is_system_admin: bool = False,
        exam_type: str | None = None,
        category: str | None = None,
        is_public: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[QuestionBank], int]:
        """
        Get question banks with filtering.

        Args:
            db: Database session
            company_id: Filter by company (if not system admin)
            is_system_admin: Whether user is system admin
            exam_type: Filter by exam type
            category: Filter by category
            is_public: Filter by public status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (banks list, total count)
        """
        # Build query
        query = select(QuestionBank)

        # Filter conditions
        conditions = []

        # Access control
        if not is_system_admin:
            # Regular users can see public banks or their company's banks
            if company_id:
                conditions.append(
                    or_(
                        QuestionBank.is_public,
                        QuestionBank.company_id == company_id,
                    )
                )
            else:
                conditions.append(QuestionBank.is_public)
        # System admins can see all banks

        # Additional filters
        if exam_type:
            conditions.append(QuestionBank.exam_type == exam_type)

        if category:
            conditions.append(QuestionBank.category == category)

        if is_public is not None:
            conditions.append(QuestionBank.is_public == is_public)

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(QuestionBank.created_at.desc())

        # Execute query
        result = await db.execute(query)
        banks = result.scalars().all()

        return list(banks), total

    async def get_with_questions(
        self, db: AsyncSession, bank_id: int
    ) -> QuestionBank | None:
        """Get question bank with all questions."""
        query = (
            select(QuestionBank)
            .options(selectinload(QuestionBank.questions))
            .where(QuestionBank.id == bank_id)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_with_questions(
        self,
        db: AsyncSession,
        bank_data: QuestionBankCreate,
        created_by_id: int,
    ) -> QuestionBank:
        """Create question bank with questions in one transaction."""
        # Create bank
        bank_dict = bank_data.model_dump(exclude={"questions"})
        bank_dict["created_by"] = created_by_id
        bank = QuestionBank(**bank_dict)

        db.add(bank)
        await db.flush()  # Get the bank ID

        # Create questions
        for i, question_data in enumerate(bank_data.questions):
            question_dict = question_data.model_dump()
            question_dict["bank_id"] = bank.id
            if question_dict.get("order_index") is None:
                question_dict["order_index"] = i
            question = QuestionBankItem(**question_dict)
            db.add(question)

        await db.commit()
        await db.refresh(bank)
        return bank

    async def get_question_count(self, db: AsyncSession, bank_id: int) -> int:
        """Get total number of questions in a bank."""
        result = await db.execute(
            select(func.count(QuestionBankItem.id)).where(
                QuestionBankItem.bank_id == bank_id
            )
        )
        return result.scalar() or 0


class CRUDQuestionBankItem(
    CRUDBase[QuestionBankItem, QuestionBankItemCreate, QuestionBankItemUpdate]
):
    """CRUD operations for question bank items."""

    async def get_by_bank(
        self, db: AsyncSession, bank_id: int
    ) -> list[QuestionBankItem]:
        """Get all questions for a bank, ordered by order_index."""
        query = (
            select(QuestionBankItem)
            .where(QuestionBankItem.bank_id == bank_id)
            .order_by(QuestionBankItem.order_index)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_random_questions(
        self,
        db: AsyncSession,
        bank_id: int,
        count: int,
        category: str | None = None,
        difficulty: str | None = None,
        tags: list[str] | None = None,
    ) -> list[QuestionBankItem]:
        """
        Get random questions from a bank with optional filtering.

        Args:
            db: Database session
            bank_id: Question bank ID
            count: Number of questions to return
            category: Filter by category (not used for QuestionBankItem, but kept for consistency)
            difficulty: Filter by difficulty
            tags: Filter by tags (questions must have at least one matching tag)

        Returns:
            List of random questions
        """
        query = select(QuestionBankItem).where(QuestionBankItem.bank_id == bank_id)

        # Apply filters
        if difficulty:
            query = query.where(QuestionBankItem.difficulty == difficulty)

        if tags:
            # Filter questions that have at least one matching tag
            # Using JSON_OVERLAPS for MySQL 8.0+
            # Fallback: Load all and filter in Python
            pass

        # Execute query
        result = await db.execute(query)
        all_questions = list(result.scalars().all())

        # Filter by tags in Python if needed
        if tags:
            filtered_questions = []
            for q in all_questions:
                if q.tags and any(tag in q.tags for tag in tags):
                    filtered_questions.append(q)
            all_questions = filtered_questions

        # Randomly select questions
        if len(all_questions) <= count:
            return all_questions

        return random.sample(all_questions, count)

    async def reorder_questions(
        self,
        db: AsyncSession,
        bank_id: int,
        question_orders: list[dict[str, int]],  # [{"question_id": 1, "order_index": 0}]
    ) -> list[QuestionBankItem]:
        """Reorder questions in a bank."""
        for order_data in question_orders:
            question = await self.get(db, id=order_data["question_id"])
            if question and question.bank_id == bank_id:
                question.order_index = order_data["order_index"]

        await db.commit()
        return await self.get_by_bank(db, bank_id)


# Create instances
question_bank = CRUDQuestionBank(QuestionBank)
question_bank_item = CRUDQuestionBankItem(QuestionBankItem)
