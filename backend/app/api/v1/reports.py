from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, require_permission, record_audit
from app.agents.reporting import ReportingAgent

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/summary")
def get_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("reports:read"))
):
    agent = ReportingAgent(db)
    return agent.generate_report_data()

@router.get("/export/csv")
def export_csv_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("reports:generate"))
):
    agent = ReportingAgent(db)
    csv_data = agent.export_csv()
    record_audit(db, current_user.id, "report:export_csv", "report")
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=securex_security_report.csv"}
    )

@router.get("/export/json")
def export_json_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("reports:generate"))
):
    agent = ReportingAgent(db)
    report_data = agent.generate_report_data()
    record_audit(db, current_user.id, "report:export_json", "report")
    return report_data

