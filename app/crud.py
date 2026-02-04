from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
from typing import Optional, List
import json

def get_proceso(db: Session, proceso_id: int):
    return db.query(models.Proceso).filter(models.Proceso.id == proceso_id, models.Proceso.deleted_at == None).first()

def get_proceso_by_numero(db: Session, numero: str):
    return db.query(models.Proceso).filter(models.Proceso.numero_proceso == numero, models.Proceso.deleted_at == None).first()

def get_procesos(db: Session, skip: int = 0, limit: int = 100, 
                 fecha_desde: Optional[date] = None, 
                 fecha_hasta: Optional[date] = None,
                 estado: Optional[models.EstadoProceso] = None,
                 numero_proceso: Optional[str] = None,
                 license_mode: str = "FREE"):
    query = db.query(models.Proceso).filter(models.Proceso.deleted_at == None)
    
    if license_mode == "FREE":
        from datetime import datetime, timedelta
        limit_date = datetime.now().date() - timedelta(days=30)
        query = query.filter(models.Proceso.fecha_radicacion >= limit_date)
    
    if fecha_desde:
        query = query.filter(models.Proceso.fecha_radicacion >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.Proceso.fecha_radicacion <= fecha_hasta)
    if estado:
        query = query.filter(models.Proceso.estado == estado)
    if numero_proceso:
        query = query.filter(models.Proceso.numero_proceso.contains(numero_proceso))
        
    return query.offset(skip).limit(limit).all()

def create_proceso(db: Session, proceso: schemas.ProcesoCreate):
    db_proceso = models.Proceso(**proceso.dict())
    db.add(db_proceso)
    db.commit()
    db.refresh(db_proceso)
    return db_proceso

def update_proceso(db: Session, proceso_id: int, updates: schemas.ProcesoUpdate):
    db_proceso = get_proceso(db, proceso_id)
    if not db_proceso:
        return None
    
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_proceso, key, value)
    
    db.commit()
    db.refresh(db_proceso)
    return db_proceso

def delete_proceso(db: Session, proceso_id: int):
    db_proceso = get_proceso(db, proceso_id)
    if not db_proceso:
        return None
    
    import datetime
    db_proceso.deleted_at = datetime.datetime.now()
    db.commit()
    return db_proceso

def get_audit_trail(db: Session, entidad_id: int):
    return db.query(models.AuditLog).filter(models.AuditLog.entidad_id == entidad_id).order_by(models.AuditLog.timestamp.desc()).all()
