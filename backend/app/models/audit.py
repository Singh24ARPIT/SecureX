from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True) # e.g. "scan:initiated", "vuln:verified", "retest:completed"
    resource_type = Column(String(50), nullable=False) # scan, vulnerability, target, endpoint
    resource_id = Column(String(50), nullable=True)
    details_json = Column(JSON, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

