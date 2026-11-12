from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.models.scan import SecurityScan, AgentExecutionLog
from app.models.target import AuthorizedTarget
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanResponse, ScanDetailResponse, AgentLogResponse
from app.api.deps import get_current_user, require_permission, record_audit
from app.agents.orchestrator import MultiAgentOrchestrator

router = APIRouter(prefix="/scans", tags=["Security Scanning"])

def run_background_scan(scan_id: int):
    db = SessionLocal()
    try:
        orchestrator = MultiAgentOrchestrator(db)
        orchestrator.run_scan(scan_id)
    finally:
        db.close()

@router.get("", response_model=List[ScanResponse])
def get_scans(
    target_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:read"))
):
    query = db.query(SecurityScan)
    if target_id:
        query = query.filter(SecurityScan.target_id == target_id)
    if status:
        query = query.filter(SecurityScan.status == status)
    return query.order_by(SecurityScan.created_at.desc()).all()

@router.post("", response_model=ScanResponse)
def start_scan(
    scan_in: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:create"))
):
    target = db.query(AuthorizedTarget).filter(AuthorizedTarget.id == scan_in.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    if not target.is_approved:
        raise HTTPException(status_code=403, detail="Target has not been approved for security testing")

    scan_name = scan_in.scan_name or f"DAST Scan - {target.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    
    scan = SecurityScan(
        target_id=target.id,
        scan_name=scan_name,
        scan_type=scan_in.scan_type,
        status="pending",
        triggered_by=current_user.full_name or current_user.username,
        config_json={
            "selected_categories": scan_in.selected_categories,
            "rate_limit_rps": scan_in.rate_limit_rps or target.rate_limit_rps,
            "auto_verify": scan_in.auto_verify
        }
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    record_audit(db, current_user.id, "scan:start", "scan", str(scan.id), {"target": target.name, "type": scan.scan_type})

    # Run multi-agent orchestrator synchronously or in background
    # Running synchronously for instant feedback in interactive demos or hackathons
    orchestrator = MultiAgentOrchestrator(db)
    orchestrator.run_scan(scan.id)
    db.refresh(scan)

    return scan

@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_detail(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:read"))
):
    scan = db.query(SecurityScan).filter(SecurityScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.post("/{scan_id}/stop")
def stop_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:stop"))
):
    scan = db.query(SecurityScan).filter(SecurityScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan.status = "stopped"
    scan.stop_reason = f"Manually aborted by {current_user.username}"
    scan.end_time = datetime.utcnow()
    db.commit()

    record_audit(db, current_user.id, "scan:stop", "scan", str(scan.id))
    return {"message": "Scan execution halted", "scan_id": scan.id}

@router.get("/{scan_id}/logs", response_model=List[AgentLogResponse])
def get_scan_agent_logs(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:read"))
):
    return db.query(AgentExecutionLog).filter(
        AgentExecutionLog.scan_id == scan_id
    ).order_by(AgentExecutionLog.created_at.asc()).all()

