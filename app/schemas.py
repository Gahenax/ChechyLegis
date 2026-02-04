from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from .models import EstadoProceso, CuantiaTipo, ExtractionStatus, LinkReason

# ============================================
# SCHEMAS DE ERROR ESTÁNDAR
# ============================================

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class APIError(BaseModel):
    error: ErrorDetail

# ============================================
# SCHEMAS DE ARCHIVOS (Legischechy Contract)
# ============================================

class FileMeta(BaseModel):
    file_id: str
    name: str
    path: str
    mime_type: str
    size_bytes: int
    sha256: str
    created_at: datetime
    updated_at: datetime
    labels: List[str] = []

class FolderCreate(BaseModel):
    path: str = Field(..., example="cases/proc_2026_0001")

class FileMove(BaseModel):
    file_id: str
    to_path: str

class FileRename(BaseModel):
    file_id: str
    new_name: str

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

# ============================================
# SCHEMAS DE SOPORTE / CRM
# ============================================

class SupportTicket(BaseModel):
    subject: str = Field(..., min_length=5)
    description: str
    priority: str = "medium"
    user_email: Optional[str] = "anon@legis.tech"

# ============================================
# LEGAL / SAFETY (Analysis Response)
# ============================================

class AnalysisResponse(BaseModel):
    analysis: str
    hypothesis: List[str] = []
    confidence: str = Field(..., description="green/yellow/red")
    disclaimer: str = "ESTE ANÁLISIS ES PRELIMINAR, NO CONSTITUYE ASESORÍA LEGAL DEFINITIVA Y NO GARANTIZA RESULTADOS. CONSULTE CON UN ABOGADO TITULADO."

