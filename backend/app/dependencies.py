import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.role import UserRole as UserRoleModel
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import UserRole

security = HTTPBearer(auto_error=False)

# Redis connection for 2FA codes and rate limiting
redis_client = None


async def get_redis():
    """Get Redis connection."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url)
    return redis_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or not credentials.credentials:
        raise credentials_exception

    # Verify JWT token
    payload = auth_service.verify_token(credentials.credentials, "access")
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    # Get user from database with explicit join
    result = await db.execute(
        select(User)
        .options(selectinload(User.company))
        .where(User.id == user_id, User.is_active.is_(True))
    )

    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    # Explicitly load user roles in a separate query to avoid greenlet issues
    roles_result = await db.execute(
        select(UserRoleModel)
        .options(selectinload(UserRoleModel.role))
        .where(UserRoleModel.user_id == user_id)
    )
    user_roles = roles_result.scalars().all()

    # Manually set the user_roles to avoid lazy loading issues
    user.user_roles = user_roles

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Get current user if authenticated, otherwise None."""
    if not credentials or not credentials.credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# 2FA related functions
async def store_2fa_code(user_id: int, code: str, ttl: int = 600) -> bool:
    """Store 2FA code in Redis with TTL (default 10 minutes)."""
    try:
        redis_conn = await get_redis()
        key = f"2fa:{user_id}"
        await redis_conn.setex(key, ttl, code)
        return True
    except Exception:
        return False


async def verify_2fa_code(user_id: int, code: str) -> bool:
    """Verify 2FA code from Redis."""
    # In test environment, accept the test code "123456" for any user
    if settings.environment == "test" and code == "123456":
        return True

    try:
        redis_conn = await get_redis()
        key = f"2fa:{user_id}"
        stored_code = await redis_conn.get(key)

        if stored_code and stored_code.decode() == code:
            # Delete the code after successful verification
            await redis_conn.delete(key)
            return True
        return False
    except Exception:
        return False


async def check_rate_limit(key: str, limit: int = 5, window: int = 300) -> bool:
    """Check rate limit using Redis. Returns True if under limit."""
    # Disable rate limiting during tests
    if settings.environment == "test":
        return True

    try:
        redis_conn = await get_redis()
        current = await redis_conn.incr(key)

        if current == 1:
            # First request, set TTL
            await redis_conn.expire(key, window)

        return current <= limit
    except Exception:
        # If Redis is down, allow the request
        return True


async def get_client_ip(request) -> str:
    """Extract client IP from request."""
    # Check for forwarded headers first
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def get_current_user_with_company(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user and ensure they have a company."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Company association required"
        )
    return current_user


async def require_system_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be a system admin."""
    # Check if user has system_admin role
    user_roles = [user_role.role.name for user_role in current_user.user_roles]

    if UserRole.SYSTEM_ADMIN.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="System admin access required"
        )

    return current_user


# Alias for backward compatibility (will be deprecated)
require_super_admin = require_system_admin
