from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Text, ForeignKey, Float
from sqlalchemy.sql import func
import enum
from .database import Base

class EstadoProceso(enum.Enum):
    ACTIVO = "ACTIVO"
    TERMINADO = "TERMINADO"
    SUSPENDIDO = "SUSPENDIDO"
    RECHAZADO = "RECHAZADO"

class CuantiaTipo(enum.Enum):
    MINIMA = "MINIMA"
    MENOR = "MENOR"
    MAYOR = "MAYOR"

class ExtractionStatus(enum.Enum):
    PENDING = "PENDING"
    OK = "OK"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class LinkReason(enum.Enum):
    MATCH_NUMBER = "MATCH_NUMBER"
    HEURISTIC = "HEURISTIC"
    LLM = "LLM"
    MANUAL = "MANUAL"

class Proceso(Base):
    __tablename__ = "procesos"

    id = Column(Integer, primary_key=True, index=True)
    numero_proceso = Column(String, unique=True, index=True, nullable=False)
    fecha_radicacion = Column(Date, nullable=False)
    estado = Column(Enum(EstadoProceso), nullable=False)
    fecha_ultima_actuacion = Column(Date, nullable=True)
    clase_proceso = Column(String, nullable=True)
    cuantia_tipo = Column(Enum(CuantiaTipo), nullable=True)
    partes = Column(String, nullable=False)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, nullable=False)
    accion = Column(String, nullable=False) # CREATE, UPDATE, DELETE
    entidad = Column(String, default="PROCESO")
    entidad_id = Column(Integer, nullable=False)
    campo_modificado = Column(String, nullable=True)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, unique=True, nullable=False)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String(64), unique=True, nullable=False, index=True)
    uploaded_by = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    extracted_text = Column(Text, nullable=True)
    extraction_status = Column(Enum(ExtractionStatus), default=ExtractionStatus.PENDING)
    error_message = Column(Text, nullable=True)

class ProcessDocument(Base):
    __tablename__ = "process_documents"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("procesos.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    linked_at = Column(DateTime(timezone=True), server_default=func.now())
    linked_by = Column(String, nullable=False)
    link_reason = Column(Enum(LinkReason), nullable=False)
    confidence = Column(Float, nullable=True)  # Para asociaciones con IA

