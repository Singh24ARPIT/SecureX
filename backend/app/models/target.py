from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuthorizedTarget(Base):
    __tablename__ = "authorized_targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    target_url = Column(String(255), nullable=False)
    environment = Column(String(50), default="staging") # staging, dev, sandbox
    is_approved = Column(Boolean, default=True)
    approval_notes = Column(Text, nullable=True)
    approved_by = Column(String(100), default="Security Architecture Board")
    rate_limit_rps = Column(Float, default=5.0)
    health_status = Column(String(50), default="healthy") # healthy, degraded, unreachable
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    endpoints = relationship("ApiEndpoint", back_populates="target", cascade="all, delete-orphan")
    scans = relationship("SecurityScan", back_populates="target", cascade="all, delete-orphan")
    deployment_events = relationship("DeploymentEvent", back_populates="target", cascade="all, delete-orphan")
