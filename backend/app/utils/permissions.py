from functools import wraps
from typing import List
from typing import Optional

from fastapi import HTTPException
from fastapi import status

from app.models.user import User
from app.rbac import has_permission
from app.utils.constants import UserRole


def requires_permission(permission: str):
    """Decorator to check if user has required permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs (should be injected by dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has the required permission
            user_roles = [ur.role.name for ur in current_user.user_roles]
            has_perm = any(has_permission(UserRole(role), permission) for role in user_roles)
            
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def requires_role(required_roles: List[UserRole]):
    """Decorator to check if user has one of the required roles."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = [UserRole(ur.role.name) for ur in current_user.user_roles]
            has_required_role = any(role in required_roles for role in user_roles)
            
            if not has_required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of these roles required: {[r.value for r in required_roles]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_company_access(user: User, target_company_id: Optional[int]) -> bool:
    """Check if user has access to the target company."""
    # Super admin has access to all companies
    user_roles = [UserRole(ur.role.name) for ur in user.user_roles]
    if UserRole.SUPER_ADMIN in user_roles:
        return True
    
    # Users can only access their own company
    if user.company_id != target_company_id:
        return False
    
    return True


def enforce_company_scoping(func):
    """Decorator to enforce company scoping on operations."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Extract company_id from various possible sources
        company_id = None
        if 'company_id' in kwargs:
            company_id = kwargs['company_id']
        elif hasattr(kwargs.get('obj'), 'company_id'):
            company_id = kwargs['obj'].company_id
        elif 'user_id' in kwargs:
            # If we're operating on a user, check their company
            db = kwargs.get('db')
            if db:
                from sqlalchemy import select
                result = await db.execute(select(User.company_id).where(User.id == kwargs['user_id']))
                company_id = result.scalar_one_or_none()
        
        # Check access
        if company_id is not None and not check_company_access(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient company permissions"
            )
        
        return await func(*args, **kwargs)
    return wrapper


async def get_user_roles(user: User) -> List[UserRole]:
    """Get list of roles for a user."""
    return [UserRole(ur.role.name) for ur in user.user_roles]


def is_super_admin(user: User) -> bool:
    """Check if user is super admin."""
    user_roles = [UserRole(ur.role.name) for ur in user.user_roles]
    return UserRole.SUPER_ADMIN in user_roles


def is_company_admin(user: User) -> bool:
    """Check if user is company admin or super admin."""
    user_roles = [UserRole(ur.role.name) for ur in user.user_roles]
    return UserRole.COMPANY_ADMIN in user_roles or UserRole.SUPER_ADMIN in user_roles


def can_manage_users(user: User, target_company_id: Optional[int] = None) -> bool:
    """Check if user can manage users (optionally for a specific company)."""
    if is_super_admin(user):
        return True
    
    if is_company_admin(user):
        # Company admin can only manage users in their own company
        return target_company_id is None or user.company_id == target_company_id
    
    return False