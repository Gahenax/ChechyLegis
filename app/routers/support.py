from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from ..core.config import settings
from ..crm_service import CRMService
from ..hotel_auth import require_auth, HotelGuest

router = APIRouter(
    prefix="/api/support",
    tags=["Soporte & CRM"]
)

# Shared instance for the pilot
crm = CRMService()

@router.post("/ticket")
async def create_support_ticket(
    ticket: schemas.SupportTicket,
    user: HotelGuest = Depends(require_auth)
):
    """
    Reporta un problema o incidencia a la Oficina Central (King CRM).
    """
    ticket_data = {
        "subject": ticket.subject,
        "description": ticket.description,
        "priority": ticket.priority,
        "user_email": user.email
    }
    
    result = crm.report_incident(ticket_data)
    
    if not result:
        raise HTTPException(
            status_code=503,
            detail="La Oficina Central no está respondiendo. Intente más tarde."
        )
    
    return {
        "status": "success", 
        "message": "Reporte enviado con éxito a la Oficina Central.",
        "remote_id": result.get("id")
    }
