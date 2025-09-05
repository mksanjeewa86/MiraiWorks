# Import all models to ensure they are registered with SQLAlchemy
from .company import Company
from .user import User
from .role import Role, UserRole
from .auth import RefreshToken, PasswordResetRequest, OauthAccount
from .audit import AuditLog
from .notification import Notification
from .message import Conversation, Message, MessageRead, conversation_participants
from .attachment import Attachment

__all__ = [
    "Company",
    "User", 
    "Role",
    "UserRole",
    "RefreshToken",
    "PasswordResetRequest", 
    "OauthAccount",
    "AuditLog",
    "Notification",
    "Conversation",
    "Message",
    "MessageRead",
    "conversation_participants",
    "Attachment",
]