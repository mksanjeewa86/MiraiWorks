import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.auth import RefreshToken
from app.models.role import UserRole as UserRoleModel
from app.models.user import User
from app.rbac import is_admin_role
from app.utils.constants import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = settings.jwt_secret
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.jwt_access_ttl_min
        self.refresh_token_expire_days = settings.jwt_refresh_ttl_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Optional[dict[str, Any]] = None) -> str:
        """Create a JWT refresh token or random token."""
        if data is not None:
            # Create JWT refresh token with data
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
            to_encode.update({"exp": expire, "type": "refresh"})
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt
        else:
            # Create random refresh token for storage
            return secrets.token_urlsafe(32)

    def hash_token(self, token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None

    def decode_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[dict[str, Any]]:
        """Alias for verify_token for backward compatibility."""
        return self.verify_token(token, token_type)

    async def store_refresh_token(
        self, db: AsyncSession, user_id: int, token: str
    ) -> RefreshToken:
        """Store a refresh token in the database."""
        token_hash = self.hash_token(token)
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        refresh_token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )

        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token

    async def revoke_refresh_token(self, db: AsyncSession, token: str) -> bool:
        """Revoke a refresh token."""
        token_hash = self.hash_token(token)

        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(is_revoked=True, revoked_at=datetime.utcnow())
        )

        await db.commit()
        return result.rowcount > 0

    async def revoke_user_tokens(self, db: AsyncSession, user_id: int) -> bool:
        """Revoke all refresh tokens for a user."""
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(is_revoked=True, revoked_at=datetime.utcnow())
        )

        await db.commit()
        return result.rowcount > 0

    async def verify_refresh_token(
        self, db: AsyncSession, token: str
    ) -> Optional[User]:
        """Verify a refresh token and return the associated user."""
        token_hash = self.hash_token(token)

        result = await db.execute(
            select(RefreshToken)
            .options(
                selectinload(RefreshToken.user)
                .selectinload(User.user_roles)
                .selectinload(UserRoleModel.role)
            )
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )

        refresh_token = result.scalar_one_or_none()
        if not refresh_token:
            return None

        return refresh_token.user

    async def authenticate_user(
        self, db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user with email and password."""
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.company),
                selectinload(User.user_roles).selectinload(UserRoleModel.role),
            )
            .where(User.email == email, User.is_deleted == False)
        )

        user = result.scalar_one_or_none()
        if not user or not user.hashed_password:
            return None

        # Check if user is suspended
        if user.is_suspended:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        return user

    def generate_2fa_code(self) -> str:
        """Generate a 6-digit 2FA code."""
        return str(secrets.randbelow(900000) + 100000)

    def generate_activation_token(self, email: str) -> str:
        """Generate an activation token for user email verification."""
        data = {"sub": email, "type": "activation"}
        # Activation tokens expire in 24 hours
        expire_delta = timedelta(hours=24)
        to_encode = data.copy()
        expire = datetime.utcnow() + expire_delta
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def requires_2fa(self, db: AsyncSession, user: User) -> bool:
        """Check if user requires 2FA based on user settings and role requirements."""

        # Get fresh user data from database instead of refreshing eager-loaded object
        result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRoleModel.role))
            .where(User.id == user.id)
        )
        fresh_user = result.scalar_one_or_none()
        if not fresh_user:
            return False

        if settings.environment.lower() == "test":
            return False

        # First check user's individual 2FA setting
        if fresh_user.require_2fa:
            return True

        # If force_2fa_for_admins is disabled, only use individual settings
        if not settings.force_2fa_for_admins:
            return False

        # Check if user has any admin roles and force_2fa_for_admins is enabled
        # (we already loaded the user with roles above)
        for user_role in fresh_user.user_roles:
            if is_admin_role(UserRole(user_role.role.name)):
                return True

        return False

    async def create_login_tokens(self, db: AsyncSession, user: User) -> dict[str, Any]:
        """Create access and refresh tokens for a user."""
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Create access token payload
        access_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "company_id": user.company_id,
            "roles": [ur.role.name for ur in user.user_roles],
        }

        # Create tokens
        access_token = self.create_access_token(access_token_data)
        refresh_token = self.create_refresh_token()

        # Store refresh token
        await self.store_refresh_token(db, user.id, refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "company_id": user.company_id,
                "roles": [ur.role.name for ur in user.user_roles],
            },
        }


# Global instance
auth_service = AuthService()
