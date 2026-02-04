from fastapi import APIRouter, Depends, Query
from ..schemas import AnalysisResponse
from ..core.config import settings
from ..core.security import get_current_user

router = APIRouter(
    prefix="/api/analysis",
    tags=["Asistente IA (Gemini)"]
)

@router.post("/criminal", response_model=AnalysisResponse)
def analyze_criminal_case(
    query: str = Query(...),
    user: dict = Depends(get_current_user)
):
    """
    Análisis preliminar de casos penales colombianos con IA (Gemini).
    """
    # En productivo se inyectaría GeminiService
    return {
        "analysis": f"Módulo IA Activo: Analizando '{query}' bajo normativa colombiana...",
        "hypothesis": [
            "Evaluación de tipicidad objetiva Art 9 C.P.",
            "Análisis de antijuridicidad material"
        ],
        "confidence": "green" if settings.GEMINI_API_KEY else "yellow",
        "disclaimer": "CONSULTA NO VINCULANTE. GAHENAX CORE."
    }
