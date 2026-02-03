"""
Configuración para construcción del instalador de ChechyLegis
Este archivo contiene la configuración para PyInstaller
"""

import sys
import os

# Información de la aplicación
APP_NAME = "ChechyLegis"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Archivo Virtual de Procesos Judiciales con IA"
APP_AUTHOR = "ChechyLegis Team"
APP_ICON = "icon.ico"

# Configuración de PyInstaller
PYINSTALLER_CONFIG = {
    'name': APP_NAME,
    'icon': APP_ICON,
    'onefile': False,  # False para mejor rendimiento
    'console': False,  # Sin consola en producción
    'windowed': True,
    'add_data': [
        ('static', 'static'),
        ('app', 'app'),
        ('.env.example', '.'),
        ('icon.ico', '.'),
        ('icon.png', '.'),
    ],
    'hidden_imports': [
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'sqlalchemy.sql.default_comparator',
        'google.generativeai',
        'passlib.handlers.bcrypt',
    ],
    'exclude_modules': [
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
    ],
}

# Configuración de Inno Setup
INNO_SETUP_CONFIG = {
    'app_name': APP_NAME,
    'app_version': APP_VERSION,
    'app_publisher': APP_AUTHOR,
    'app_url': 'https://github.com/yourusername/ChechyLegis',
    'default_dir_name': f'{{autopf}}\\{APP_NAME}',
    'default_group_name': APP_NAME,
    'output_dir': 'installers',
    'output_base_filename': f'{APP_NAME}_Setup_v{APP_VERSION}',
    'compression': 'lzma2',
    'solid_compression': True,
}

def get_version():
    """Retorna la versión de la aplicación"""
    return APP_VERSION

def get_app_info():
    """Retorna información completa de la aplicación"""
    return {
        'name': APP_NAME,
        'version': APP_VERSION,
        'description': APP_DESCRIPTION,
        'author': APP_AUTHOR,
    }
