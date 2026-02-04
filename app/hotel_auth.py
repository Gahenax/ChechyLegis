from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .database import get_db
from .hotel_models import HotelGuest, HotelRoom, HotelRoomKey, HotelEntryLog

from .core.config import settings

# Secret comes from settings (loaded from .env)
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/reception/checkin", auto_error=False)

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Try token first, then session cookie
    if not token:
        token = request.cookies.get("gahenax_session")
    
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
        
    user = db.query(HotelGuest).filter(HotelGuest.email == email).first()
    return user

async def require_auth(user: HotelGuest = Depends(get_current_user)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please check-in at the Lobby.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def require_room_key(room_slug: str, user: HotelGuest = Depends(require_auth), db: Session = Depends(get_db)):
    room = db.query(HotelRoom).filter(HotelRoom.slug == room_slug).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    key = db.query(HotelRoomKey).filter(
        HotelRoomKey.guest_id == user.id,
        HotelRoomKey.room_id == room.id,
        HotelRoomKey.status == "active",
        HotelRoomKey.expires_at > datetime.utcnow()
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No valid key for {room.name}. Access denied."
        )
    
    # Check plan in access_policy
    if key.plan not in room.access_policy.get("allowed_plans", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your {key.plan} key does not grant access to this room."
        )
        
    return key

def log_entry(db: Session, guest_id: int, room_id: int, action: str, allow: bool, reason: str, ip: str, ua: str):
    log = HotelEntryLog(
        guest_id=guest_id,
        room_id=room_id,
        action=action,
        allow=allow,
        reason=reason,
        ip=ip,
        user_agent=ua
    )
    db.add(log)
    db.commit()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
