from typing import List, Dict, Any
from pydantic import BaseModel

class OverviewStatsResponse(BaseModel):
    total_apis: int
    active_apis: int
    zombie_apis: int
    shadow_apis: int
    total_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    active_scans: int
    verified_vulnerabilities: int
    security_health_score: float # 0 to 100

class ApiStatsResponse(BaseModel):
    by_method: Dict[str, int]
    by_classification: Dict[str, int]
    auth_coverage_pct: float
    high_risk_endpoints: int

class VulnerabilityTrendsResponse(BaseModel):
    trends: List[Dict[str, Any]]
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    false_positive_rate: float
    remediation_rate: float

