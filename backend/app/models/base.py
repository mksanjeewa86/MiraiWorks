from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
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
            email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
            # id, created_at, updated_at are inherited
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
