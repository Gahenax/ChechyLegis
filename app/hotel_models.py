from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class HotelGuest(Base):
    __tablename__ = "hotel_guests"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String, default="customer") # viewer, customer, operator, admin
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    keys = relationship("HotelRoomKey", back_populates="guest")
    logs = relationship("HotelEntryLog", back_populates="guest")

class HotelRoom(Base):
    __tablename__ = "hotel_rooms"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    name = Column(String)
    floor = Column(Integer)
    type = Column(String)
    tagline = Column(String)
    description_short = Column(String)
    description_long = Column(String)
    tags = Column(JSON)
    requirements = Column(JSON)
    services = Column(JSON)
    access_policy = Column(JSON)
    status = Column(String, default="active")
    existing_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    keys = relationship("HotelRoomKey", back_populates="room")
    logs = relationship("HotelEntryLog", back_populates="room")

class HotelRoomKey(Base):
    __tablename__ = "hotel_room_keys"
    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("hotel_guests.id"))
    room_id = Column(Integer, ForeignKey("hotel_rooms.id"))
    plan = Column(String) # core, pro, max
    status = Column(String, default="active") # active, expired, revoked
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    revoked_at = Column(DateTime, nullable=True)

    guest = relationship("HotelGuest", back_populates="keys")
    room = relationship("HotelRoom", back_populates="keys")

class HotelEntryLog(Base):
    __tablename__ = "hotel_entry_logs"
    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("hotel_guests.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("hotel_rooms.id"))
    action = Column(String) # enter_attempt
    allow = Column(Boolean)
    reason = Column(String) # success, no_auth, no_key, expired, wrong_plan, revoked
    ip = Column(String)
    user_agent = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)

    guest = relationship("HotelGuest", back_populates="logs")
    room = relationship("HotelRoom", back_populates="logs")
