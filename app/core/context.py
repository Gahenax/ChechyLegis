import contextvars
from typing import Optional

# Variable de contexto para rastrear el usuario actual en el hilo de la petición
current_user_name = contextvars.ContextVar("current_user_name", default="Anónimo")

def set_current_user(name: str):
    current_user_name.set(name)

def get_current_user_name() -> str:
    return current_user_name.get()
