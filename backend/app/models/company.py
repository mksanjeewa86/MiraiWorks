from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.utils.constants import CompanyType


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
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
    is_demo = Column(Boolean, nullable=False, default=False, index=True)
    demo_end_date = Column(DateTime(timezone=True), nullable=True)
    demo_features = Column(Text, nullable=True)
    demo_notes = Column(Text, nullable=True)
    # Logical deletion fields
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)  # ID of user who deleted this company
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="company", cascade="all, delete-orphan")
    profile = relationship(
        "CompanyProfile",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )
    exams = relationship("Exam", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', type='{self.type}')>"
