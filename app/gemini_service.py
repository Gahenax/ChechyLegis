"""
Servicio de IA usando Gemini API (Nueva versión google-genai)
Proporciona búsqueda semántica y análisis de lenguaje natural
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import logging
from functools import lru_cache
from datetime import datetime

logger = logging.getLogger("chechy.gemini")

class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def parse_natural_query(self, query: str, procesos: List[Dict]) -> Dict[str, Any]:
        """
        Convierte una consulta en lenguaje natural a filtros estructurados.
        """
        
        prompt = f"""
Eres un asistente legal especializado en procesos judiciales.
CONTEXTO: Tienes acceso a {len(procesos)} procesos judiciales.
CONSULTA DEL USUARIO: "{query}"
TAREA: Analiza la consulta y genera una respuesta estructurada en JSON.
Responde SOLO con el JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Remove markdown code blocks if present
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error en parse_natural_query: {e}")
            return {"filtros": {}, "interpretacion": "Error al interpretar", "sugerencias": []}
    
    @lru_cache(maxsize=128)
    def analyze_proceso(self, proceso_json: str) -> Dict[str, Any]:
        """
        Analiza un proceso y genera insights automáticos.
        """
        proceso = json.loads(proceso_json)
        prompt = f"Analiza este proceso judicial y devuelve JSON: {proceso_json}"
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error en analyze_proceso: {e}")
            return {"resumen": "Error", "alertas": []}

    def chat_assistant(self, message: str, context: Dict = None) -> str:
        """
        Asistente conversacional.
        """
        prompt = f"Asistente Legal: {message}"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error en chat_assistant: {e}")
            return "Lo siento, hubo un error."
