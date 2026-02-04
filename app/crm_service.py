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
    Envía incidencias en tiempo real al sistema de soporte.
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def check_health(self) -> bool:
        """Verifica conexión con el backend de soporte"""
        try:
            response = requests.get(f"{self.base_url}/status", headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error conectando a Soporte: {e}")
            return False

    def report_incident(self, ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Envía un ticket de soporte al CRM.
        """
        endpoint = f"{self.base_url}/tickets" 
        
        payload = {
            "subject": ticket_data.get("subject", "Problema sin asunto"),
            "body": ticket_data.get("description", ""),
            "priority": ticket_data.get("priority", "medium"),
            "metadata": {
                "user_email": ticket_data.get("user_email"),
                "source": "ChechyLegis-App",
                "timestamp": str(datetime.now()) if 'datetime' in globals() else str(datetime.now().isoformat())
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"Ticket enviado con éxito: {response.json().get('id')}")
                return response.json()
            else:
                logger.error(f"Fallo envío ticket: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Excepción en envío ticket: {e}")
            return None
