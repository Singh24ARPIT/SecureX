from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("authorized_targets.id"), nullable=False)
    path = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True) # GET, POST, PUT, PATCH, DELETE
    summary = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    auth_required = Column(Boolean, default=True)
    required_roles = Column(String(255), default="authenticated") # e.g. "admin,agency_admin"
    request_schema = Column(JSON, nullable=True)
    response_schema = Column(JSON, nullable=True)
    
    # Classification: active, zombie (old/unused but reachable), shadow (in use but undocumented)
    classification = Column(String(20), default="active", index=True)
    risk_score = Column(Float, default=1.0)
    
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_deprecated = Column(Boolean, default=False)
    recommendation = Column(Text, nullable=True) # e.g. "Decommission unused zombie endpoint", "Add OpenAPI schema"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    target = relationship("AuthorizedTarget", back_populates="endpoints")
    parameters = relationship("ApiParameter", back_populates="endpoint", cascade="all, delete-orphan")
    history = relationship("ApiInventoryHistory", back_populates="endpoint", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="endpoint", cascade="all, delete-orphan")

class ApiParameter(Base):
    __tablename__ = "api_parameters"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), nullable=False)
    name = Column(String(100), nullable=False)
    in_location = Column(String(20), nullable=False) # path, query, header, body
    data_type = Column(String(50), default="string")
    is_required = Column(Boolean, default=False)
    description = Column(String(255), nullable=True)
    example_value = Column(String(255), nullable=True)

    endpoint = relationship("ApiEndpoint", back_populates="parameters")

class ApiInventoryHistory(Base):
    __tablename__ = "api_inventory_history"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), nullable=False)
    change_type = Column(String(50), nullable=False) # added, modified, deprecated, classification_changed
    old_hash = Column(String(64), nullable=True)
    new_hash = Column(String(64), nullable=True)
    diff_summary = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)

    endpoint = relationship("ApiEndpoint", back_populates="history")

class DeploymentEvent(Base):
    __tablename__ = "deployment_events"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("authorized_targets.id"), nullable=False)
    service_name = Column(String(100), nullable=False)
    commit_sha = Column(String(64), nullable=False)
    branch = Column(String(100), default="main")
    triggered_by = Column(String(100), default="ci/cd-pipeline")
    event_type = Column(String(50), default="api_deploy") # api_deploy, schema_update, hotfix
    payload_json = Column(JSON, nullable=True)
    status = Column(String(50), default="processed") # pending, processed, scan_triggered
    created_at = Column(DateTime, default=datetime.utcnow)

    target = relationship("AuthorizedTarget", back_populates="deployment_events")
