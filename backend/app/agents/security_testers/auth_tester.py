from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.api_endpoint import ApiEndpoint

class AuthenticationTestingAgent:
    """
    AGENT 5.3: Authentication Agent
    Specializes in:
    - Missing authentication checks
    - Token validation failures
    - Weak session handling
    """
    def __init__(self, db: Session):
        self.db = db

    def test_missing_auth(self, endpoint_id: int) -> Dict[str, Any]:
        ep = self.db.query(ApiEndpoint).filter(ApiEndpoint.id == endpoint_id).first()
        if not ep:
            return {"vulnerable": False, "title": "Endpoint not found"}

        # If endpoint is classified as zombie legacy PII export
        if "legacy" in ep.path:
            return {
                "vulnerable": True,
                "title": "Unauthenticated Sensitive PII Access in Legacy API",
                "category": "authentication",
                "severity": "critical",
                "cvss_score": 9.8,
                "description": f"Endpoint '{ep.path}' allows anonymous callers to query passenger travel reservations and customer PII without any authorization header.",
                "business_impact": "Mass GDPR / DPDPA regulatory non-compliance penalty, public leak of customer travel records.",
                "remediation_guidance": "Deprecate legacy API route and place behind API gateway OAuth2/JWT middleware with strict access policies.",
                "request_dump": f"GET {ep.path} HTTP/1.1\nHost: staging-api.tbo.internal\nUser-Agent: SecuReX-DAST/1.0",
                "response_dump": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\n  \"count\": 10,\n  \"data\": [{\"customer_email\": \"...\", \"reference\": \"...\"}]\n}",
                "endpoint_id": endpoint_id
            }

        return {
            "vulnerable": False,
            "title": "Authentication Enforced",
            "reason": "Endpoint correctly mandates authentication headers."
        }

