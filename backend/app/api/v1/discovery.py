from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_endpoint import ApiEndpoint, DeploymentEvent
from app.models.target import AuthorizedTarget
from app.models.user import User
from app.schemas.api_endpoint import (
    ApiEndpointResponse,
    DeploymentEventCreate,
    DeploymentEventResponse
)
from app.api.deps import get_current_user, require_permission, record_audit
from app.agents.recon_discovery import ReconDiscoveryAgent
from app.agents.change_detection import ChangeDetectionAgent

router = APIRouter(prefix="/discovery", tags=["API Discovery & Recon"])

@router.get("/endpoints", response_model=List[ApiEndpointResponse])
def get_discovered_endpoints(
    target_id: Optional[int] = None,
    classification: Optional[str] = None, # active, zombie, shadow
    method: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:read"))
):
    query = db.query(ApiEndpoint)
    if target_id:
        query = query.filter(ApiEndpoint.target_id == target_id)
    if classification:
        query = query.filter(ApiEndpoint.classification == classification)
    if method:
        query = query.filter(ApiEndpoint.method == method.upper())
    if search:
        query = query.filter(
            (ApiEndpoint.path.ilike(f"%{search}%")) | 
            (ApiEndpoint.summary.ilike(f"%{search}%"))
        )
    return query.all()

@router.get("/endpoints/{endpoint_id}", response_model=ApiEndpointResponse)
def get_endpoint_detail(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:read"))
):
    ep = db.query(ApiEndpoint).filter(ApiEndpoint.id == endpoint_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return ep

@router.post("/scan/{target_id}")
def trigger_recon_scan(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:discover"))
):
    target = db.query(AuthorizedTarget).filter(AuthorizedTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Authorized target not found")
    
    agent = ReconDiscoveryAgent(db)
    result = agent.discover_staging_apis(target_id)
    
    record_audit(
        db, current_user.id, "discovery:scan", "target", str(target_id),
        {"endpoints_mapped": result["total_endpoints_discovered"]}
    )
    return {
        "message": "Reconnaissance & API Discovery completed successfully",
        "details": result
    }

@router.post("/webhook/deploy", response_model=DeploymentEventResponse)
def simulate_deployment_webhook(
    event_in: DeploymentEventCreate,
    db: Session = Depends(get_db)
):
    """
    AGENT 1: Change Detection Agent Webhook Endpoint.
    Receives deployment events (CI/CD / GitHub action webhook) and compares API inventory.
    """
    target = db.query(AuthorizedTarget).filter(AuthorizedTarget.id == event_in.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not registered in authorized inventory")
    
    agent = ChangeDetectionAgent(db)
    result = agent.process_deployment_event(event_in.model_dump())
    
    deployment = db.query(DeploymentEvent).filter(DeploymentEvent.id == result["deployment_id"]).first()
    return deployment

@router.get("/deployments", response_model=List[DeploymentEventResponse])
def get_deployment_history(
    target_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:read"))
):
    query = db.query(DeploymentEvent)
    if target_id:
        query = query.filter(DeploymentEvent.target_id == target_id)
    return query.order_by(DeploymentEvent.created_at.desc()).limit(20).all()

