"""
Script de Verificación Pre-Build
Verifica que todo esté listo para empaquetar
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Verifica si un archivo existe"""
    exists = os.path.exists(filepath)
    status = "[OK]" if exists else ("[ERROR]" if required else "[WARN]")
    print(f"{status} {filepath}")
    return exists

def check_directory_exists(dirpath, required=True):
    """Verifica si un directorio existe"""
    exists = os.path.isdir(dirpath)
    status = "[OK]" if exists else ("[ERROR]" if required else "[WARN]")
    print(f"{status} {dirpath}/")
    return exists

def main():
    print("\n" + "="*60)
    print("  ChechyLegis - Verificación Pre-Build")
    print("="*60 + "\n")
    
    errors = []
    warnings = []
    
    # Verificar archivos principales
    print("[*] Archivos Principales:")
    if not check_file_exists("launcher.py"):
        errors.append("launcher.py no encontrado")
    if not check_file_exists("requirements.txt"):
        errors.append("requirements.txt no encontrado")
    if not check_file_exists(".env.example"):
        errors.append(".env.example no encontrado")
    if not check_file_exists("README.md"):
        warnings.append("README.md no encontrado")
    
    print("\n[*] Archivos de Empaquetado:")
    if not check_file_exists("ChechyLegis.spec"):
        errors.append("ChechyLegis.spec no encontrado")
    if not check_file_exists("installer.iss"):
        errors.append("installer.iss no encontrado")
    if not check_file_exists("build_config.py"):
        errors.append("build_config.py no encontrado")
    
    print("\n[*] Recursos:")
    if not check_file_exists("icon.ico"):
        errors.append("icon.ico no encontrado")
    if not check_file_exists("icon.png", required=False):
        warnings.append("icon.png no encontrado")
    
    print("\n[*] Documentacion:")
    check_file_exists("LICENSE.txt", required=False)
    check_file_exists("INSTALACION_INFO.txt", required=False)
    check_file_exists("EMPAQUETADO.md", required=False)
    
    print("\n[*] Directorios:")
    if not check_directory_exists("app"):
        errors.append("Directorio app/ no encontrado")
    if not check_directory_exists("static"):
        errors.append("Directorio static/ no encontrado")
    
    print("\n[*] Archivos de Backend (app/):")
    backend_files = [
        "app/__init__.py",
        "app/main.py",
        "app/models.py",
        "app/schemas.py",
        "app/crud.py",
        "app/database.py",
        "app/gemini_service.py",
    ]
    for f in backend_files:
        if not check_file_exists(f):
            errors.append(f"{f} no encontrado")
    
    print("\n[*] Archivos de Frontend (static/):")
    frontend_files = [
        "static/index.html",
        "static/styles.css",
        "static/app.js",
    ]
    for f in frontend_files:
        if not check_file_exists(f):
            errors.append(f"{f} no encontrado")
    
    print("\n[*] Scripts de Build:")
    check_file_exists("build_exe.bat")
    check_file_exists("build_installer.bat")
    check_file_exists("build_all.bat")
    
    # Verificar dependencias de Python
    print("\n[*] Verificando Dependencias de Python:")
    try:
        import fastapi
        print("[OK] fastapi")
    except ImportError:
        errors.append("fastapi no instalado")
        print("[ERROR] fastapi")
    
    try:
        import uvicorn
        print("[OK] uvicorn")
    except ImportError:
        errors.append("uvicorn no instalado")
        print("[ERROR] uvicorn")
    
    try:
        import sqlalchemy
        print("[OK] sqlalchemy")
    except ImportError:
        errors.append("sqlalchemy no instalado")
        print("[ERROR] sqlalchemy")
    
    try:
        import google.generativeai
        print("[OK] google-genai")
    except ImportError:
        errors.append("google-genai no instalado")
        print("[ERROR] google-genai")
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print("[OK] PyInstaller")
    except ImportError:
        warnings.append("PyInstaller no instalado (se instalara automaticamente)")
        print("[WARN] PyInstaller (se instalara automaticamente)")
    
    # Resumen
    print("\n" + "="*60)
    print("  RESUMEN")
    print("="*60)
    
    if errors:
        print(f"\n[ERROR] ERRORES CRITICOS ({len(errors)}):")
        for error in errors:
            print(f"   - {error}")
    
    if warnings:
        print(f"\n[WARN] ADVERTENCIAS ({len(warnings)}):")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not errors and not warnings:
        print("\n[OK] TODO LISTO PARA EMPAQUETAR!")
        print("\nProximos pasos:")
        print("  1. Ejecutar: build_all.bat")
        print("  2. O ejecutar paso a paso:")
        print("     - build_exe.bat")
        print("     - build_installer.bat")
    elif not errors:
        print("\n[OK] LISTO PARA EMPAQUETAR (con advertencias menores)")
        print("\nPuedes proceder con: build_all.bat")
    else:
        print("\n[ERROR] NO LISTO PARA EMPAQUETAR")
        print("\nPor favor corrige los errores antes de continuar.")
        return 1
    
    print("\n" + "="*60 + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
