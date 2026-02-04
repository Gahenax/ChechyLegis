from fastapi import APIRouter, Depends, Query
from ..schemas import AnalysisResponse
from ..core.config import settings
from ..core.security import get_current_user

from ..gemini_service import GeminiService

router = APIRouter(
    prefix="/api/analysis",
    tags=["Asistente IA (Gemini)"]
)

# Inyectar servicio
ai_service = GeminiService(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

@router.post("/criminal", response_model=AnalysisResponse)
def analyze_criminal_case(
    query: str = Query(...),
    user: dict = Depends(get_current_user)
):
    """
    Análisis preliminar de casos penales colombianos con IA (Gemini).
    """
    if not ai_service:
        return {
            "analysis": "ERROR DE CONFIGURACIÓN: GEMINI_API_KEY no configurada.",
            "hypothesis": ["Por favor, configure su API Key en el archivo .env"],
            "confidence": "red",
            "disclaimer": "SISTEMA LIMITADO."
        }
    
    # Usar el asistente conversacional para análisis general de la consulta
    response_text = ai_service.chat_assistant(query)
    
    # Mapear a la respuesta esperada por el frontend
    return {
        "analysis": response_text,
        "hypothesis": [
            "Evaluación de tipicidad según C.P. Colombiano",
            "Análisis preventivo de riesgos procesales"
        ],
        "confidence": "green",
        "disclaimer": "ESTE ANÁLISIS ES GENERADO POR IA Y NO SUSTITUYE EL JUICIO HUMANO."
    }
