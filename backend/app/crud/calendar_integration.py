from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.calendar_integration import ExternalCalendarAccount
from app.models.user import User


class CRUDCalendarIntegration(CRUDBase[ExternalCalendarAccount, dict, dict]):
    """Calendar integration CRUD operations."""

    async def get_by_user_and_provider_account(
        self,
        db: AsyncSession,
        user_id: int,
        provider: str,
        provider_account_id: str
    ) -> Optional[ExternalCalendarAccount]:
        """Get calendar account by user, provider and provider account ID."""
        result = await db.execute(
            select(ExternalCalendarAccount).where(
                and_(
                    ExternalCalendarAccount.user_id == user_id,
                    ExternalCalendarAccount.provider == provider,
                    ExternalCalendarAccount.provider_account_id == provider_account_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_accounts_by_user(
        self, db: AsyncSession, user_id: int
    ) -> List[ExternalCalendarAccount]:
        """Get active calendar accounts for a user."""
        result = await db.execute(
            select(ExternalCalendarAccount)
            .where(
                ExternalCalendarAccount.user_id == user_id,
                ExternalCalendarAccount.is_active == True,
            )
            .order_by(ExternalCalendarAccount.created_at)
        )
        return result.scalars().all()

    async def get_user_account_by_id(
        self, db: AsyncSession, account_id: int, user_id: int
    ) -> Optional[ExternalCalendarAccount]:
        """Get calendar account by ID and user ID."""
        result = await db.execute(
            select(ExternalCalendarAccount).where(
                and_(
                    ExternalCalendarAccount.id == account_id,
                    ExternalCalendarAccount.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_active_user_account_by_id(
        self, db: AsyncSession, account_id: int, user_id: int
    ) -> Optional[ExternalCalendarAccount]:
        """Get active calendar account by ID and user ID."""
        result = await db.execute(
            select(ExternalCalendarAccount).where(
                and_(
                    ExternalCalendarAccount.id == account_id,
                    ExternalCalendarAccount.user_id == user_id,
                    ExternalCalendarAccount.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_sync_enabled_accounts_by_user(
        self, db: AsyncSession, user_id: int
    ) -> List[ExternalCalendarAccount]:
        """Get sync-enabled calendar accounts for a user."""
        result = await db.execute(
            select(ExternalCalendarAccount).where(
                ExternalCalendarAccount.user_id == user_id,
                ExternalCalendarAccount.is_active == True,
                ExternalCalendarAccount.sync_enabled == True,
            )
        )
        return result.scalars().all()

    async def get_filtered_accounts_by_user(
        self, db: AsyncSession, user_id: int, account_id: Optional[int] = None
    ) -> List[ExternalCalendarAccount]:
        """Get calendar accounts for a user, optionally filtered by account ID."""
        query = select(ExternalCalendarAccount).where(
            ExternalCalendarAccount.user_id == user_id,
            ExternalCalendarAccount.is_active == True,
        )

        if account_id:
            query = query.where(ExternalCalendarAccount.id == account_id)

        result = await db.execute(query)
        return result.scalars().all()

    async def create_calendar_account(
        self,
        db: AsyncSession,
        user_id: int,
        provider: str,
        provider_account_id: str,
        email: str,
        display_name: Optional[str],
        access_token: str,
        refresh_token: Optional[str],
        token_expires_at: datetime,
    ) -> ExternalCalendarAccount:
        """Create a new calendar account."""
        account = ExternalCalendarAccount(
            user_id=user_id,
            provider=provider,
            provider_account_id=provider_account_id,
            email=email,
            display_name=display_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            is_active=True,
            sync_enabled=True,
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    async def update_account_tokens(
        self,
        db: AsyncSession,
        account: ExternalCalendarAccount,
        access_token: str,
        refresh_token: Optional[str],
        token_expires_at: datetime,
        email: str,
        display_name: Optional[str],
    ) -> ExternalCalendarAccount:
        """Update account tokens and info."""
        account.access_token = access_token
        if refresh_token:
            account.refresh_token = refresh_token
        account.token_expires_at = token_expires_at
        account.is_active = True
        account.sync_enabled = True
        account.email = email
        account.display_name = display_name

        await db.commit()
        await db.refresh(account)
        return account

    async def update_webhook_info(
        self,
        db: AsyncSession,
        account: ExternalCalendarAccount,
        webhook_id: str,
        webhook_expires_at: datetime,
    ) -> ExternalCalendarAccount:
        """Update webhook information for an account."""
        account.webhook_id = webhook_id
        account.webhook_expires_at = webhook_expires_at
        await db.commit()
        return account

    async def deactivate_account(
        self, db: AsyncSession, account: ExternalCalendarAccount
    ) -> ExternalCalendarAccount:
        """Deactivate a calendar account."""
        account.is_active = False
        account.sync_enabled = False
        await db.commit()
        return account

    async def update_last_sync(
        self, db: AsyncSession, account: ExternalCalendarAccount, sync_time: datetime
    ) -> ExternalCalendarAccount:
        """Update last sync time for an account."""
        account.last_sync_at = sync_time
        await db.commit()
        return account


# Create the CRUD instance
calendar_integration = CRUDCalendarIntegration(ExternalCalendarAccount)