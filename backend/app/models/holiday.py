from datetime import date as date_type

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Holiday(BaseModel):
    __tablename__ = "holidays"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(10), default="JP", nullable=False, index=True)
    is_national: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description_en: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __str__(self) -> str:
        return (
            f"Holiday(name='{self.name}', date={self.date}, country='{self.country}')"
        )

    def __repr__(self) -> str:
        return self.__str__()
