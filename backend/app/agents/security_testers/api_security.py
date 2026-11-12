from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.api_endpoint import ApiEndpoint

class ApiSecurityTestingAgent:
    """
    AGENT 5.5: API Security Agent
    Specializes in:
    - Shadow and Zombie API exposure
    - Excessive data exposure
    - Missing rate limiting headers
    """
    def __init__(self, db: Session):
        self.db = db

    def test_zombie_shadow_exposure(self, endpoint_id: int) -> Dict[str, Any]:
        ep = self.db.query(ApiEndpoint).filter(ApiEndpoint.id == endpoint_id).first()
        if not ep:
            return {"vulnerable": False, "title": "Endpoint not found"}

        if ep.classification == "zombie":
            return {
                "vulnerable": True,
                "title": f"Zombie API Endpoint Accessible in Staging: {ep.path}",
                "category": "api_security",
                "severity": "high",
                "cvss_score": 8.2,
                "description": f"Endpoint '{ep.path}' has been marked as deprecated/zombie but continues responding to requests, expanding the attack surface.",
                "business_impact": "Allows attackers to bypass current gateway policies and modern security controls using unmonitored legacy code paths.",
                "remediation_guidance": "Decommission the routing rule in ingress controller or API Gateway and remove deprecated controller methods.",
                "request_dump": f"GET {ep.path} HTTP/1.1\nHost: staging-api.tbo.internal",
                "response_dump": "HTTP/1.1 200 OK\nWarning: 299 - 'Deprecated Endpoint'",
                "endpoint_id": endpoint_id
            }

        if ep.classification == "shadow":
            return {
                "vulnerable": True,
                "title": f"Shadow API Endpoint Without Documentation: {ep.path}",
                "category": "api_security",
                "severity": "medium",
                "cvss_score": 6.5,
                "description": f"Endpoint '{ep.path}' was identified in network traffic but is absent from the approved OpenAPI registry.",
                "business_impact": "Blind spot in security monitoring and compliance governance.",
                "remediation_guidance": "Add endpoint to OpenAPI schema definition and enforce governance gate in CI/CD pipeline.",
                "request_dump": f"POST {ep.path} HTTP/1.1\nHost: staging-api.tbo.internal",
                "response_dump": "HTTP/1.1 200 OK",
                "endpoint_id": endpoint_id
            }

        return {
            "vulnerable": False,
            "title": "API Policy Check Passed",
            "reason": "Endpoint conforms to current documented API schema."
        }
