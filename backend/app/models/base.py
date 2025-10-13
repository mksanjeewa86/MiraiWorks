from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func

from app.database import Base


class BaseModel(Base):
    """Base model with common fields for all models.

    Provides:
    - id: Primary key (auto-incrementing integer)
    - created_at: Timestamp when record was created (UTC)
    - updated_at: Timestamp when record was last updated (UTC)

    Usage:
        class User(BaseModel):
            __tablename__ = "users"
            email = Column(String, unique=True, nullable=False)
            # id, created_at, updated_at are inherited
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
