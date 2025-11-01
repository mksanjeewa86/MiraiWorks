from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import CompanyType


class Company(BaseModel):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[CompanyType] = mapped_column(Enum(CompanyType), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    prefecture: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[str] = mapped_column(String(1), nullable=False, default="1", index=True)
    # Logical deletion fields
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    positions = relationship(
        "Position", back_populates="company", cascade="all, delete-orphan"
    )
    profile = relationship(
        "CompanyProfile",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )
    exams = relationship("Exam", back_populates="company", cascade="all, delete-orphan")
    workflows = relationship(
        "Workflow",
        back_populates="employer_company",
        cascade="all, delete-orphan",
    )

    # Company connections (new system)
    company_connections_as_source = relationship(
        "CompanyConnection",
        foreign_keys="CompanyConnection.source_company_id",
        back_populates="source_company",
        cascade="all, delete-orphan",
    )
    company_connections_as_target = relationship(
        "CompanyConnection",
        foreign_keys="CompanyConnection.target_company_id",
        back_populates="target_company",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', type='{self.type}')>"
