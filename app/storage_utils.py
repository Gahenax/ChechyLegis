import os
from pathlib import Path
from typing import Optional
import re

def sanitize_path(base_root: str, user_id: str, relative_path: str) -> Optional[Path]:
    """
    Sanitiza y valida una ruta absoluta dentro del sandbox del usuario.
    Reglas GAHENAX:
    - No permite '..'
    - No permite caracteres ilegales
    - Debe estar estrictamente bajo base_root/users/user_id
    """
    if not relative_path:
        relative_path = ""
    
    # Limpiar backslashes y asegurar formato unix-like para validación interna
    clean_rel = relative_path.replace("\\", "/").strip("/")
    
    # Bloquear intentos de traversal obvios
    if ".." in clean_rel or clean_rel.startswith("/") or ":" in clean_rel:
        return None
    
    # Reemplazar caracteres sospechosos (seguridad proactiva)
    clean_rel = re.sub(r'[^a-zA-Z0-9/_.-]', '_', clean_rel)
    
    # Construir ruta final
    sandbox_root = Path(base_root).resolve() / "users" / user_id
    final_path = (sandbox_root / clean_rel).resolve()
    
    # Verificación final de contención
    if not str(final_path).startswith(str(sandbox_root)):
        return None
        
    return final_path

def ensure_user_layout(base_root: str, user_id: str):
    """Crea la estructura de carpetas obligatoria para un nuevo usuario"""
    user_root = Path(base_root).resolve() / "users" / user_id
    dirs = ["inbox", "cases", "docs", "exports", "trash", ".meta"]
    for d in dirs:
        (user_root / d).mkdir(parents=True, exist_ok=True)
