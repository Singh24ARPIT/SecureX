import csv
import io
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.vulnerability import Vulnerability
from app.models.api_endpoint import ApiEndpoint

class ReportingAgent:
    """
    AGENT 9: Reporting Agent
    Generates actionable executive security summaries, detailed vulnerability findings,
    reproduction evidence, remediation paths, and exportable reports (CSV / JSON / HTML printable).
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_report_data(self) -> Dict[str, Any]:
        vulns = self.db.query(Vulnerability).all()
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "informational": 0}
        category_counts = {}
        items = []

        for v in vulns:
            sev = v.severity.lower()
            if sev in severity_counts:
                severity_counts[sev] += 1
            else:
                severity_counts[sev] = 1

            cat = v.category
            category_counts[cat] = category_counts.get(cat, 0) + 1

            endpoint_info = "N/A"
            http_method = "N/A"
            if v.endpoint:
                endpoint_info = v.endpoint.path
                http_method = v.endpoint.method

            items.append({
                "id": v.id,
                "title": v.title,
                "category": v.category,
                "affected_api": endpoint_info,
                "http_method": http_method,
                "severity": v.severity.upper(),
                "cvss_score": v.cvss_score,
                "status": v.status.upper(),
                "description": v.description,
                "business_impact": v.business_impact or "Commercial impact to operations",
                "recommended_remediation": v.remediation_guidance or "Apply parameter validation and access checks",
                "responsible_owner": v.responsible_owner,
                "created_at": v.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        total = len(vulns)
        return {
            "title": "SentinelAI Executive Cybersecurity Assessment Report",
            "platform": "TBO Voyagehack 4.0 Security Scanner",
            "total_findings": total,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "findings": items
        }

    def export_csv(self) -> str:
        report = self.generate_report_data()
        output = io.StringIO()
        fieldnames = [
            "id", "title", "category", "affected_api", "http_method", 
            "severity", "cvss_score", "status", "business_impact", 
            "recommended_remediation", "responsible_owner", "created_at"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for item in report["findings"]:
            row = {k: item.get(k, "") for k in fieldnames}
            writer.writerow(row)
        return output.getvalue()

