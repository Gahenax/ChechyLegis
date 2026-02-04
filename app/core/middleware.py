from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .context import set_current_user
import time
import logging

logger = logging.getLogger("gahenax.audit")

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Identificar usuario (simplificado, asumiendo que security ya validó o vendrá después)
        # Nota: En una arquitectura real, el middleware de auth debería ir ANTES que este
        # o este middleware debería extraer el usuario de los headers/cookies.
        
        user_name = request.headers.get("X-User-Name", "Sistema")
        
        # Establecer en el contexto para los listeners de la base de datos
        set_current_user(user_name)
        
        start_time = time.time()
        
        # Procesar petición
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log de acción en consola/logs (Caja Negra de Red)
        if request.url.path.startswith("/api"):
            logger.info(f"AUDIT: {user_name} | {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.4f}s")
        
        return response
