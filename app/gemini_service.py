"""
Servicio de IA usando Gemini API (Nueva versión google-genai)
Proporciona búsqueda semántica y análisis de lenguaje natural
"""

from google import genai
from google.genai import types
from typing import List, Dict, Any
import json
from datetime import datetime

class GeminiService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-flash-latest'
    
    def parse_natural_query(self, query: str, procesos: List[Dict]) -> Dict[str, Any]:
        """
        Convierte una consulta en lenguaje natural a filtros estructurados
        Ejemplo: "procesos activos de enero" -> {"estado": "ACTIVO", "mes": 1}
        """
        
        prompt = f"""
Eres un asistente legal especializado en procesos judiciales.

CONTEXTO: Tienes acceso a {len(procesos)} procesos judiciales.

CONSULTA DEL USUARIO: "{query}"

TAREA: Analiza la consulta y genera una respuesta estructurada en JSON con:
1. "filtros": objeto con los filtros a aplicar (estado, fecha_desde, fecha_hasta, numero_proceso, partes, clase_proceso)
2. "interpretacion": explicación breve de cómo interpretaste la consulta
3. "sugerencias": array de búsquedas relacionadas que el usuario podría querer hacer

ESTADOS VÁLIDOS: ACTIVO, TERMINADO, SUSPENDIDO, RECHAZADO

EJEMPLO DE RESPUESTA:
{{
  "filtros": {{
    "estado": "ACTIVO",
    "fecha_desde": "2024-01-01",
    "fecha_hasta": "2024-01-31"
  }},
  "interpretacion": "Buscando procesos activos del mes de enero de 2024",
  "sugerencias": [
    "procesos terminados de enero",
    "procesos activos de febrero",
    "todos los procesos de 2024"
  ]
}}

Responde SOLO con el JSON, sin texto adicional.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            return {
                "filtros": {},
                "interpretacion": f"No pude interpretar la consulta: {str(e)}",
                "sugerencias": []
            }
    
    def analyze_proceso(self, proceso: Dict) -> Dict[str, Any]:
        """
        Analiza un proceso y genera insights automáticos
        """
        
        prompt = f"""
Eres un asistente legal. Analiza el siguiente proceso judicial:

DATOS DEL PROCESO:
- Número: {proceso.get('numero_proceso')}
- Estado: {proceso.get('estado')}
- Fecha Radicación: {proceso.get('fecha_radicacion')}
- Partes: {proceso.get('partes')}
- Clase: {proceso.get('clase_proceso', 'No especificada')}
- Cuantía: {proceso.get('cuantia_tipo', 'No especificada')}
- Observaciones: {proceso.get('observaciones', 'Ninguna')}

TAREA: Genera un análisis en JSON con:
1. "resumen": resumen ejecutivo del proceso (máx 2 líneas)
2. "alertas": array de posibles alertas o puntos de atención
3. "clasificacion_sugerida": tipo de proceso sugerido si no está especificado
4. "acciones_recomendadas": array de próximas acciones sugeridas

Responde SOLO con el JSON, sin texto adicional.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            return {
                "resumen": "Error al analizar el proceso",
                "alertas": [],
                "clasificacion_sugerida": "No disponible",
                "acciones_recomendadas": []
            }
    
    def find_similar_cases(self, proceso: Dict, all_procesos: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Encuentra casos similares usando análisis semántico
        """
        
        # Crear descripción del proceso actual
        proceso_desc = f"""
Proceso {proceso.get('numero_proceso')}:
- Estado: {proceso.get('estado')}
- Clase: {proceso.get('clase_proceso', 'No especificada')}
- Partes: {proceso.get('partes')}
- Cuantía: {proceso.get('cuantia_tipo', 'No especificada')}
- Observaciones: {proceso.get('observaciones', 'Ninguna')}
"""
        
        # Crear lista de otros procesos
        otros_procesos = [p for p in all_procesos if p.get('id') != proceso.get('id')]
        
        if not otros_procesos:
            return []
        
        procesos_desc = "\n\n".join([
            f"ID {p.get('id')}: {p.get('numero_proceso')} - {p.get('clase_proceso', 'Sin clase')} - {p.get('partes')}"
            for p in otros_procesos[:20]  # Limitar para no saturar el prompt
        ])
        
        prompt = f"""
Eres un asistente legal especializado en encontrar casos similares.

PROCESO DE REFERENCIA:
{proceso_desc}

OTROS PROCESOS DISPONIBLES:
{procesos_desc}

TAREA: Identifica los {limit} procesos más similares al proceso de referencia.
Considera: tipo de proceso, partes involucradas, cuantía, y naturaleza del caso.

Responde SOLO con un JSON array de IDs ordenados por similitud (más similar primero):
[id1, id2, id3, ...]

Ejemplo: [5, 12, 3, 8, 1]
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            similar_ids = json.loads(response.text.strip())
            
            # Retornar los procesos completos en orden de similitud
            result = []
            for proc_id in similar_ids[:limit]:
                matching = next((p for p in otros_procesos if p.get('id') == proc_id), None)
                if matching:
                    result.append(matching)
            
            return result
        except Exception as e:
            return []
    
    def chat_assistant(self, message: str, context: Dict = None) -> str:
        """
        Asistente conversacional para consultas generales
        """
        
        context_str = ""
        if context:
            context_str = f"\n\nCONTEXTO ACTUAL:\n{json.dumps(context, indent=2, ensure_ascii=False)}"
        
PROMPT = f"""
Eres un asistente legal virtual de ChechyLegis (Versión FREE).
REGLAS CRÍTICAS:
1. NUNCA prometas resultados judiciales ni des asesoría legal definitiva.
2. Todo análisis es HIPOTÉTICO y PRELIMINAR.
3. El usuario es un profesional y tú eres solo un apoyo.

Puedes ayudar con:
- Búsqueda de procesos (Máx 3 activos en esta versión)
- Explicación de estados y procedimientos
- Sugerencias de clasificación
- Análisis de casos

MENSAJE DEL USUARIO: "{message}"{context_str}

Responde de manera clara, profesional y concisa. Si necesitas más información, pregunta.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Lo siento, ocurrió un error: {str(e)}"
