from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

security = HTTPBearer()

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Simulación de autenticación JWT.
    En producción, aquí se decodificaría el token JWT.
    """
    token = auth.credentials
    if token == settings.ADMIN_TOKEN:
        return {"id": "admin_user", "role": "admin", "name": "Administrador"}
    elif token == settings.OPERATOR_TOKEN:
        return {"id": "op_user", "role": "operator", "name": "Operador Legal"}
    elif token == "viewer-token" or not settings.ADMIN_TOKEN: # Fallback para desarrollo
        return {"id": "viewer_user", "role": "viewer", "name": "Consultor"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

def role_required(allowed_roles: list[str]):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker
