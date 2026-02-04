import os
import requests
import json
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Configurar logger
logger = logging.getLogger("chechy.crm")

class CRMService:
    """
    Servicio de Soporte y Reporte de Problemas (CRM).
    Envía incidencias en tiempo real al sistema de soporte (KING CRM).
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000", api_key: str = "TKN-3D9A855B"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        # Usamos Bearer token como estándar del Hotel
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def check_health(self) -> bool:
        """Verifica conexión con el backend de soporte (Office)"""
        try:
            # Note: Mock CRM might not have /status, usually we just check base URL or a known endpoint
            response = requests.post(f"{self.base_url}/tickets", json={}, headers=self.headers, timeout=2)
            # 400 is fine here as it means we hit the server but sent empty body
            return response.status_code in [201, 400]
        except Exception as e:
            logger.error(f"Error conectando a la Oficina (CRM): {e}")
            return False

    def report_incident(self, ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Envía un ticket de soporte al CRM.
        """
        endpoint = f"{self.base_url}/tickets" 
        
        payload = {
            "subject": ticket_data.get("subject", "Problema sin asunto"),
            "description": ticket_data.get("description", ticket_data.get("body", "")),
            "priority": ticket_data.get("priority", "medium"),
            "user_email": ticket_data.get("user_email", "guest@gahenax.com"),
            "metadata": {
                "source": "ChechyLegis-Room-101",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=10)
            if response.status_code in [200, 201]:
                res_data = response.json()
                logger.info(f"Reporte enviado a Oficina Central: {res_data.get('id')}")
                return res_data
            else:
                logger.error(f"Fallo reporte a Oficina: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Excepción en reporte a Oficina: {e}")
            return None
