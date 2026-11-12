from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.models.target import AuthorizedTarget
from app.models.staging import StagingHotel, StagingBooking
from app.core.rbac import ROLE_PERMISSIONS, UserRole

def seed_database(db: Session):
    # 1. Seed Roles
    for role_name, perms in ROLE_PERMISSIONS.items():
        existing_role = db.query(Role).filter(Role.name == role_name.value).first()
        if not existing_role:
            db.add(Role(
                name=role_name.value,
                description=f"System role for {role_name.value}",
                permissions=",".join(perms)
            ))
    db.commit()

    # 2. Seed Default Users
    users_data = [
        {
            "username": "admin",
            "email": "admin@securex.internal",
            "full_name": "Chief Security Architect",
            "password": "SecuReXAdmin2026!",
            "role": "admin",
            "agency_id": None
        },
        {
            "username": "sec_engineer",
            "email": "engineer@securex.internal",
            "full_name": "DevSecOps Lead",
            "password": "SecurityEng2026!",
            "role": "security_engineer",
            "agency_id": None
        },
        {
            "username": "agency1_user",
            "email": "agent@voyagecorp.example",
            "full_name": "Agency 101 Booking Officer",
            "password": "AgencyPass2026!",
            "role": "agency_admin",
            "agency_id": "agency_101"
        },
        {
            "username": "agency2_user",
            "email": "agent@competitortravel.example",
            "full_name": "Agency 202 Booking Officer",
            "password": "AgencyPass2026!",
            "role": "agency_admin",
            "agency_id": "agency_202"
        }
    ]

    for u in users_data:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            user = User(
                username=u["username"],
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                agency_id=u["agency_id"]
            )
            db.add(user)
    db.commit()

    # 3. Seed Authorized Staging Target
    target_name = "TBO Staging Travel API Cluster"
    existing_target = db.query(AuthorizedTarget).filter(AuthorizedTarget.name == target_name).first()
    if not existing_target:
        target = AuthorizedTarget(
            name=target_name,
            target_url="http://127.0.0.1:8000/api/v1/staging",
            environment="staging",
            is_approved=True,
            approval_notes="Approved for TBO VOYAGEHACK 4.0 dynamic security validation",
            approved_by="Security Architecture Board",
            rate_limit_rps=5.0,
            health_status="healthy"
        )
        db.add(target)
        db.commit()

    # 4. Seed Synthetic Staging Hotels
    hotels = [
        {"hotel_code": "HTL-DXB-01", "name": "Grand Palm Hotel Dubai", "city": "Dubai", "base_fare_per_night": 300.0, "available_rooms": 15},
        {"hotel_code": "HTL-LON-02", "name": "The Thames Royal London", "city": "London", "base_fare_per_night": 250.0, "available_rooms": 10},
        {"hotel_code": "HTL-DEL-03", "name": "The Oberoi Palace Delhi", "city": "Delhi", "base_fare_per_night": 180.0, "available_rooms": 25}
    ]

    for h in hotels:
        existing_h = db.query(StagingHotel).filter(StagingHotel.hotel_code == h["hotel_code"]).first()
        if not existing_h:
            db.add(StagingHotel(
                hotel_code=h["hotel_code"],
                name=h["name"],
                city=h["city"],
                base_fare_per_night=h["base_fare_per_night"],
                available_rooms=h["available_rooms"]
            ))
    db.commit()

    # 5. Seed Synthetic Staging Bookings (for IDOR demonstration)
    bkg = db.query(StagingBooking).filter(StagingBooking.booking_reference == "TBO-BKG-8891").first()
    if not bkg:
        db.add(StagingBooking(
            booking_reference="TBO-BKG-8891",
            agency_id="agency_101",
            customer_name="Alice Smith",
            customer_email="alice.smith@travelcorp.example",
            hotel_code="HTL-DXB-01",
            room_count=1,
            nights=2,
            calculated_fare=600.0,
            submitted_fare=600.0,
            status="confirmed"
        ))
        db.commit()

