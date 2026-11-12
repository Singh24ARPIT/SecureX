from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.api.deps import get_current_user, require_permission

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

class AuditLogItem(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details_json: Optional[dict] = None
    ip_address: str
    timestamp: datetime

    class Config:
        from_attributes = True

@router.get("/logs", response_model=List[AuditLogItem])
def get_audit_trail(
    limit: int = 50,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit:read"))
):
    query = db.query(AuditLog)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
