from fastapi import HTTPException, status

from app.models.user import User
from app.utils.constants import UserRole


def require_roles(user: User, required_roles: list[UserRole]) -> None:
    """Check if user has any of the required roles."""
    if not user or not user.user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    user_roles = [user_role.role.name for user_role in user.user_roles]

    # Check if user has any of the required roles
    has_required_role = any(role in user_roles for role in required_roles)

    if not has_required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )


def has_role(user: User, role: UserRole) -> bool:
    """Check if user has a specific role."""
    if not user or not user.user_roles:
        return False

    user_roles = [user_role.role.name for user_role in user.user_roles]
    return role in user_roles


def has_any_role(user: User, roles: list[UserRole]) -> bool:
    """Check if user has any of the specified roles."""
    if not user or not user.user_roles:
        return False

    user_roles = [user_role.role.name for user_role in user.user_roles]
    return any(role in user_roles for role in roles)


def is_company_user(user: User) -> bool:
    """Check if user belongs to a company."""
    return user.company_id is not None


def is_candidate(user: User) -> bool:
    """Check if user is a candidate."""
    return has_role(user, UserRole.CANDIDATE)


def is_recruiter(user: User) -> bool:
    """Check if user is a recruiter."""
    return has_any_role(user, [UserRole.ADMIN])


def can_manage_exams(user: User) -> bool:
    """Check if user can manage exams."""
    return has_any_role(user, [UserRole.ADMIN])
