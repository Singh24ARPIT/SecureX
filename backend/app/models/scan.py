from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class SecurityScan(Base):
    __tablename__ = "security_scans"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("authorized_targets.id"), nullable=False)
    scan_name = Column(String(150), nullable=False)
    scan_type = Column(String(50), default="full") # full, incremental, targeted_api, retest
    status = Column(String(50), default="pending", index=True) # pending, running, completed, stopped, failed
    triggered_by = Column(String(100), default="system")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    total_endpoints = Column(Integer, default=0)
    tested_endpoints = Column(Integer, default=0)
    vulnerabilities_count = Column(Integer, default=0)
    config_json = Column(JSON, nullable=True) # Selected categories, rate limits, role accounts
    stop_reason = Column(String(255), nullable=True) # e.g. "Safety engine threshold triggered"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    target = relationship("AuthorizedTarget", back_populates="scans")
    agent_logs = relationship("AgentExecutionLog", back_populates="scan", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")

class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("security_scans.id"), nullable=False)
    agent_name = Column(String(100), nullable=False, index=True) 
    # e.g., "Change Detection Agent", "Recon Discovery Agent", "Inventory Agent", 
    # "Attack Planner", "Access Control Agent", "Business Logic Agent",
    # "Safety & Policy Agent", "Verification Agent", "Risk Assessment Agent", "Reporting Agent", "Retest Agent"
    step_name = Column(String(150), nullable=False)
    status = Column(String(50), default="info") # info, started, completed, warning, error, alert
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    execution_duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("SecurityScan", back_populates="agent_logs")

