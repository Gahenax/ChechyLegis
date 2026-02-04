from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from ..core.config import settings
from ..core.security import get_current_user

router = APIRouter(
    prefix="/api/support",
    tags=["Soporte & CRM"]
)

@router.post("/ticket")
def create_support_ticket(
    ticket: schemas.SupportTicket,
    user: dict = Depends(get_current_user)
):
    """
    Reporta un problema o incidencia al CRM. (DESHABILITADO EN VERSIÓN FREE)
    """
    if settings.LICENSE_MODE == "FREE":
        raise HTTPException(
            status_code=403, 
            detail="Integración CRM no disponible en versión FREE local."
        )
    
    # Aquí se integraría con crm_service.py
    return {
        "status": "success", 
        "message": "Reporte recibido en Gahenax Hub (PRO Simulado)"
    }
