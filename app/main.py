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

from . import models, schemas, crud, database
from .database import engine, get_db
from .gemini_service import GeminiService
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Archivo Virtual de Procesos Judiciales")

# Inicializar servicio de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_service = GeminiService(GEMINI_API_KEY) if GEMINI_API_KEY else None

# Inicializar servicio CRM
from .crm_service import CRMService
CRM_URL = os.getenv("CRM_API_URL", "")
CRM_KEY = os.getenv("CRM_API_KEY", "")

crm_service = None
if CRM_URL and CRM_KEY:
    crm_service = CRMService(CRM_URL, CRM_KEY)
    logger.info(f"CRM Service activado: {CRM_URL}")
else:
    logger.info("CRM Service no configurado (Faltan variables de entorno)")

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
    existing = crud.get_proceso_by_numero(db, proceso.numero_proceso)
    if existing:
        raise HTTPException(status_code=400, detail="El número de proceso ya existe")
    new_proceso = crud.create_proceso(db=db, proceso=proceso, usuario=user["name"])
    
    # Sincronizar con CRM si está activo (Fire & Forget idealmente, aquí síncrono por simplicidad)
    if crm_service:
        try:
            proceso_dict = schemas.ProcesoSchema.from_orm(new_proceso).dict()
            crm_service.sync_proceso(proceso_dict)
        except Exception as e:
            logger.warning(f"No se pudo sincronizar con CRM: {e}")
            
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
    return crud.get_procesos(db, skip, limit, fecha_desde, fecha_hasta, estado, numero_proceso)

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

# ============================================
# ENDPOINTS DE IA CON GEMINI
# ============================================

class NaturalQueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

@app.post("/api/ai/search")
def natural_language_search(
    request: NaturalQueryRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_role)
):
    """
    Búsqueda en lenguaje natural usando Gemini
    Ejemplo: "procesos activos de enero" o "casos de María García"
    """
    if not gemini_service:
        raise HTTPException(status_code=503, detail="Servicio de IA no disponible. Configure GEMINI_API_KEY")
    
    # Obtener todos los procesos para contexto
    all_procesos = crud.get_procesos(db, 0, 1000)
    procesos_dict = [schemas.ProcesoSchema.from_orm(p).dict() for p in all_procesos]
    
    # Analizar consulta con Gemini
    result = gemini_service.parse_natural_query(request.query, procesos_dict)
    
    # Aplicar filtros interpretados
    filtros = result.get("filtros", {})
    filtered_procesos = crud.get_procesos(
        db, 
        0, 
        100,
        fecha_desde=filtros.get("fecha_desde"),
        fecha_hasta=filtros.get("fecha_hasta"),
        estado=filtros.get("estado"),
        numero_proceso=filtros.get("numero_proceso")
    )
    
    return {
        "query_original": request.query,
        "interpretacion": result.get("interpretacion"),
        "filtros_aplicados": filtros,
        "resultados": [schemas.ProcesoSchema.from_orm(p).dict() for p in filtered_procesos],
        "total_resultados": len(filtered_procesos),
        "sugerencias": result.get("sugerencias", [])
    }

@app.get("/api/ai/analyze/{proceso_id}")
def analyze_proceso(
    proceso_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_role)
):
    """
    Analiza un proceso usando IA y genera insights automáticos
    """
    if not gemini_service:
        raise HTTPException(status_code=503, detail="Servicio de IA no disponible. Configure GEMINI_API_KEY")
    
    proceso = crud.get_proceso(db, proceso_id)
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    proceso_dict = schemas.ProcesoSchema.from_orm(proceso).dict()
    analysis = gemini_service.analyze_proceso(proceso_dict)
    
    return {
        "proceso": proceso_dict,
        "analisis": analysis
    }

@app.get("/api/ai/similar/{proceso_id}")
def find_similar_cases(
    proceso_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_role)
):
    """
    Encuentra casos similares usando análisis semántico de IA
    """
    if not gemini_service:
        raise HTTPException(status_code=503, detail="Servicio de IA no disponible. Configure GEMINI_API_KEY")
    
    proceso = crud.get_proceso(db, proceso_id)
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    all_procesos = crud.get_procesos(db, 0, 1000)
    procesos_dict = [schemas.ProcesoSchema.from_orm(p).dict() for p in all_procesos]
    proceso_dict = schemas.ProcesoSchema.from_orm(proceso).dict()
    
    similar = gemini_service.find_similar_cases(proceso_dict, procesos_dict, limit)
    
    return {
        "proceso_referencia": proceso_dict,
        "casos_similares": similar,
        "total_encontrados": len(similar)
    }

@app.post("/api/ai/chat")
def chat_assistant(
    request: ChatRequest,
    user: dict = Depends(get_current_user_role)
):
    """
    Asistente conversacional para consultas generales sobre el sistema
    """
    if not gemini_service:
        raise HTTPException(status_code=503, detail="Servicio de IA no disponible. Configure GEMINI_API_KEY")
    
    response = gemini_service.chat_assistant(request.message, request.context)
    
    return {
        "mensaje_usuario": request.message,
        "respuesta": response
    }

# Static files for frontend
@app.get("/", include_in_schema=False)
async def serve_root():
    return FileResponse("static/index.html")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_or_static(full_path: str):
    # Seguridad básica contra directory traversal
    if ".." in full_path:
         raise HTTPException(status_code=404)
         
    # 1. Intentar servir archivo estático exacto
    static_file_path = os.path.join("static", full_path)
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    
    # 2. Si es API, dejar que sea 404 real (aunque las rutas API definidas arriba tienen precedencia)
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
        
    # 3. Fallback a index.html para rutas de SPA (ej: /settings, /login)
    return FileResponse("static/index.html")
