from typing import Dict, List, Set
from app.utils.constants import UserRole

# Define permissions
PERMISSIONS = {
    # User management
    "users.create": "Create users",
    "users.read": "Read user data", 
    "users.update": "Update user data",
    "users.delete": "Delete users",
    "users.bulk_import": "Import users via CSV",
    
    # Company management
    "companies.create": "Create companies",
    "companies.read": "Read company data",
    "companies.update": "Update company data",
    "companies.delete": "Delete companies",
    
    # Messaging
    "messages.create": "Send messages",
    "messages.read": "Read messages",
    "messages.delete": "Delete messages",
    
    # Interviews
    "interviews.create": "Create interviews",
    "interviews.read": "Read interview data",
    "interviews.update": "Update interviews",
    "interviews.propose": "Propose interview times",
    "interviews.accept": "Accept interview proposals",
    "interviews.cancel": "Cancel interviews",
    
    # Resumes
    "resumes.create": "Create resumes",
    "resumes.read": "Read resumes",
    "resumes.update": "Update resumes",
    "resumes.share": "Share resumes",
    
    # Calendar
    "calendar.read": "Read calendar",
    "calendar.write": "Write to calendar",
    "calendar.integrate": "Integrate external calendars",
    
    # Admin functions
    "admin.audit": "View audit logs",
    "admin.notifications": "Manage notifications",
    "admin.password_reset": "Reset passwords",
}

# Role permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.SUPER_ADMIN: {
        # Super admin has all permissions
        *PERMISSIONS.keys()
    },
    
    UserRole.COMPANY_ADMIN: {
        # Company admin can manage users within their company
        "users.create", "users.read", "users.update", "users.delete", "users.bulk_import",
        "companies.read", "companies.update",
        "messages.read", "messages.delete", 
        "interviews.read", "interviews.update", "interviews.cancel",
        "resumes.read",
        "calendar.read",
        "admin.notifications", "admin.password_reset",
    },
    
    UserRole.RECRUITER: {
        "users.read",  # Limited to candidates and employers they work with
        "messages.create", "messages.read",
        "interviews.create", "interviews.read", "interviews.update", "interviews.propose", "interviews.accept", "interviews.cancel",
        "resumes.read", "resumes.share",
        "calendar.read", "calendar.write", "calendar.integrate",
    },
    
    UserRole.EMPLOYER: {
        "users.read",  # Limited to candidates through recruiters
        "messages.create", "messages.read",
        "interviews.read", "interviews.update", "interviews.propose", "interviews.accept", "interviews.cancel",
        "resumes.read",
        "calendar.read", "calendar.write", "calendar.integrate",
    },
    
    UserRole.CANDIDATE: {
        "users.read", "users.update",  # Own profile only
        "messages.create", "messages.read",
        "interviews.read", "interviews.propose", "interviews.accept",
        "resumes.create", "resumes.read", "resumes.update", "resumes.share",
        "calendar.read", "calendar.write", "calendar.integrate",
    },
}


def get_role_permissions(role: UserRole) -> Set[str]:
    """Get permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(user_role: UserRole, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_role_permissions(user_role)


def is_admin_role(role: UserRole) -> bool:
    """Check if role is an admin role requiring 2FA."""
    return role in {UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN}