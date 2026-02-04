from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import time

# Configurar logger institucional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gahenax.crm")

app = FastAPI(title="GAHENAX - Gahenax CRM (Mock Office)")

# Metrics store
metrics = {
    "start_time": time.time(),
    "tickets_received": 0,
    "keys_issued": 0
}

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    if token != "TKN-3D9A855B": # Token institucional de prueba
        raise HTTPException(status_code=403, detail="Forbidden")
    return token

class SupportTicket(BaseModel):
    subject: str
    description: str
    priority: str = "medium"
    user_email: str
    metadata: Optional[Dict[str, Any]] = None

class LicenseRequest(BaseModel):
    guest_email: str
    room_slug: str
    plan: str
    duration_days: int

class GuestLog(BaseModel):
    timestamp: datetime
    guest_email: str
    action: str
    status: str

# In-memory mock data
active_keys = [
    {"guest": "test@gahenax.com", "room": "chechylegis", "plan": "pro", "expires": "2026-03-04"}
]

logs = [
    {"timestamp": datetime.now(), "guest": "test@gahenax.com", "action": "lobby_entry", "status": "success"}
]

@app.get("/", dependencies=[Depends(verify_token)])
async def office_dashboard():
    uptime = time.time() - metrics["start_time"]
    return {
        "office": "Gahenax CRM - Central Command",
        "status": "Operational",
        "active_keys_count": len(active_keys),
        "total_rooms": 1,
        "metrics": {
            "uptime_seconds": round(uptime, 2),
            "tickets_received": metrics["tickets_received"],
            "keys_issued": metrics["keys_issued"]
        },
        "recent_logs": logs[-5:]
    }

@app.get("/metrics", dependencies=[Depends(verify_token)])
async def get_metrics():
    return {
        "uptime": round(time.time() - metrics["start_time"], 2),
        "tickets": metrics["tickets_received"],
        "keys": metrics["keys_issued"]
    }

@app.get("/keys", dependencies=[Depends(verify_token)])
async def list_keys():
    return active_keys

@app.post("/issue-key", dependencies=[Depends(verify_token)])
async def issue_key(req: LicenseRequest):
    new_key = {
        "guest": req.guest_email,
        "room": req.room_slug,
        "plan": req.plan,
        "expires": (datetime.now().isoformat())
    }
    active_keys.append(new_key)
    metrics["keys_issued"] += 1
    logger.info(f"Key issued for {req.guest_email} - Room: {req.room_slug}")
    return {"status": "Key issued via Gahenax CRM", "key": new_key}

@app.post("/tickets", dependencies=[Depends(verify_token)])
async def receive_ticket(ticket: SupportTicket):
    metrics["tickets_received"] += 1
    ticket_id = f"TKT-{metrics['tickets_received']:04d}"
    logger.info(f"Ticket received: {ticket_id} - {ticket.subject}")
    return {
        "id": ticket_id,
        "status": "received",
        "message": "Incidencia registrada en Oficina Central"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
