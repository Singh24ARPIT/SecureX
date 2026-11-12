from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_endpoint import ApiEndpoint
from app.models.scan import SecurityScan
from app.models.vulnerability import Vulnerability
from app.models.user import User
from app.schemas.dashboard import OverviewStatsResponse, ApiStatsResponse, VulnerabilityTrendsResponse
from app.api.deps import get_current_user, require_permission

router = APIRouter(prefix="/dashboard", tags=["Overview Dashboard"])

@router.get("/overview", response_model=OverviewStatsResponse)
def get_overview_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:read"))
):
    total_apis = db.query(ApiEndpoint).count()
    active_apis = db.query(ApiEndpoint).filter(ApiEndpoint.classification == "active").count()
    zombie_apis = db.query(ApiEndpoint).filter(ApiEndpoint.classification == "zombie").count()
    shadow_apis = db.query(ApiEndpoint).filter(ApiEndpoint.classification == "shadow").count()

    total_vulns = db.query(Vulnerability).count()
    critical_vulns = db.query(Vulnerability).filter(Vulnerability.severity == "critical").count()
    high_vulns = db.query(Vulnerability).filter(Vulnerability.severity == "high").count()
    medium_vulns = db.query(Vulnerability).filter(Vulnerability.severity == "medium").count()
    low_vulns = db.query(Vulnerability).filter(Vulnerability.severity == "low").count()

    active_scans = db.query(SecurityScan).filter(SecurityScan.status == "running").count()
    verified_vulns = db.query(Vulnerability).filter(Vulnerability.status == "verified").count()
    resolved_vulns = db.query(Vulnerability).filter(Vulnerability.status == "resolved").count()

    # Calculate overall security health score (0 - 100):
    # Starts at 100, deducted by critical (-15), high (-8), medium (-4), zombie (-5), shadow (-3)
    # Recovered by resolved vulnerabilities (+5)
    score = 100.0 - (critical_vulns * 15.0) - (high_vulns * 8.0) - (medium_vulns * 4.0) - (zombie_apis * 5.0) - (shadow_apis * 3.0) + (resolved_vulns * 6.0)
    score = max(5.0, min(100.0, score))

    return OverviewStatsResponse(
        total_apis=total_apis,
        active_apis=active_apis,
        zombie_apis=zombie_apis,
        shadow_apis=shadow_apis,
        total_vulnerabilities=total_vulns,
        critical_vulnerabilities=critical_vulns,
        high_vulnerabilities=high_vulns,
        medium_vulnerabilities=medium_vulns,
        low_vulnerabilities=low_vulns,
        active_scans=active_scans,
        verified_vulnerabilities=verified_vulns,
        security_health_score=round(score, 1)
    )

@router.get("/api-stats", response_model=ApiStatsResponse)
def get_api_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("apis:read"))
):
    endpoints = db.query(ApiEndpoint).all()
    methods = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}
    classifications = {"active": 0, "zombie": 0, "shadow": 0}
    auth_count = 0
    high_risk = 0

    for ep in endpoints:
        m = ep.method.upper()
        methods[m] = methods.get(m, 0) + 1
        
        c = ep.classification.lower()
        classifications[c] = classifications.get(c, 0) + 1
        
        if ep.auth_required:
            auth_count += 1
        if ep.risk_score >= 8.0:
            high_risk += 1

    total = len(endpoints)
    coverage = round((auth_count / max(total, 1)) * 100.0, 1)

    return ApiStatsResponse(
        by_method=methods,
        by_classification=classifications,
        auth_coverage_pct=coverage,
        high_risk_endpoints=high_risk
    )

@router.get("/trends", response_model=VulnerabilityTrendsResponse)
def get_vulnerability_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vulns:read"))
):
    vulns = db.query(Vulnerability).all()
    cat_counts = {}
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    fp_count = 0
    resolved_count = 0

    for v in vulns:
        cat_counts[v.category] = cat_counts.get(v.category, 0) + 1
        s = v.severity.lower()
        if s in sev_counts:
            sev_counts[s] += 1
        if v.status == "false_positive":
            fp_count += 1
        if v.status == "resolved":
            resolved_count += 1

    total = max(len(vulns), 1)
    fp_rate = round((fp_count / total) * 100.0, 1)
    remediation_rate = round((resolved_count / total) * 100.0, 1)

    # Simulated 7-day trend series for charting
    trends_series = [
        {"day": "Day -6", "detected": 1, "resolved": 0},
        {"day": "Day -5", "detected": 2, "resolved": 1},
        {"day": "Day -4", "detected": 1, "resolved": 0},
        {"day": "Day -3", "detected": 3, "resolved": 2},
        {"day": "Day -2", "detected": 2, "resolved": 1},
        {"day": "Yesterday", "detected": 4, "resolved": 2},
        {"day": "Today", "detected": len(vulns), "resolved": resolved_count}
    ]

    return VulnerabilityTrendsResponse(
        trends=trends_series,
        by_category=cat_counts,
        by_severity=sev_counts,
        false_positive_rate=fp_rate,
        remediation_rate=remediation_rate
    )

