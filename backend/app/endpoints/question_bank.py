"""Question bank API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.question_bank import (
    question_bank as question_bank_crud,
)
from app.crud.question_bank import (
    question_bank_item as question_bank_item_crud,
)
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.question_bank import (
    QuestionBankCreate,
    QuestionBankDetail,
    QuestionBankInfo,
    QuestionBankItemCreate,
    QuestionBankItemInfo,
    QuestionBankItemUpdate,
    QuestionBankListResponse,
    QuestionBankUpdate,
)
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter()


# Question Bank Management


@router.post(API_ROUTES.QUESTION_BANKS.BASE, response_model=QuestionBankDetail)
async def create_question_bank(
    bank_data: QuestionBankCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new question bank with questions.

    System admins can create global banks (company_id=None).
    Company admins/recruiters can only create company-specific banks.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    # Check if user is system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Validate permissions
    if bank_data.company_id is None:
        # Creating global bank - only system admins allowed
        if not is_system_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only system admins can create global question banks",
            )
    else:
        # Creating company bank - must be user's company
        if not is_system_admin and (
            not current_user.company_id
            or bank_data.company_id != current_user.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create banks for your own company",
            )

    bank = await question_bank_crud.create_with_questions(
        db=db, bank_data=bank_data, created_by_id=current_user.id
    )

    return bank


@router.get(API_ROUTES.QUESTION_BANKS.BASE, response_model=QuestionBankListResponse)
async def get_question_banks(
    exam_type: str | None = Query(None, description="Filter by exam type"),
    category: str | None = Query(None, description="Filter by category"),
    is_public: bool | None = Query(None, description="Filter by public status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get question banks.

    System admins can view all banks.
    Company users can view public banks + their company's banks.
    """
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    # Check if user is system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    banks, total = await question_bank_crud.get_banks(
        db=db,
        company_id=current_user.company_id,
        is_system_admin=is_system_admin,
        exam_type=exam_type,
        category=category,
        is_public=is_public,
        skip=skip,
        limit=limit,
    )

    # Add question count for each bank
    banks_with_counts = []
    for bank in banks:
        count = await question_bank_crud.get_question_count(db=db, bank_id=bank.id)
        bank_info = QuestionBankInfo.model_validate(bank)
        bank_info.question_count = count
        banks_with_counts.append(bank_info)

    return QuestionBankListResponse(
        banks=banks_with_counts,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(banks) == limit,
    )


@router.get(API_ROUTES.QUESTION_BANKS.BY_ID, response_model=QuestionBankDetail)
async def get_question_bank_detail(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed question bank with all questions."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    bank = await question_bank_crud.get_with_questions(db=db, bank_id=bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    # Check access permissions
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and (
        not bank.is_public and bank.company_id != current_user.company_id
    ):
        # User must have access to this bank
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return bank


@router.put(API_ROUTES.QUESTION_BANKS.BY_ID, response_model=QuestionBankInfo)
async def update_question_bank(
    bank_id: int,
    bank_data: QuestionBankUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update question bank details."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    bank = await question_bank_crud.get(db=db, id=bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    # Check permissions
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and bank.company_id != current_user.company_id:
        # User can only update their company's banks
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    bank = await question_bank_crud.update(db=db, db_obj=bank, obj_in=bank_data)
    return bank


@router.delete(API_ROUTES.QUESTION_BANKS.BY_ID)
async def delete_question_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a question bank."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    bank = await question_bank_crud.get(db=db, id=bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    # Check permissions
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and bank.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await question_bank_crud.remove(db=db, id=bank_id)
    return {"message": "Question bank deleted successfully"}


# Question Management


@router.get(
    API_ROUTES.QUESTION_BANKS.QUESTIONS, response_model=list[QuestionBankItemInfo]
)
async def get_bank_questions(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all questions for a question bank."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    bank = await question_bank_crud.get(db=db, id=bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    # Check access
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if (
        not is_system_admin
        and not bank.is_public
        and bank.company_id != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    questions = await question_bank_item_crud.get_by_bank(db=db, bank_id=bank_id)
    return questions


@router.post(API_ROUTES.QUESTION_BANKS.QUESTIONS, response_model=QuestionBankItemInfo)
async def add_question_to_bank(
    bank_id: int,
    question_data: QuestionBankItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a new question to a question bank."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    bank = await question_bank_crud.get(db=db, id=bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    # Check permissions
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and bank.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Create question
    question_dict = question_data.model_dump()
    question_dict["bank_id"] = bank_id
    question = await question_bank_item_crud.create(
        db=db, obj_in=QuestionBankItemCreate(**question_dict)
    )

    return question


@router.put(
    API_ROUTES.QUESTION_BANKS.QUESTION_BY_ID, response_model=QuestionBankItemInfo
)
async def update_bank_question(
    question_id: int,
    question_data: QuestionBankItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a question in a question bank."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    question = await question_bank_item_crud.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    # Verify permissions through bank
    bank = await question_bank_crud.get(db=db, id=question.bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and bank.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    question = await question_bank_item_crud.update(
        db=db, db_obj=question, obj_in=question_data
    )
    return question


@router.delete(API_ROUTES.QUESTION_BANKS.QUESTION_BY_ID)
async def delete_bank_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a question from a question bank."""
    require_roles(
        current_user,
        [UserRole.ADMIN, UserRole.SYSTEM_ADMIN],
    )

    question = await question_bank_item_crud.get(db=db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    # Verify permissions through bank
    bank = await question_bank_crud.get(db=db, id=question.bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question bank not found"
        )

    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and bank.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await question_bank_item_crud.remove(db=db, id=question_id)
    return {"message": "Question deleted successfully"}
