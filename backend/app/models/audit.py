from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action = Column(String(50), nullable=False, index=True)  # AuditAction enum values
    entity_type = Column(
        String(50), nullable=False, index=True
    )  # e.g., 'User', 'Company'
    entity_id = Column(Integer, nullable=True, index=True)
    entity_data = Column(JSON, nullable=True)  # Snapshot of entity data
    changes = Column(JSON, nullable=True)  # Diff of changes made
    ip_address = Column(String(45), nullable=True, index=True)  # IPv4/IPv6
    user_agent = Column(Text, nullable=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    actor = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', entity_type='{self.entity_type}', timestamp={self.timestamp})>"
