from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from app.core.database import Base

class StagingHotel(Base):
    __tablename__ = "staging_hotels"

    id = Column(Integer, primary_key=True, index=True)
    hotel_code = Column(String(50), unique=True, index=True)
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), default="India")
    base_fare_per_night = Column(Float, nullable=False)
    available_rooms = Column(Integer, default=20)
    created_at = Column(DateTime, default=datetime.utcnow)

class StagingBooking(Base):
    __tablename__ = "staging_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(50), unique=True, index=True) # e.g. "TBO-BKG-8891"
    agency_id = Column(String(50), nullable=False, index=True) # e.g. "agency_101", "agency_202"
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(120), nullable=False)
    hotel_code = Column(String(50), nullable=False)
    room_count = Column(Integer, default=1)
    nights = Column(Integer, default=2)
    calculated_fare = Column(Float, nullable=False)
    submitted_fare = Column(Float, nullable=False) # In vulnerable mode, accepts client fare!
    status = Column(String(30), default="confirmed") # confirmed, cancelled, refunded
    created_at = Column(DateTime, default=datetime.utcnow)

class StagingPayment(Base):
    __tablename__ = "staging_payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(60), unique=True, index=True)
    booking_reference = Column(String(50), nullable=False)
    agency_id = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(30), default="successful") # successful, failed, reversed
    created_at = Column(DateTime, default=datetime.utcnow)

class StagingRefund(Base):
    __tablename__ = "staging_refunds"

    id = Column(Integer, primary_key=True, index=True)
    refund_reference = Column(String(60), unique=True, index=True)
    booking_reference = Column(String(50), nullable=False)
    agency_id = Column(String(50), nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_count = Column(Integer, default=1) # Detect duplicate refund abuse
    status = Column(String(30), default="processed") # processed, rejected, flag_duplicate
    created_at = Column(DateTime, default=datetime.utcnow)

