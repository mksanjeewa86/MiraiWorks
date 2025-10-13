from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.constants import CompanyType


class Company(BaseModel):
    __tablename__ = "companies"
    name = Column(String(255), nullable=False, index=True)
    type = Column(Enum(CompanyType), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    website = Column(String(255), nullable=True)
    postal_code = Column(String(10), nullable=True)
    prefecture = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(String(1), nullable=False, default="1", index=True)
    # Logical deletion fields
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)  # ID of user who deleted this company

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
