from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.api_endpoint import ApiEndpoint, ApiParameter, ApiInventoryHistory
from app.models.target import AuthorizedTarget

class ReconDiscoveryAgent:
    """
    AGENT 2: Reconnaissance & API Discovery Agent
    Discovers API endpoints from authorized staging application, analyzes HTTP methods,
    identifies parameters and authentication requirements, and builds the API knowledge graph.
    """
    def __init__(self, db: Session):
        self.db = db

    def discover_staging_apis(self, target_id: int) -> Dict[str, Any]:
        target = self.db.query(AuthorizedTarget).filter(AuthorizedTarget.id == target_id).first()
        if not target:
            raise ValueError(f"Target ID {target_id} not found")

        # In production, this agent crawls OpenAPI schemas / docs or analyzes staging traffic.
        # For SentinelAI, we discover all defined staging travel endpoints:
        known_discovery_catalog = [
            {
                "path": "/api/v1/staging/hotels/search",
                "method": "GET",
                "summary": "Search Hotels by destination",
                "description": "Public or partner travel search endpoint",
                "auth_required": False,
                "required_roles": "public,agency",
                "classification": "active",
                "risk_score": 2.0,
                "parameters": [
                    {"name": "city", "in_location": "query", "data_type": "string", "is_required": False, "example_value": "Dubai"}
                ]
            },
            {
                "path": "/api/v1/staging/bookings",
                "method": "POST",
                "summary": "Create Hotel Booking",
                "description": "Creates a hotel reservation for travel agency customers",
                "auth_required": True,
                "required_roles": "agency_admin",
                "classification": "active",
                "risk_score": 8.5,
                "parameters": [
                    {"name": "hotel_code", "in_location": "body", "data_type": "string", "is_required": True, "example_value": "HTL-DXB-01"},
                    {"name": "customer_name", "in_location": "body", "data_type": "string", "is_required": True, "example_value": "John Doe"},
                    {"name": "submitted_fare", "in_location": "body", "data_type": "float", "is_required": True, "example_value": "1200.00"},
                    {"name": "nights", "in_location": "body", "data_type": "integer", "is_required": True, "example_value": "2"},
                    {"name": "x-agency-id", "in_location": "header", "data_type": "string", "is_required": True, "example_value": "agency_101"}
                ]
            },
            {
                "path": "/api/v1/staging/bookings/{booking_ref}",
                "method": "GET",
                "summary": "Retrieve Booking Details",
                "description": "Fetches booking itinerary and customer details by reference",
                "auth_required": True,
                "required_roles": "agency_admin",
                "classification": "active",
                "risk_score": 9.0,
                "parameters": [
                    {"name": "booking_ref", "in_location": "path", "data_type": "string", "is_required": True, "example_value": "TBO-BKG-8891"},
                    {"name": "x-agency-id", "in_location": "header", "data_type": "string", "is_required": True, "example_value": "agency_101"}
                ]
            },
            {
                "path": "/api/v1/staging/payments",
                "method": "POST",
                "summary": "Process Booking Settlement",
                "description": "Settles payment for a confirmed booking reference",
                "auth_required": True,
                "required_roles": "agency_admin",
                "classification": "active",
                "risk_score": 8.0,
                "parameters": [
                    {"name": "booking_reference", "in_location": "body", "data_type": "string", "is_required": True, "example_value": "TBO-BKG-8891"},
                    {"name": "amount", "in_location": "body", "data_type": "float", "is_required": True, "example_value": "1200.00"}
                ]
            },
            {
                "path": "/api/v1/staging/refunds",
                "method": "POST",
                "summary": "Initiate Booking Cancellation Refund",
                "description": "Processes refund credit to agency account",
                "auth_required": True,
                "required_roles": "agency_admin",
                "classification": "active",
                "risk_score": 9.2,
                "parameters": [
                    {"name": "booking_reference", "in_location": "body", "data_type": "string", "is_required": True, "example_value": "TBO-BKG-8891"},
                    {"name": "refund_amount", "in_location": "body", "data_type": "float", "is_required": True, "example_value": "1200.00"}
                ]
            },
            {
                "path": "/api/v1/staging/v1/legacy/export-customer-pii",
                "method": "GET",
                "summary": "Legacy Customer Export",
                "description": "Deprecated unauthenticated endpoint remaining active in staging environment",
                "auth_required": False,
                "required_roles": "none",
                "classification": "zombie", # Marked as zombie
                "risk_score": 9.5,
                "parameters": [
                    {"name": "secret_key", "in_location": "query", "data_type": "string", "is_required": False, "example_value": "test"}
                ]
            },
            {
                "path": "/api/v1/staging/internal/supplier-pricing-sync",
                "method": "POST",
                "summary": "Internal Supplier Margin Sync",
                "description": "Undocumented supplier synchronization endpoint found in network traffic",
                "auth_required": False,
                "required_roles": "internal",
                "classification": "shadow", # Shadow API
                "risk_score": 7.8,
                "parameters": []
            }
        ]

        discovered_count = 0
        updated_count = 0

        for item in known_discovery_catalog:
            ep = self.db.query(ApiEndpoint).filter(
                ApiEndpoint.target_id == target_id,
                ApiEndpoint.path == item["path"],
                ApiEndpoint.method == item["method"]
            ).first()

            if not ep:
                ep = ApiEndpoint(
                    target_id=target_id,
                    path=item["path"],
                    method=item["method"],
                    summary=item["summary"],
                    description=item["description"],
                    auth_required=item["auth_required"],
                    required_roles=item["required_roles"],
                    classification=item["classification"],
                    risk_score=item["risk_score"],
                    recommendation="Decommission outdated endpoint immediately" if item["classification"] == "zombie" else ("Document API in official Swagger specification" if item["classification"] == "shadow" else None)
                )
                self.db.add(ep)
                self.db.commit()
                self.db.refresh(ep)

                # Add parameters
                for param in item.get("parameters", []):
                    p = ApiParameter(
                        endpoint_id=ep.id,
                        name=param["name"],
                        in_location=param["in_location"],
                        data_type=param["data_type"],
                        is_required=param["is_required"],
                        example_value=param.get("example_value")
                    )
                    self.db.add(p)

                hist = ApiInventoryHistory(
                    endpoint_id=ep.id,
                    change_type="discovered",
                    diff_summary=f"Discovered {item['method']} {item['path']} during automated recon scan"
                )
                self.db.add(hist)
                discovered_count += 1
            else:
                ep.last_seen = datetime.utcnow()
                updated_count += 1

        self.db.commit()

        return {
            "target_id": target_id,
            "total_endpoints_discovered": discovered_count + updated_count,
            "new_endpoints_added": discovered_count,
            "existing_endpoints_refreshed": updated_count,
            "timestamp": datetime.utcnow().isoformat()
        }

