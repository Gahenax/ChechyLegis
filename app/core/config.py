import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables de entorno
load_dotenv()

class Config:
    # Versión y Metadatos
    VERSION = "1.1.0-REF"
    PROJECT_NAME = "ChechyLegis"
    AUTHOR = "Gahenax Hub"

    # Licencia y Límites
    LICENSE_MODE = os.getenv("LICENSE_MODE", "FREE").upper()  # FREE | PRO
    MAX_CASES_FREE = 3
    MAX_DOCS_FREE = 10

    # Seguridad
    JWT_SECRET = os.getenv("JWT_SECRET")  # Requerido en .env
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-token")
    OPERATOR_TOKEN = os.getenv("OPERATOR_TOKEN", "operator-token")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
    
    # Rutas de Archivos
    FILES_ROOT = os.getenv("FILES_ROOT", os.path.join(os.getcwd(), "storage"))
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    @classmethod
    def validate(cls):
        """Valida configuraciones críticas."""
        if not cls.GEMINI_API_KEY:
            print("⚠️ ADVERTENCIA: GEMINI_API_KEY no configurada. Funciones IA limitadas.")
        
        if not cls.JWT_SECRET:
            raise ValueError("❌ ERROR CRÍTICO: JWT_SECRET no configurada en el entorno.")
        
        if not os.path.exists(cls.FILES_ROOT):
            os.makedirs(cls.FILES_ROOT, exist_ok=True)
            print(f"✅ Sandbox de archivos creado en: {cls.FILES_ROOT}")

# Inicializar configuración
settings = Config()
settings.validate()
