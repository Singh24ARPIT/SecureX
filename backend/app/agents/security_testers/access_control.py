from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.staging import StagingBooking
from app.api.v1.staging_app import get_booking_details

class AccessControlTestingAgent:
    """
    AGENT 5.1: Access Control Agent
    Specializes in:
    - Insecure Direct Object References (IDOR)
    - Cross-agency multi-tenant access violations
    - Privilege escalation
    """
    def __init__(self, db: Session):
        self.db = db

    def test_cross_agency_idor(self, endpoint_id: int) -> Dict[str, Any]:
        # Target: Fetch a booking created by Agency 101, but query it using Agency 202 credentials
        booking = self.db.query(StagingBooking).filter(StagingBooking.agency_id == "agency_101").first()
        if not booking:
            # Create a sample synthetic booking if none exists
            booking = StagingBooking(
                booking_reference="TBO-BKG-9921",
                agency_id="agency_101",
                customer_name="Alice Smith",
                customer_email="alice.smith@travelcorp.example",
                hotel_code="HTL-DXB-01",
                room_count=1,
                nights=2,
                calculated_fare=500.0,
                submitted_fare=500.0,
                status="confirmed"
            )
            self.db.add(booking)
            self.db.commit()
            self.db.refresh(booking)

        # Execute test: call staging booking endpoint with x_agency_id="agency_202"
        from fastapi import HTTPException
        request_dump = f"GET /api/v1/staging/bookings/{booking.booking_reference} HTTP/1.1\nHost: staging-api.tbo.internal\nX-Agency-Id: agency_202\nAuthorization: Bearer test_token_agency_202"
        
        try:
            res = get_booking_details(
                booking_ref=booking.booking_reference,
                x_agency_id="agency_202",
                db=self.db
            )
            # If function returned 200 without raising 403 Forbidden:
            response_dump = f"HTTP/1.1 200 OK\nContent-Type: application/json\n\n{{\n  \"booking_reference\": \"{res['booking_reference']}\",\n  \"agency_id\": \"{res['agency_id']}\",\n  \"customer_name\": \"{res['customer_name']}\"\n}}"
            
            return {
                "vulnerable": True,
                "title": "Cross-Agency BOLA / IDOR in Booking API",
                "category": "access_control",
                "severity": "critical",
                "cvss_score": 9.1,
                "description": f"Agency 'agency_202' was able to view booking '{booking.booking_reference}' belonging to 'agency_101'. Missing tenant isolation check allows unauthorized cross-agency data access.",
                "business_impact": "Severe commercial confidentiality breach. Competitor travel agencies can view customer itineraries, passenger names, and pricing.",
                "remediation_guidance": "Enforce object-level authorization by validating that `booking.agency_id == current_user.agency_id` before returning booking details.",
                "request_dump": request_dump,
                "response_dump": response_dump,
                "endpoint_id": endpoint_id
            }
        except HTTPException as exc:
            if exc.status_code == 403:
                # Patched secure behavior
                return {
                    "vulnerable": False,
                    "title": "Cross-Agency IDOR Check Passed",
                    "reason": "Server returned 403 Forbidden when agency_202 attempted to view agency_101's booking.",
                    "request_dump": request_dump,
                    "response_dump": f"HTTP/1.1 403 Forbidden\n\n{exc.detail}"
                }
            return {
                "vulnerable": False,
                "title": f"HTTP {exc.status_code}",
                "reason": str(exc.detail)
            }

