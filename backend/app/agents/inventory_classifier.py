from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.api_endpoint import ApiEndpoint, ApiInventoryHistory

class ApiInventoryAgent:
    """
    AGENT 3: API Inventory Agent
    Classifies endpoints into Active, Zombie, and Shadow APIs.
    Generates actionable remediation recommendations to decommission or document endpoints.
    """
    def __init__(self, db: Session):
        self.db = db

    def evaluate_inventory(self, target_id: int) -> Dict[str, Any]:
        endpoints = self.db.query(ApiEndpoint).filter(ApiEndpoint.target_id == target_id).all()
        
        now = datetime.utcnow()
        active_list = []
        zombie_list = []
        shadow_list = []

        for ep in endpoints:
            # Classification logic
            if "legacy" in ep.path.lower() or "old" in ep.path.lower() or "v1/deprecated" in ep.path.lower():
                ep.classification = "zombie"
                ep.recommendation = "Decommission legacy route and revoke external route mapping in ingress."
                zombie_list.append(ep)
            elif "internal" in ep.path.lower() or "undocumented" in ep.path.lower():
                ep.classification = "shadow"
                ep.recommendation = "Register endpoint in OpenAPI documentation and enforce strict mutual TLS / gateway auth."
                shadow_list.append(ep)
            else:
                ep.classification = "active"
                ep.recommendation = "Maintain regular continuous security testing in CI/CD pipeline."
                active_list.append(ep)

        self.db.commit()

        return {
            "target_id": target_id,
            "total_inventory_count": len(endpoints),
            "active_count": len(active_list),
            "zombie_count": len(zombie_list),
            "shadow_count": len(shadow_list),
            "recommendations": [
                {
                    "endpoint_id": ep.id,
                    "method": ep.method,
                    "path": ep.path,
                    "classification": ep.classification,
                    "recommendation": ep.recommendation
                }
                for ep in zombie_list + shadow_list
            ]
        }

