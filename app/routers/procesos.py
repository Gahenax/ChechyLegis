from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from .. import crud, models, schemas
from ..database import get_db
from ..core.config import settings
from ..core.security import get_current_user, role_required

router = APIRouter(
    prefix="/api/procesos",
    tags=["Procesos Judiciales"]
)

@router.post("", response_model=schemas.ProcesoSchema)
def create_proceso(
    proceso: schemas.ProcesoCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(role_required(["admin", "operator"]))
):
    # Enforce FREE limits
    if settings.LICENSE_MODE == "FREE":
        current_count = db.query(models.Proceso).filter(models.Proceso.deleted_at == None).count()
        if current_count >= settings.MAX_CASES_FREE:
            raise HTTPException(
                status_code=403, 
                detail=f"Límite de la versión FREE alcanzado ({settings.MAX_CASES_FREE} casos)."
            )

    existing = crud.get_proceso_by_numero(db, proceso.numero_proceso)
    if existing:
        raise HTTPException(status_code=400, detail="El número de proceso ya existe")
    
    new_proceso = crud.create_proceso(db=db, proceso=proceso)
    return new_proceso

@router.get("", response_model=List[schemas.ProcesoSchema])
def list_procesos(
    skip: int = 0, 
    limit: int = 100,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    estado: Optional[models.EstadoProceso] = None,
    numero_proceso: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return crud.get_procesos(db, skip, limit, fecha_desde, fecha_hasta, estado, numero_proceso, license_mode=settings.LICENSE_MODE)

@router.get("/{proceso_id}", response_model=schemas.ProcesoDetailSchema)
def get_proceso_detail(
    proceso_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    proceso = crud.get_proceso(db, proceso_id)
    if not proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    
    audit_trail = crud.get_audit_trail(db, proceso_id)
    proceso_data = schemas.ProcesoSchema.model_validate(proceso).model_dump()
    proceso_data["audit_trail"] = audit_trail
    return proceso_data

@router.put("/{proceso_id}", response_model=schemas.ProcesoSchema)
def update_proceso(
    proceso_id: int, 
    updates: schemas.ProcesoUpdate, 
    db: Session = Depends(get_db),
    user: dict = Depends(role_required(["admin", "operator"]))
):
    db_proceso = crud.update_proceso(db, proceso_id, updates)
    if not db_proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return db_proceso

@router.delete("/{proceso_id}")
def delete_proceso(
    proceso_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(role_required(["admin"]))
):
    db_proceso = crud.delete_proceso(db, proceso_id)
    if not db_proceso:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return {"detail": "Proceso eliminado (soft delete)"}
