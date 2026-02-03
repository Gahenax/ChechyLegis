import os
import requests
import json
from typing import Dict, Any, Optional
import logging

# Configurar logger
logger = logging.getLogger("chechy.crm")

class CRMService:
    """
    Servicio de integración con CRM externo.
    Permite sincronizar procesos y clientes con un CRM a través de API REST.
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
        """Verifica conexión con el CRM"""
        try:
            # Asume un endpoint estándar /health o /api/status. Ajustar según CRM real.
            # Si es un CRM genérico, podríamos probar un GET /users/me o similar.
            response = requests.get(f"{self.base_url}/status", headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error conectando a CRM: {e}")
            return False

    def sync_proceso(self, proceso_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Envía un nuevo proceso al CRM (ej. como un 'Deal' o 'Caso').
        """
        endpoint = f"{self.base_url}/leads" # Ajustar a 'deals', 'cases', etc.
        
        # Mapeo de datos (Adapter Pattern simplificado)
        payload = {
            "title": f"Proceso {proceso_data.get('numero_proceso')} - {proceso_data.get('demandante')} vs {proceso_data.get('demandado')}",
            "description": proceso_data.get("descripcion", ""),
            "value": 0, # Valor por defecto
            "status": "new",
            "custom_fields": {
                "radicado": proceso_data.get("numero_proceso"),
                "tipo": proceso_data.get("tipo", "Ejecutivo"),
                "juzgado": proceso_data.get("despacho", "")
            },
            "contact": {
                "name": proceso_data.get("demandante", "Desconocido")
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"Proceso sincronizado con CRM: {response.json().get('id')}")
                return response.json()
            else:
                logger.error(f"Fallo sync CRM: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Excepción en sync CRM: {e}")
            return None

    def get_client_info(self, client_id_or_email: str) -> Optional[Dict[str, Any]]:
        """Busca información de cliente en CRM"""
        try:
            response = requests.get(
                f"{self.base_url}/contacts/search", 
                params={"q": client_id_or_email},
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                results = response.json()
                return results[0] if results else None
            return None
        except Exception as e:
            logger.error(f"Error fetching client from CRM: {e}")
            return None
