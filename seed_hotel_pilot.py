import json
import os
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import engine, SessionLocal
from app.hotel_models import Base, HotelGuest, HotelRoom, HotelRoomKey
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def seed_hotel():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Read Manifest
        manifest_path = "hotel_manifest_pilot.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        # 2. Seed Rooms
        for room_data in manifest["rooms_seed"]:
            existing_room = db.query(HotelRoom).filter(HotelRoom.slug == room_data["slug"]).first()
            if not existing_room:
                room = HotelRoom(
                    slug=room_data["slug"],
                    name=room_data["name"],
                    floor=room_data["floor"],
                    type=room_data["type"],
                    tagline=room_data["tagline"],
                    description_short=room_data["description_short"],
                    description_long=room_data["description_long"],
                    tags=room_data["tags"],
                    requirements=room_data["requirements"],
                    services=room_data["services"],
                    access_policy=room_data["access_policy"],
                    status=room_data["status"],
                    existing_url=room_data.get("existing_url", "/static/index.html")
                )
                db.add(room)
                print(f"Added room: {room.name}")
            else:
                print(f"Room {room_data['name']} already exists.")
        
        # 3. Seed Test Guest
        test_email = "test@gahenax.com"
        existing_guest = db.query(HotelGuest).filter(HotelGuest.email == test_email).first()
        if not existing_guest:
            guest = HotelGuest(
                email=test_email,
                name="Test Guest",
                role="customer",
                password_hash=pwd_context.hash("test123")
            )
            db.add(guest)
            db.flush()
            print(f"Added test guest: {test_email}")
            
            # 4. Seed Test Key for ChechyLegis (Room 101)
            chechy_room = db.query(HotelRoom).filter(HotelRoom.slug == "chechylegis").first()
            if chechy_room:
                key = HotelRoomKey(
                    guest_id=guest.id,
                    room_id=chechy_room.id,
                    plan="pro",
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                db.add(key)
                print(f"Added Pro Key for {test_email} to {chechy_room.name}")
        else:
            print(f"Guest {test_email} already exists.")

        # 5. Seed Admin
        admin_email = "admin@gahenax.com"
        existing_admin = db.query(HotelGuest).filter(HotelGuest.email == admin_email).first()
        if not existing_admin:
            admin = HotelGuest(
                email=admin_email,
                name="Hotel Admin",
                role="admin",
                password_hash=pwd_context.hash("admin123")
            )
            db.add(admin)
            print(f"Added admin: {admin_email}")

        db.commit()
        print("Success: Database seeded.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_hotel()
