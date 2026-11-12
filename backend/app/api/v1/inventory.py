from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_endpoint import ApiEndpoint, ApiInventoryHistory
from app.models.user import User
from app.schemas.api_endpoint import EndpointClassificationUpdate, ApiEndpointResponse
from app.api.deps import get_current_user, require_permission, record_audit
from app.agents.inventory_classifier import ApiInventoryAgent

router = APIRouter(prefix="/inventory", tags=["API Inventory & Governance"])

@router.get("/stats")
def get_inventory_stats(
    target_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:read"))
):
    query = db.query(ApiEndpoint)
    if target_id:
        query = query.filter(ApiEndpoint.target_id == target_id)
    
    total = query.count()
    active = query.filter(ApiEndpoint.classification == "active").count()
    zombie = query.filter(ApiEndpoint.classification == "zombie").count()
    shadow = query.filter(ApiEndpoint.classification == "shadow").count()
    deprecated = query.filter(ApiEndpoint.is_deprecated == True).count()
    
    return {
        "total_endpoints": total,
        "active_apis": active,
        "zombie_apis": zombie,
        "shadow_apis": shadow,
        "deprecated_apis": deprecated,
        "governance_coverage_score": round(((active / max(total, 1)) * 100), 1)
    }

@router.post("/reclassify/{target_id}")
def run_inventory_classification(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:classify"))
):
    agent = ApiInventoryAgent(db)
    result = agent.evaluate_inventory(target_id)
    record_audit(db, current_user.id, "inventory:classify", "target", str(target_id), result)
    return {
        "message": "API Inventory Classification refreshed",
        "result": result
    }

@router.put("/endpoints/{endpoint_id}/classify", response_model=ApiEndpointResponse)
def update_endpoint_classification(
    endpoint_id: int,
    update_in: EndpointClassificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:classify"))
):
    ep = db.query(ApiEndpoint).filter(ApiEndpoint.id == endpoint_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    old_class = ep.classification
    ep.classification = update_in.classification
    if update_in.recommendation:
        ep.recommendation = update_in.recommendation
    
    hist = ApiInventoryHistory(
        endpoint_id=ep.id,
        change_type="classification_changed",
        diff_summary=f"Manually reclassified from '{old_class}' to '{update_in.classification}' by {current_user.username}"
    )
    db.add(hist)
    db.commit()
    db.refresh(ep)
    
    record_audit(db, current_user.id, "inventory:reclassify_endpoint", "endpoint", str(ep.id), {"from": old_class, "to": ep.classification})
    return ep
