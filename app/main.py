from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from .storage_service import StorageService
from . import storage_utils, models, schemas, database
from .database import engine, get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse
from fastapi import UploadFile, File as FastAPIFile

load_dotenv()

# --- CONFIGURACIÓN LEGISCHECHY ---
LICENSE_MODE = os.getenv("LICENSE_MODE", "FREE")  # FREE | PRO
MAX_CASES_FREE = 3
MAX_DOCS_FREE = 10

FILES_ROOT = os.getenv("FILES_ROOT", os.path.join(os.getcwd(), "storage"))
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
security = HTTPBearer()

os.makedirs(FILES_ROOT, exist_ok=True)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LEGISCHECHY API (Colombian Criminal Law Assistant)")

# Dependency for Storage
def get_storage(db: Session = Depends(get_db)):
    return StorageService(db, FILES_ROOT)

# --- AUTH STUB & RBAC ---
def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    # Simulación de JWT Bearer - En producción validar JWT real
    token = auth.credentials
    if token == "admin-token":
        return {"id": "admin_user", "role": "admin", "name": "Administrador"}
    elif token == "operator-token":
        return {"id": "op_user", "role": "operator", "name": "Operador Legal"}
    return {"id": "viewer_user", "role": "viewer", "name": "Consultor"}

def rbac_required(allowed_roles: List[str]):
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            return JSONResponse(
                status_code=403,
                content={"error": {"code": "FORBIDDEN", "message": "Rol insuficiente"}}
            )
        return user
    return checker

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# MIDDLEWARE DE SEGURIDAD (SEC-01, SEC-06)
# ---------------------------------------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # HSTS (Strict-Transport-Security) - 1 año
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Evitar inferencia de tipos MIME
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Protección básica XSS (aunque moderna browsers lo ignoran, es compliance)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# ---------------------------------------------------------
# HEALTHCHECK (OBS-02)
# ---------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "service": "ChechyLegis"}

# Simple Mock Auth Dependency
def get_current_user_role(request: Request):
    role = request.headers.get("X-User-Role", "viewer")
    user = request.headers.get("X-User-Name", "anonymous")
    if role not in ["viewer", "operator", "admin"]:
        role = "viewer"
    return {"name": user, "role": role}

def role_required(allowed_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user_role)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operación no permitida para su rol"
            )
        return current_user
    return role_checker

@app.post("/api/procesos", response_model=schemas.ProcesoSchema)
def create_proceso(
    proceso: schemas.ProcesoCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(role_required(["operator", "admin"]))
):
    # Enforce FREE limits
    if LICENSE_MODE == "FREE":
        current_count = db.query(models.Proceso).filter(models.Proceso.deleted_at == None).count()
        if current_count >= MAX_CASES_FREE:
            raise HTTPException(
                status_code=403, 
                detail=f"Límite de la versión FREE alcanzado ({MAX_CASES_FREE} casos). Por favor elimine uno para continuar."
            )

    existing = crud.get_proceso_by_numero(db, proceso.numero_proceso)
    if existing:
        raise HTTPException(status_code=400, detail="El número de proceso ya existe")
    new_proceso = crud.create_proceso(db=db, proceso=proceso, usuario=user["name"])
    
    return new_proceso

@app.get("/api/procesos", response_model=List[schemas.ProcesoSchema])
def list_procesos(
    skip: int = 0, 
    limit: int = 100,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    estado: Optional[models.EstadoProceso] = None,
    numero_proceso: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_role)
):
    return crud.get_procesos(db, skip, limit, fecha_desde, fecha_hasta, estado, numero_proceso, license_mode=LICENSE_MODE)

@app.get("/api/procesos/{proceso_id}", response_model=schemas.ProcesoDetailSchema)
def get_proceso_detail(
    proceso_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_role)
):
    proceso = crud.get_proceso(db, proceso_id)
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    # Attach audit trail
    audit_trail = crud.get_audit_trail(db, proceso_id)
    proceso_data = schemas.ProcesoSchema.from_orm(proceso).dict()
    proceso_data["audit_trail"] = audit_trail
    return proceso_data

@app.put("/api/procesos/{proceso_id}", response_model=schemas.ProcesoSchema)
def update_proceso(
    proceso_id: int, 
    updates: schemas.ProcesoUpdate, 
    db: Session = Depends(get_db),
    user: dict = Depends(role_required(["operator", "admin"]))
):
    db_proceso = crud.update_proceso(db, proceso_id, updates, user["name"])
    if not db_proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return db_proceso

@app.delete("/api/procesos/{proceso_id}")
def delete_proceso(
    proceso_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(role_required(["admin"]))
):
    db_proceso = crud.delete_proceso(db, proceso_id, user["name"])
    if not db_proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return {"detail": "Proceso eliminado (soft delete)"}

# ---------------------------------------------------------
# SOPORTE EN TIEMPO REAL (CRM INCIDENTS)
# ---------------------------------------------------------
@app.post("/api/support/ticket")
def create_support_ticket(
    ticket: schemas.SupportTicket,
    user: dict = Depends(get_current_user_role)
):
    """
    Reporta un problema o incidencia al CRM. (DESHABILITADO EN VERSIÓN FREE)
    """
    if LICENSE_MODE == "FREE":
        raise HTTPException(status_code=403, detail="Integración CRM no disponible en versión FREE local.")
    
    if not crm_service:
         raise HTTPException(status_code=503, detail="Servicio de soporte no configurado")
    
    result = crm_service.report_incident(ticket.dict())
    if not result:
        raise HTTPException(status_code=500, detail="No se pudo enviar el reporte de soporte")
        
    return {"status": "success", "ticket_id": result.get("id"), "message": "Reporte enviado correctamente"}

# ---------------------------------------------------------
# CONTRATO DE ARCHIVOS (LEGISCHECHY)
# ---------------------------------------------------------

@app.post("/api/files/folders", tags=["Files"])
def create_folder(
    folder: schemas.FolderCreate,
    user: dict = Depends(rbac_required(["operator", "admin"])),
    storage: StorageService = Depends(get_storage)
):
    storage_utils.ensure_user_layout(FILES_ROOT, user["id"])
    success = storage.create_folder(user["id"], folder.path)
    if not success:
        return JSONResponse(status_code=400, content={"error": {"code": "PATH_INVALID", "message": "Ruta inválida o fuera de sandbox"}})
    return {"status": "success", "path": folder.path}

@app.get("/api/files/folders", tags=["Files"])
def list_files(
    path: str = Query("", description="Ruta relativa para listar"),
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage)
):
    records = storage.list_files(user["id"], path)
    return records

@app.post("/api/files/upload", tags=["Files"])
async def upload_file(
    path: str = FastAPIFile(...),
    file: UploadFile = FastAPIFile(...),
    user: dict = Depends(rbac_required(["operator", "admin"])),
    storage: StorageService = Depends(get_storage)
):
    content = await file.read()
    record = storage.upload_file(user["id"], path, file.filename, content, file.content_type)
    if not record:
        return JSONResponse(status_code=400, content={"error": {"code": "UPLOAD_FAILED", "message": "Error al guardar el archivo"}})
    return record

@app.get("/api/files/download/{file_id}", tags=["Files"])
def download_file(
    file_id: str,
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage)
):
    path = storage.get_file_path(user["id"], file_id)
    if not path or not path.exists():
        return JSONResponse(status_code=404, content={"error": {"code": "FILE_NOT_FOUND", "message": "Archivo no existe"}})
    return FileResponse(path)

@app.post("/api/files/trash", tags=["Files"])
def trash_file(
    request: dict,
    user: dict = Depends(rbac_required(["operator", "admin"])),
    storage: StorageService = Depends(get_storage)
):
    file_id = request.get("file_id")
    success = storage.move_to_trash(user["id"], file_id)
    if not success:
        return JSONResponse(status_code=400, content={"error": {"code": "TRASH_FAILED", "message": "No se pudo mover a la papelera"}})
    return {"status": "success"}

# ---------------------------------------------------------
# ANÁLISIS PENAL (LEGISCHECHY)
# ---------------------------------------------------------
@app.post("/api/analysis/criminal", response_model=schemas.AnalysisResponse, tags=["Criminal Law"])
def analyze_criminal_case(
    query: str = Query(...),
    user: dict = Depends(get_current_user)
):
    """
    Análisis preliminar de casos penales colombianos con IA.
    """
    # Stub de respuesta - En productivo invocar a GeminiService
    return {
        "analysis": f"Análisis preliminar para: {query}. Basado en el Código Penal Colombiano...",
        "hypothesis": ["Posible tipicidad bajo Art 239", "Circunstancia de atenuación probable"],
        "confidence": "yellow",
        "disclaimer": "ESTE ANÁLISIS ES PRELIMINAR, NO CONSTITUYE ASESORÍA LEGAL DEFINITIVA. CONSULTE CON UN ABOGADO."
    }

@app.get("/health", tags=["Ops"])
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "service": "LEGISCHECHY"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
