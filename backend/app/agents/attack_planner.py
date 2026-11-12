from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.api_endpoint import ApiEndpoint

class AttackPlanningAgent:
    """
    AGENT 4: AI Attack Planning Agent
    Analyzes API functionality and determines appropriate targeted tests rather than blindly spraying payloads.
    Generates a structured test plan with rationale, expected behavior, risk level, and required role.
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_plan(self, target_id: int, selected_categories: List[str]) -> List[Dict[str, Any]]:
        endpoints = self.db.query(ApiEndpoint).filter(ApiEndpoint.target_id == target_id).all()
        plan = []

        for ep in endpoints:
            path_lower = ep.path.lower()

            # 1. Booking APIs -> IDOR & Access Control
            if "booking" in path_lower and ("access_control" in selected_categories):
                if ep.method in ["GET", "PUT", "DELETE"]:
                    plan.append({
                        "endpoint_id": ep.id,
                        "path": ep.path,
                        "method": ep.method,
                        "test_category": "access_control",
                        "test_name": "Cross-Agency IDOR Validation",
                        "reason": "Booking query/modification APIs frequently expose data across tenant boundaries if tenant isolation is missing.",
                        "expected_secure_behavior": "HTTP 403 Forbidden when requesting resources belonging to another travel agency.",
                        "risk_level": "Critical",
                        "required_role": "agency_101 vs agency_202 test account"
                    })

            # 2. Booking / Payment APIs -> Business Logic & Fare Manipulation
            if ("booking" in path_lower or "fare" in path_lower or "price" in path_lower) and ep.method == "POST" and ("business_logic" in selected_categories):
                plan.append({
                    "endpoint_id": ep.id,
                    "path": ep.path,
                    "method": ep.method,
                    "test_category": "business_logic",
                    "test_name": "Client-Side Fare Manipulation Check",
                    "reason": "Client-controlled booking amounts must be validated against server-side inventory pricing.",
                    "expected_secure_behavior": "HTTP 400 Bad Request if submitted fare differs from server calculation.",
                    "risk_level": "Critical",
                    "required_role": "agency_101"
                })

            # 3. Refund APIs -> Duplicate Refund Workflow Abuse
            if "refund" in path_lower and ("business_logic" in selected_categories):
                plan.append({
                    "endpoint_id": ep.id,
                    "path": ep.path,
                    "method": ep.method,
                    "test_category": "business_logic",
                    "test_name": "Duplicate Refund Workflow Abuse Check",
                    "reason": "Cancellation and refund routes must prevent multiple payouts for the same booking reference.",
                    "expected_secure_behavior": "HTTP 409 Conflict when refund is attempted more than once on the same transaction.",
                    "risk_level": "High",
                    "required_role": "agency_101"
                })

            # 4. Authentication & Access
            if ep.auth_required and ("authentication" in selected_categories):
                plan.append({
                    "endpoint_id": ep.id,
                    "path": ep.path,
                    "method": ep.method,
                    "test_category": "authentication",
                    "test_name": "Missing Authentication Bypass Check",
                    "reason": "Verify that endpoint strictly enforces credentials before returning data.",
                    "expected_secure_behavior": "HTTP 401 Unauthorized when request lacks authorization token/header.",
                    "risk_level": "High",
                    "required_role": "unauthenticated"
                })

            # 5. API Security & Zombie Data Exposure
            if ep.classification in ["zombie", "shadow"] and ("api_security" in selected_categories):
                plan.append({
                    "endpoint_id": ep.id,
                    "path": ep.path,
                    "method": ep.method,
                    "test_category": "api_security",
                    "test_name": "Excessive Data Exposure & Zombie Endpoint Audit",
                    "reason": "Unmaintained endpoints frequently expose sensitive customer PII without rate limits or audit trails.",
                    "expected_secure_behavior": "Endpoint should be disabled or return 404/410 Gone.",
                    "risk_level": "Critical",
                    "required_role": "unauthenticated"
                })

        return plan

