from typing import Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.staging import StagingBooking, StagingHotel
from app.api.v1.staging_app import (
    create_booking,
    request_refund,
    BookingRequest,
    RefundRequest
)

class BusinessLogicTestingAgent:
    """
    AGENT 5.2: Business Logic Agent
    Specializes in:
    - Fare and price manipulation
    - Refund workflow abuse
    - Coupon / discount tampering
    - Invalid booking quantities
    """
    def __init__(self, db: Session):
        self.db = db

    def test_fare_manipulation(self, endpoint_id: int) -> Dict[str, Any]:
        # Target: Submit booking with deliberate $1.00 price while base fare is $300.00/night
        request_obj = BookingRequest(
            hotel_code="HTL-DXB-01",
            customer_name="Bob Test",
            customer_email="bob.test@agency101.example",
            room_count=1,
            nights=2,
            submitted_fare=1.00 # Arbitrary low fare
        )

        request_dump = (
            "POST /api/v1/staging/bookings HTTP/1.1\n"
            "Host: staging-api.tbo.internal\n"
            "X-Agency-Id: agency_101\n"
            "Content-Type: application/json\n\n"
            "{\n"
            "  \"hotel_code\": \"HTL-DXB-01\",\n"
            "  \"room_count\": 1,\n"
            "  \"nights\": 2,\n"
            "  \"submitted_fare\": 1.00\n"
            "}"
        )

        try:
            res = create_booking(booking_in=request_obj, x_agency_id="agency_101", db=self.db)
            if res.get("tampering_accepted") or res.get("charged_fare") == 1.00:
                response_dump = (
                    "HTTP/1.1 200 OK\n"
                    "Content-Type: application/json\n\n"
                    f"{{\n"
                    f"  \"booking_reference\": \"{res['booking_reference']}\",\n"
                    f"  \"server_calculated_fare\": {res['server_calculated_fare']},\n"
                    f"  \"charged_fare\": {res['charged_fare']},\n"
                    f"  \"tampering_accepted\": true\n"
                    f"}}"
                )
                return {
                    "vulnerable": True,
                    "title": "Client-Side Fare Manipulation in Booking API",
                    "category": "business_logic",
                    "severity": "critical",
                    "cvss_score": 9.3,
                    "description": f"The booking endpoint accepted client-submitted price ($1.00) instead of calculating and enforcing server-side tariff (${res['server_calculated_fare']}).",
                    "business_impact": "Direct financial revenue leakage and inventory arbitrage exploit. Malicious agency accounts can book luxury accommodations at near-zero rates.",
                    "remediation_guidance": "Calculate booking total strictly on the server based on contracted hotel rates. Never trust price values transmitted from the client body.",
                    "request_dump": request_dump,
                    "response_dump": response_dump,
                    "endpoint_id": endpoint_id
                }
            return {"vulnerable": False, "title": "Fare Check Passed"}
        except HTTPException as exc:
            if exc.status_code == 400:
                return {
                    "vulnerable": False,
                    "title": "Fare Manipulation Prevented",
                    "reason": "Server rejected client-supplied fare and returned HTTP 400 Bad Request.",
                    "request_dump": request_dump,
                    "response_dump": f"HTTP/1.1 400 Bad Request\n\n{exc.detail}"
                }
            return {"vulnerable": False, "title": f"HTTP {exc.status_code}", "reason": str(exc.detail)}

    def test_duplicate_refund(self, endpoint_id: int) -> Dict[str, Any]:
        # Target: Execute two sequential refunds against a confirmed booking
        booking = self.db.query(StagingBooking).first()
        if not booking:
            booking = StagingBooking(
                booking_reference="TBO-BKG-REF1",
                agency_id="agency_101",
                customer_name="Carol Miller",
                customer_email="carol@example.com",
                hotel_code="HTL-DXB-01",
                room_count=1,
                nights=1,
                calculated_fare=350.0,
                submitted_fare=350.0,
                status="confirmed"
            )
            self.db.add(booking)
            self.db.commit()

        # Attempt 1
        req1 = RefundRequest(booking_reference=booking.booking_reference, refund_amount=350.0)
        create_res1 = request_refund(req1, x_agency_id="agency_101", db=self.db)

        # Attempt 2 (Duplicate check)
        request_dump = (
            f"POST /api/v1/staging/refunds HTTP/1.1\n"
            f"Host: staging-api.tbo.internal\n"
            f"X-Agency-Id: agency_101\n"
            f"Content-Type: application/json\n\n"
            f"{{\n"
            f"  \"booking_reference\": \"{booking.booking_reference}\",\n"
            f"  \"refund_amount\": 350.0\n"
            f"}}"
        )

        try:
            res2 = request_refund(req1, x_agency_id="agency_101", db=self.db)
            response_dump = (
                f"HTTP/1.1 200 OK\n"
                f"Content-Type: application/json\n\n"
                f"{{\n"
                f"  \"refund_reference\": \"{res2['refund_reference']}\",\n"
                f"  \"refund_attempt_number\": {res2['refund_attempt_number']},\n"
                f"  \"status\": \"{res2['status']}\"\n"
                f"}}"
            )
            return {
                "vulnerable": True,
                "title": "Duplicate Refund Workflow Abuse",
                "category": "business_logic",
                "severity": "high",
                "cvss_score": 8.5,
                "description": f"The refund endpoint permitted multiple full refund credits ({res2['refund_attempt_number']} times) against a single booking reference '{booking.booking_reference}'.",
                "business_impact": "Financial loss through duplicate settlement payouts and balance inflation.",
                "remediation_guidance": "Implement idempotency locks and verify that cumulative refunded amount does not exceed the settled payment amount.",
                "request_dump": request_dump,
                "response_dump": response_dump,
                "endpoint_id": endpoint_id
            }
        except HTTPException as exc:
            if exc.status_code == 409:
                return {
                    "vulnerable": False,
                    "title": "Duplicate Refund Prevented",
                    "reason": "Server rejected second refund with HTTP 409 Conflict.",
                    "request_dump": request_dump,
                    "response_dump": f"HTTP/1.1 409 Conflict\n\n{exc.detail}"
                }
            return {"vulnerable": False, "title": f"HTTP {exc.status_code}", "reason": str(exc.detail)}
