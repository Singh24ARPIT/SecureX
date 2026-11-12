from typing import Tuple, Dict, Any, Optional
import time
from sqlalchemy.orm import Session
from app.models.target import AuthorizedTarget

class SafetyPolicyAgent:
    """
    AGENT 6: Safety & Policy Agent
    Mandatory safety gatekeeper enforcing scope boundaries, approved targets,
    rate limiting, and preventing destructive operations.
    """
    def __init__(self, db: Session):
        self.db = db
    
    def validate_target_scope(self, target_id: int) -> Tuple[bool, str, Optional[AuthorizedTarget]]:
        target = self.db.query(AuthorizedTarget).filter(AuthorizedTarget.id == target_id).first()
        if not target:
            return False, "Target not registered in inventory", None
        
        if not target.is_approved:
            return False, f"Target '{target.name}' is NOT approved by Security Architecture Board", target
        
        if target.environment not in ["staging", "dev", "sandbox"]:
            return False, f"Testing prohibited in environment '{target.environment}'. Only staging/sandbox permitted.", target
            
        return True, "Target in approved scope", target

    def check_application_health(self, target: AuthorizedTarget) -> Tuple[bool, str]:
        # Health check on target URL/service
        if target.health_status == "unreachable":
            return False, "Target health status is unreachable. Halting scan to prevent service interruption."
        return True, "Target health check healthy"

    def enforce_rate_limit(self, target: AuthorizedTarget, last_request_time: float) -> float:
        # Enforce rate limit (e.g. 5 RPS => 0.20s delay)
        interval = 1.0 / max(target.rate_limit_rps, 1.0)
        elapsed = time.time() - last_request_time
        if elapsed < interval:
            time.sleep(interval - elapsed)
        return time.time()

    def filter_safe_test_categories(self, requested_categories: list) -> list:
        # Guarantee no DoS or destructive tests
        safe_allowed = [
            "access_control",
            "business_logic",
            "authentication",
            "injection",
            "api_security"
        ]
        sanitized = [cat for cat in requested_categories if cat in safe_allowed]
        return sanitized

