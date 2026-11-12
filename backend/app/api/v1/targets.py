from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.target import AuthorizedTarget
from app.models.user import User
from app.schemas.target import TargetCreate, TargetUpdate, TargetResponse
from app.api.deps import get_current_user, require_permission, record_audit

router = APIRouter(prefix="/targets", tags=["Authorized Targets"])

@router.get("", response_model=List[TargetResponse])
def get_targets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("targets:read"))
):
    return db.query(AuthorizedTarget).all()

@router.post("", response_model=TargetResponse)
def create_target(
    target_in: TargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("targets:create"))
):
    existing = db.query(AuthorizedTarget).filter(AuthorizedTarget.name == target_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Target with this name already exists")
    
    target = AuthorizedTarget(
        name=target_in.name,
        target_url=target_in.target_url,
        environment=target_in.environment,
        is_approved=target_in.is_approved,
        approval_notes=target_in.approval_notes,
        approved_by=current_user.full_name or current_user.username,
        rate_limit_rps=target_in.rate_limit_rps
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    
    record_audit(db, current_user.id, "target:create", "target", str(target.id), {"name": target.name, "url": target.target_url})
    return target

@router.get("/{target_id}", response_model=TargetResponse)
def get_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("targets:read"))
):
    target = db.query(AuthorizedTarget).filter(AuthorizedTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@router.put("/{target_id}", response_model=TargetResponse)
def update_target(
    target_id: int,
    target_in: TargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("targets:update"))
):
    target = db.query(AuthorizedTarget).filter(AuthorizedTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    update_data = target_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target, field, value)
    
    db.commit()
    db.refresh(target)
    record_audit(db, current_user.id, "target:update", "target", str(target.id), update_data)
    return target

@router.delete("/{target_id}")
def delete_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("targets:delete"))
):
    target = db.query(AuthorizedTarget).filter(AuthorizedTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    db.delete(target)
    db.commit()
    record_audit(db, current_user.id, "target:delete", "target", str(target_id), {"name": target.name})
    return {"message": f"Target '{target.name}' deleted successfully"}
