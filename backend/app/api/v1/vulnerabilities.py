from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vulnerability import (
    Vulnerability,
    RemediationRecord,
    VulnerabilityEvidence,
    RetestHistory
)
from app.models.user import User
from app.schemas.vulnerability import (
    VulnerabilityResponse,
    RemediationRequest,
    RetestRequest,
    RetestHistoryResponse
)
from app.api.deps import get_current_user, require_permission, record_audit
from app.agents.verification import VulnerabilityVerificationAgent
from app.agents.retesting import RetestingAgent

router = APIRouter(prefix="/vulnerabilities", tags=["Vulnerability Management"])

@router.get("", response_model=List[VulnerabilityResponse])
def get_vulnerabilities(
    scan_id: Optional[int] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vulns:read"))
):
    query = db.query(Vulnerability)
    if scan_id:
        query = query.filter(Vulnerability.scan_id == scan_id)
    if category:
        query = query.filter(Vulnerability.category == category)
    if severity:
        query = query.filter(Vulnerability.severity == severity.lower())
    if status:
        query = query.filter(Vulnerability.status == status.lower())
    if search:
        query = query.filter(
            (Vulnerability.title.ilike(f"%{search}%")) |
            (Vulnerability.description.ilike(f"%{search}%"))
        )
    return query.order_by(Vulnerability.cvss_score.desc(), Vulnerability.created_at.desc()).all()

@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
def get_vulnerability_detail(
    vuln_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vulns:read"))
):
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln

@router.post("/{vuln_id}/verify")
def trigger_agent_verification(
    vuln_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vulns:verify"))
):
    """
    AGENT 7: Vulnerability Verification Agent.
    Rechecks detected finding to filter out false positives and confirm reproduction proof.
    """
    agent = VulnerabilityVerificationAgent(db)
    result = agent.verify_vulnerability(vuln_id)
    record_audit(db, current_user.id, "vuln:verify", "vulnerability", str(vuln_id), result)
    return result

@router.post("/{vuln_id}/remediate")
def submit_remediation(
    vuln_id: int,
    remediation_in: RemediationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vulns:update"))
):
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    vuln.status = "remediated"
    vuln.updated_at = datetime.utcnow()

    record = RemediationRecord(
        vulnerability_id=vuln.id,
        action_taken=remediation_in.action_taken,
        patch_details=remediation_in.patch_details,
        developer_notes=remediation_in.developer_notes,
        marked_fixed_by=current_user.full_name or current_user.username
    )
    db.add(record)
    db.commit()

    record_audit(db, current_user.id, "vuln:remediate", "vulnerability", str(vuln.id), {"action": remediation_in.action_taken})
    return {"message": "Remediation logged. Status updated to 'remediated'. Ready for retesting.", "vuln_id": vuln.id}

@router.post("/{vuln_id}/retest")
def retest_vulnerability(
    vuln_id: int,
    retest_in: Optional[RetestRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vulns:retest"))
):
    """
    AGENT 10: Retesting Agent.
    Executes controlled reproduction test against fixed staging application.
    Updates status to 'resolved' if fixed or 'detected' if flaw still reproduces.
    """
    agent = RetestingAgent(db)
    notes = retest_in.notes if retest_in and retest_in.notes else f"Triggered by {current_user.username}"
    result = agent.retest_vulnerability(vuln_id, test_notes=notes)
    
    record_audit(db, current_user.id, "vuln:retest", "vulnerability", str(vuln_id), result)
    return result

