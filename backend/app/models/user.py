from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    permissions = Column(Text, nullable=False) # Comma-separated or JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    username = Column(String(60), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    role = Column(String(50), nullable=False, default="security_engineer") # admin, security_engineer, auditor, agency_admin
    agency_id = Column(String(50), nullable=True) # Used for travel agency multi-tenancy testing (e.g. 'agency_1', 'agency_2')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")

