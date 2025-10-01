from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String

from app.database import Base


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    date = Column(Date, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    country = Column(String(10), default="JP", nullable=False, index=True)
    is_national = Column(Boolean, default=True, nullable=False)
    is_recurring = Column(Boolean, default=True, nullable=False)
    description = Column(String(500), nullable=True)
    description_en = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __str__(self) -> str:
        return f"Holiday(name='{self.name}', date={self.date}, country='{self.country}')"

    def __repr__(self) -> str:
        return self.__str__()
