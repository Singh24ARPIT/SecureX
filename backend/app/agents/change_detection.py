import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.api_endpoint import ApiEndpoint, ApiInventoryHistory, DeploymentEvent
from app.models.target import AuthorizedTarget

class ChangeDetectionAgent:
    """
    AGENT 1: Change Detection Agent
    Monitors deployment events, compares current API inventory with previous versions,
    identifies changes, and triggers targeted security testing.
    """
    def __init__(self, db: Session):
        self.db = db

    def process_deployment_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        target_id = event_data.get("target_id")
        service_name = event_data.get("service_name", "travel-booking-service")
        commit_sha = event_data.get("commit_sha", hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:8])
        endpoints_data = event_data.get("endpoints", [])
        
        deployment = DeploymentEvent(
            target_id=target_id,
            service_name=service_name,
            commit_sha=commit_sha,
            branch=event_data.get("branch", "main"),
            triggered_by=event_data.get("triggered_by", "CI/CD Webhook"),
            event_type=event_data.get("event_type", "api_deploy"),
            payload_json=event_data,
            status="processed"
        )
        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)

        changes_detected = []
        for ep_info in endpoints_data:
            path = ep_info.get("path")
            method = ep_info.get("method", "GET").upper()
            
            existing = self.db.query(ApiEndpoint).filter(
                ApiEndpoint.target_id == target_id,
                ApiEndpoint.path == path,
                ApiEndpoint.method == method
            ).first()

            ep_content_str = json.dumps(ep_info, sort_keys=True)
            current_hash = hashlib.sha256(ep_content_str.encode()).hexdigest()

            if not existing:
                # Newly deployed endpoint detected!
                new_endpoint = ApiEndpoint(
                    target_id=target_id,
                    path=path,
                    method=method,
                    summary=ep_info.get("summary", "Discovered endpoint"),
                    description=ep_info.get("description", ""),
                    auth_required=ep_info.get("auth_required", True),
                    required_roles=ep_info.get("required_roles", "agency_admin"),
                    classification="active",
                    risk_score=ep_info.get("risk_score", 5.0)
                )
                self.db.add(new_endpoint)
                self.db.commit()
                self.db.refresh(new_endpoint)

                history = ApiInventoryHistory(
                    endpoint_id=new_endpoint.id,
                    change_type="added",
                    new_hash=current_hash,
                    diff_summary=f"New endpoint {method} {path} introduced in commit {commit_sha}"
                )
                self.db.add(history)
                changes_detected.append({
                    "action": "added",
                    "path": path,
                    "method": method,
                    "endpoint_id": new_endpoint.id
                })
            else:
                existing.last_seen = datetime.utcnow()
                history = ApiInventoryHistory(
                    endpoint_id=existing.id,
                    change_type="modified",
                    new_hash=current_hash,
                    diff_summary=f"Endpoint {method} {path} updated in deployment {commit_sha}"
                )
                self.db.add(history)
                changes_detected.append({
                    "action": "modified",
                    "path": path,
                    "method": method,
                    "endpoint_id": existing.id
                })

        self.db.commit()
        return {
            "deployment_id": deployment.id,
            "commit_sha": commit_sha,
            "changes_detected_count": len(changes_detected),
            "changes": changes_detected,
            "testing_trigger_recommended": len(changes_detected) > 0
        }

