from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from .models import EstadoProceso, CuantiaTipo, ExtractionStatus, LinkReason

class ProcesoBase(BaseModel):
    numero_proceso: str
    fecha_radicacion: date
    estado: EstadoProceso
    partes: str
    fecha_ultima_actuacion: Optional[date] = None
    clase_proceso: Optional[str] = None
    cuantia_tipo: Optional[CuantiaTipo] = None
    observaciones: Optional[str] = None

class ProcesoCreate(ProcesoBase):
    pass

class ProcesoUpdate(BaseModel):
    numero_proceso: Optional[str] = None
    fecha_radicacion: Optional[date] = None
    estado: Optional[EstadoProceso] = None
    partes: Optional[str] = None
    fecha_ultima_actuacion: Optional[date] = None
    clase_proceso: Optional[str] = None
    cuantia_tipo: Optional[CuantiaTipo] = None
    observaciones: Optional[str] = None

class AuditLogSchema(BaseModel):
    id: int
    usuario: str
    accion: str
    entidad: str
    entidad_id: int
    campo_modificado: Optional[str]
    valor_anterior: Optional[str]
    valor_nuevo: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class ProcesoSchema(ProcesoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProcesoDetailSchema(ProcesoSchema):
    audit_trail: List[AuditLogSchema] = []

# ============================================
# SCHEMAS DE DOCUMENTOS
# ============================================

class DocumentSchema(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    uploaded_by: str
    uploaded_at: datetime
    extracted_text: Optional[str]
    extraction_status: ExtractionStatus
    error_message: Optional[str]

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    document_id: int
    status: str
    message: str
    action: Optional[str] = None  # LINKED, NEEDS_REVIEW
    process_id: Optional[int] = None
    numero_proceso: Optional[str] = None
    link_reason: Optional[str] = None
    confidence: Optional[float] = None

class ProcessDocumentSchema(BaseModel):
    id: int
    process_id: int
    document_id: int
    linked_at: datetime
    linked_by: str
    link_reason: LinkReason
    confidence: Optional[float]

    class Config:
        from_attributes = True

class LinkDocumentResponse(BaseModel):
    success: bool
    message: str
    process_id: Optional[int] = None
    document_id: int

