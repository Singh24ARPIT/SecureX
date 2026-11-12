from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.models.staging import StagingHotel, StagingBooking, StagingPayment, StagingRefund

router = APIRouter(prefix="/staging", tags=["Staging Application (Synthetic Travel App)"])

# State toggle for demonstrating fixes and retesting:
# When vulnerable=True, the endpoints exhibit the business logic, IDOR, and refund abuse vulnerabilities.
# When vulnerable=False (patched), proper authorization and server-side checks are enforced.
STAGING_SECURITY_CONFIG = {
    "idor_vulnerable": True,
    "fare_tampering_vulnerable": True,
    "duplicate_refund_vulnerable": True,
    "unauthorized_admin_vulnerable": True
}

class HotelSearchResponse(BaseModel):
    hotel_code: str
    name: str
    city: str
    base_fare_per_night: float
    available_rooms: int

class BookingRequest(BaseModel):
    hotel_code: str
    customer_name: str
    customer_email: str
    room_count: int = 1
    nights: int = 2
    submitted_fare: float # Price sent by client

class PaymentRequest(BaseModel):
    booking_reference: str
    amount: float
    currency: str = "USD"

class RefundRequest(BaseModel):
    booking_reference: str
    refund_amount: float

class PatchToggleRequest(BaseModel):
    idor_vulnerable: Optional[bool] = None
    fare_tampering_vulnerable: Optional[bool] = None
    duplicate_refund_vulnerable: Optional[bool] = None
    unauthorized_admin_vulnerable: Optional[bool] = None

@router.get("/config")
def get_security_config():
    return {
        "status": "Staging Travel API Operational",
        "vulnerability_flags": STAGING_SECURITY_CONFIG,
        "mode": "synthetic-testbed"
    }

@router.post("/security/toggle-patch")
def toggle_security_patch(payload: PatchToggleRequest):
    if payload.idor_vulnerable is not None:
        STAGING_SECURITY_CONFIG["idor_vulnerable"] = payload.idor_vulnerable
    if payload.fare_tampering_vulnerable is not None:
        STAGING_SECURITY_CONFIG["fare_tampering_vulnerable"] = payload.fare_tampering_vulnerable
    if payload.duplicate_refund_vulnerable is not None:
        STAGING_SECURITY_CONFIG["duplicate_refund_vulnerable"] = payload.duplicate_refund_vulnerable
    if payload.unauthorized_admin_vulnerable is not None:
        STAGING_SECURITY_CONFIG["unauthorized_admin_vulnerable"] = payload.unauthorized_admin_vulnerable
    return {
        "message": "Staging security configuration updated",
        "current_state": STAGING_SECURITY_CONFIG
    }

@router.get("/hotels/search", response_model=List[HotelSearchResponse])
def search_hotels(
    city: Optional[str] = Query(None, description="City to filter hotels"),
    db: Session = Depends(get_db)
):
    query = db.query(StagingHotel)
    if city:
        query = query.filter(StagingHotel.city.ilike(f"%{city}%"))
    hotels = query.all()
    return [
        HotelSearchResponse(
            hotel_code=h.hotel_code,
            name=h.name,
            city=h.city,
            base_fare_per_night=h.base_fare_per_night,
            available_rooms=h.available_rooms
        )
        for h in hotels
    ]

@router.post("/bookings")
def create_booking(
    booking_in: BookingRequest,
    x_agency_id: str = Header("agency_101", description="Header identifying requesting travel agency"),
    db: Session = Depends(get_db)
):
    hotel = db.query(StagingHotel).filter(StagingHotel.hotel_code == booking_in.hotel_code).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    server_calculated_fare = hotel.base_fare_per_night * booking_in.nights * booking_in.room_count
    
    # BUSINESS LOGIC CHECK:
    # If patched: server must strictly validate that submitted_fare matches server_calculated_fare
    if not STAGING_SECURITY_CONFIG["fare_tampering_vulnerable"]:
        if abs(booking_in.submitted_fare - server_calculated_fare) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Price discrepancy detected. Expected {server_calculated_fare}, received {booking_in.submitted_fare}"
            )
        if booking_in.room_count <= 0 or booking_in.nights <= 0:
            raise HTTPException(status_code=400, detail="Invalid booking quantities")
    
    ref = f"TBO-BKG-{uuid.uuid4().hex[:6].upper()}"
    new_booking = StagingBooking(
        booking_reference=ref,
        agency_id=x_agency_id,
        customer_name=booking_in.customer_name,
        customer_email=booking_in.customer_email,
        hotel_code=booking_in.hotel_code,
        room_count=booking_in.room_count,
        nights=booking_in.nights,
        calculated_fare=server_calculated_fare,
        submitted_fare=booking_in.submitted_fare,
        status="confirmed"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {
        "booking_reference": new_booking.booking_reference,
        "agency_id": new_booking.agency_id,
        "status": new_booking.status,
        "server_calculated_fare": new_booking.calculated_fare,
        "charged_fare": new_booking.submitted_fare,
        "tampering_accepted": (new_booking.submitted_fare < new_booking.calculated_fare)
    }

@router.get("/bookings/{booking_ref}")
def get_booking_details(
    booking_ref: str,
    x_agency_id: str = Header("agency_101", description="Agency token/header"),
    db: Session = Depends(get_db)
):
    booking = db.query(StagingBooking).filter(StagingBooking.booking_reference == booking_ref).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking reference not found")
    
    # ACCESS CONTROL CHECK (IDOR):
    # If patched: agency must only view bookings belonging to their own agency_id
    if not STAGING_SECURITY_CONFIG["idor_vulnerable"]:
        if booking.agency_id != x_agency_id:
            raise HTTPException(
                status_code=403,
                detail=f"Unauthorized: Agency '{x_agency_id}' cannot access records belonging to '{booking.agency_id}'"
            )
    
    return {
        "booking_reference": booking.booking_reference,
        "agency_id": booking.agency_id,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "hotel_code": booking.hotel_code,
        "room_count": booking.room_count,
        "nights": booking.nights,
        "fare": booking.submitted_fare,
        "status": booking.status,
        "created_at": booking.created_at
    }

@router.post("/payments")
def process_payment(
    payment_in: PaymentRequest,
    x_agency_id: str = Header("agency_101"),
    db: Session = Depends(get_db)
):
    booking = db.query(StagingBooking).filter(StagingBooking.booking_reference == payment_in.booking_reference).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    payment = StagingPayment(
        transaction_id=tx_id,
        booking_reference=payment_in.booking_reference,
        agency_id=x_agency_id,
        amount=payment_in.amount,
        currency=payment_in.currency,
        status="successful"
    )
    db.add(payment)
    db.commit()
    return {
        "transaction_id": tx_id,
        "booking_reference": payment_in.booking_reference,
        "amount": payment_in.amount,
        "status": "payment_settled"
    }

@router.post("/refunds")
def request_refund(
    refund_in: RefundRequest,
    x_agency_id: str = Header("agency_101"),
    db: Session = Depends(get_db)
):
    booking = db.query(StagingBooking).filter(StagingBooking.booking_reference == refund_in.booking_reference).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    existing_refunds = db.query(StagingRefund).filter(
        StagingRefund.booking_reference == refund_in.booking_reference
    ).count()
    
    # BUSINESS LOGIC (DUPLICATE REFUND):
    if not STAGING_SECURITY_CONFIG["duplicate_refund_vulnerable"]:
        if existing_refunds > 0:
            raise HTTPException(
                status_code=409,
                detail="Refund already processed for this booking. Duplicate refund rejected."
            )
    
    ref_id = f"REF-{uuid.uuid4().hex[:6].upper()}"
    refund = StagingRefund(
        refund_reference=ref_id,
        booking_reference=refund_in.booking_reference,
        agency_id=x_agency_id,
        refund_amount=refund_in.refund_amount,
        refund_count=existing_refunds + 1,
        status="processed"
    )
    db.add(refund)
    db.commit()
    
    return {
        "refund_reference": ref_id,
        "booking_reference": refund_in.booking_reference,
        "refund_amount": refund_in.refund_amount,
        "refund_attempt_number": existing_refunds + 1,
        "status": "refund_approved"
    }

@router.get("/v1/legacy/export-customer-pii")
def legacy_export_pii(
    secret_key: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    ZOMBIE / SHADOW API EXAMPLE:
    An outdated, unauthenticated legacy endpoint from an old deployment that leaks customer records!
    """
    bookings = db.query(StagingBooking).limit(10).all()
    return {
        "warning": "Legacy endpoint active",
        "count": len(bookings),
        "data": [
            {
                "reference": b.booking_reference,
                "agency": b.agency_id,
                "name": b.customer_name,
                "email": b.customer_email
            }
            for b in bookings
        ]
    }
