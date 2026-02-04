from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

from .core.config import settings
from .routers import procesos, storage, ai_engine, support, jules
from .core.middleware import AuditMiddleware
from .core.audit import register_audit_listeners
from . import models
from .database import engine

# Inicializar Base de Datos y Auditoría
models.Base.metadata.create_all(bind=engine)
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
    allow_origins=["*"],
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

@app.get("/gahenax_hub.html")
async def serve_hub():
    hub_file = os.path.join(static_path, "gahenax_hub.html")
    if os.path.exists(hub_file):
        return FileResponse(hub_file)
    return JSONResponse(status_code=404, content={"detail": "Hub not found"})

@app.get("/")
@app.get("/{full_path:path}")
async def serve_index(request: Request, full_path: str = ""):
    # Si la ruta comienza con /api o /static, dejar que FastAPI la maneje normalmente
    if full_path.startswith("api") or full_path.startswith("static") or full_path.startswith("downloads"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Gahenax Core Online. Static files not found."}

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
