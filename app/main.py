from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import os

from .core.config import settings
from .routers import procesos, storage, ai_engine, support, jules
from .core.middleware import AuditMiddleware
from .core.audit import register_audit_listeners
from . import models, hotel_models, schemas
from .core.metrics import metrics
from .database import engine, get_db
from sqlalchemy.orm import Session
from .hotel_auth import require_auth, require_room_key, create_access_token, log_entry, HotelGuest, HotelRoom, HotelRoomKey
from passlib.context import CryptContext
import json

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Inicializar Base de Datos y Auditoría
models.Base.metadata.create_all(bind=engine)
hotel_models.Base.metadata.create_all(bind=engine)
register_audit_listeners()

app = FastAPI(
    title="GAHENAX - ChechyLegis API",
    version=settings.VERSION,
    description="Sistema experto de asistencia legal penal colombiana."
)

# Middlewares
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Seguridad
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Gahenax-Version"] = settings.VERSION
    return response

# Inclusión de Rutas Modulares
app.include_router(procesos.router)
app.include_router(storage.router)
app.include_router(ai_engine.router)
app.include_router(support.router)
app.include_router(jules.router)

# --- HOTEL API ROUTES ---

@app.get("/api/hotel/rooms")
async def list_rooms(db: Session = Depends(get_db)):
    rooms = db.query(HotelRoom).filter(HotelRoom.status == "active").all()
    return rooms

@app.get("/api/hotel/rooms/{room_slug}")
async def room_details(room_slug: str, user: HotelGuest = Depends(require_auth), db: Session = Depends(get_db)):
    room = db.query(HotelRoom).filter(HotelRoom.slug == room_slug).first()
    if not room:
        return JSONResponse(status_code=404, content={"detail": "Room not found"})
    
    # Check if user has key
    key = db.query(HotelRoomKey).filter(
        HotelRoomKey.guest_id == user.id,
        HotelRoomKey.room_id == room.id,
        HotelRoomKey.status == "active",
        HotelRoomKey.expires_at > datetime.utcnow()
    ).first()
    
    return {
        "room": room,
        "door_state": "unlocked" if key else "locked",
        "key_plan": key.plan if key else None
    }

@app.get("/api/admin/metrics")
async def get_metrics(user: dict = Depends(require_auth)):
    # Simulación de verificación de rol Admin
    # En un sistema real usaríamos require_auth con scope admin
    return metrics.get_report()

@app.post("/api/reception/checkin")
async def checkin(data: schemas.CheckinRequest, db: Session = Depends(get_db)):
    email = data.email
    password = data.password
    
    user = db.query(HotelGuest).filter(HotelGuest.email == email).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
    
    access_token = create_access_token(data={"sub": user.email})
    response = JSONResponse(content={
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"email": user.email, "name": user.name, "role": user.role}
    })
    response.set_cookie(key="gahenax_session", value=access_token, httponly=True)
    return response

@app.get("/api/reception/me")
async def get_me(user: HotelGuest = Depends(require_auth)):
    return user

@app.get("/api/reception/keys/mine")
async def my_keys(user: HotelGuest = Depends(require_auth), db: Session = Depends(get_db)):
    keys = db.query(HotelRoomKey).filter(HotelRoomKey.guest_id == user.id, HotelRoomKey.status == "active").all()
    return keys

@app.post("/api/hotel/rooms/{room_slug}/enter")
async def enter_room(room_slug: str, request: Request, user: HotelGuest = Depends(require_auth), db: Session = Depends(get_db)):
    room = db.query(HotelRoom).filter(HotelRoom.slug == room_slug).first()
    if not room:
        return JSONResponse(status_code=404, content={"detail": "Room not found"})
        
    try:
        await require_room_key(room_slug, user, db)
        log_entry(db, user.id, room.id, "enter_attempt", True, "success", request.client.host, request.headers.get("user-agent"))
        return {"allowed": True, "url": room.existing_url}
    except HTTPException as e:
        log_entry(db, user.id, room.id, "enter_attempt", False, str(e.detail), request.client.host, request.headers.get("user-agent"))
        return {"allowed": False, "reason": e.detail}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Internal error during entry: {str(e)}"})

# Admin FrontDesk
@app.post("/api/frontdesk/keys/issue")
async def issue_key(data: dict, user: HotelGuest = Depends(require_auth), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    guest = db.query(HotelGuest).filter(HotelGuest.email == data["guest_email"]).first()
    room = db.query(HotelRoom).filter(HotelRoom.slug == data["room_slug"]).first()
    
    if not guest or not room:
        raise HTTPException(status_code=404, detail="Guest or Room not found")
        
    new_key = HotelRoomKey(
        guest_id=guest.id,
        room_id=room.id,
        plan=data["plan"],
        expires_at=datetime.utcnow() + timedelta(days=data.get("expires_days", 30))
    )
    db.add(new_key)
    db.commit()
    return {"message": "Key issued"}

# Montar Archivos Estáticos
# Asegurarse de que la ruta absoluta sea correcta
base_path = os.path.dirname(os.path.dirname(__file__))
static_path = os.path.join(base_path, "static")
if os.path.exists(static_path):
    # Carpeta Downloads - Ahora apuntando a static/downloads para el Hub
    downloads_path = os.path.join(static_path, "downloads")
    if os.path.exists(downloads_path):
        app.mount("/downloads", StaticFiles(directory=downloads_path), name="downloads")
    
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# hotel_lobby_path = os.path.join(base_path, "hotel_lobby")
# if os.path.exists(hotel_lobby_path):
#    app.mount("/hotel_lobby", StaticFiles(directory=hotel_lobby_path), name="hotel_lobby")

# Hub now served at /lobby and /

@app.get("/")
@app.get("/lobby")
@app.get("/hotel_lobby/hotel.html")
@app.get("/gahenax_hub.html")
async def serve_lobby():
    lobby_file = os.path.join(os.getcwd(), "gahenax_hub.html")
    if os.path.exists(lobby_file):
        return FileResponse(lobby_file)
    return {"message": "Gahenax Hotel Lobby Online. hub file not found."}

@app.get("/chechylegis")
async def serve_chechylegis(request: Request, user: HotelGuest = Depends(require_auth), db: Session = Depends(get_db)):
    # Check for room key before serving the index
    try:
        await require_room_key("chechylegis", user, db)
    except HTTPException:
        # If no key, redirect to Hub/Lobby with info
        return JSONResponse(status_code=403, content={"detail": "No valid key for ChechyLegis. Please visit the Lobby.", "redirect": "/gahenax_hub.html"})
        
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "ChechyLegis Room Online. Static files not found."}

@app.get("/api/health")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "mode": settings.LICENSE_MODE,
        "engine": "Gahenax-1.1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
