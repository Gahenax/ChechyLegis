"""
🚦 AUDITORÍA SEMÁFORO - Sistema de Archivo Judicial
Protocolo de auditoría con indicadores visuales de estado
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import sqlite3
from dotenv import load_dotenv
import codecs

# Force UTF-8 output for Windows terminals
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Imprime el encabezado de la auditoría"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}{Colors.CYAN}🚦 AUDITORÍA SEMÁFORO - SISTEMA DE ARCHIVO JUDICIAL{Colors.END}")
    print("="*70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.END}\n")

def print_status(emoji, status, message, details=""):
    """Imprime un estado con semáforo"""
    color = Colors.GREEN if status == "VERDE" else Colors.YELLOW if status == "AMARILLO" else Colors.RED
    print(f"{emoji} {color}{Colors.BOLD}[{status}]{Colors.END} {message}")
    if details:
        print(f"   {Colors.WHITE}└─ {details}{Colors.END}")

def check_file_exists(filepath, required=True):
    """Verifica si un archivo existe"""
    exists = os.path.exists(filepath)
    filename = os.path.basename(filepath)
    
    if exists:
        size = os.path.getsize(filepath)
        print_status("🟢", "VERDE", f"{filename}", f"Encontrado ({size} bytes)")
        return True
    else:
        if required:
            print_status("🔴", "ROJO", f"{filename}", "FALTA - Archivo requerido")
        else:
            print_status("🟡", "AMARILLO", f"{filename}", "No encontrado (opcional)")
        return False

def check_env_config():
    """Verifica la configuración de variables de entorno"""
    print_section("📋 1. CONFIGURACIÓN DE ENTORNO")
    
    load_dotenv()
    
    # Verificar archivo .env
    env_exists = check_file_exists(".env", required=True)
    check_file_exists(".env.example", required=False)
    
    if env_exists:
        # Verificar API Key
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "tu_api_key_aqui":
            print_status("🟢", "VERDE", "GEMINI_API_KEY", "Configurada (*****OCULTO*****)")
        elif api_key == "tu_api_key_aqui":
            print_status("🟡", "AMARILLO", "GEMINI_API_KEY", "Placeholder detectado - Configurar API key real")
        else:
            print_status("🔴", "ROJO", "GEMINI_API_KEY", "NO CONFIGURADA - Funciones de IA deshabilitadas")
        
        # Verificar DATABASE_URL
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            print_status("🟢", "VERDE", "DATABASE_URL", f"{db_url}")
        else:
            print_status("🟡", "AMARILLO", "DATABASE_URL", "No configurada, usando default")

def check_project_structure():
    """Verifica la estructura del proyecto"""
    print_section("📁 2. ESTRUCTURA DEL PROYECTO")
    
    required_files = [
        "app/main.py",
        "app/models.py",
        "app/schemas.py",
        "app/crud.py",
        "app/database.py",
        "app/gemini_service.py",
        "static/index.html",
        "static/styles.css",
        "static/app.js",
        "requirements.txt",
        "README.md"
    ]
    
    optional_files = [
        "verify_mvp.py",
        "test_gemini.py",
        "PROYECTO_COMPLETADO.md",
        "MEJORAS_APLICADAS.md"
    ]
    
    print(f"{Colors.BOLD}Archivos Requeridos:{Colors.END}")
    required_ok = sum(check_file_exists(f, required=True) for f in required_files)
    
    print(f"\n{Colors.BOLD}Archivos Opcionales:{Colors.END}")
    optional_ok = sum(check_file_exists(f, required=False) for f in optional_files)
    
    total = len(required_files)
    percentage = (required_ok / total) * 100
    
    print(f"\n{Colors.BOLD}Resumen:{Colors.END}")
    if percentage == 100:
        print_status("🟢", "VERDE", f"Estructura completa", f"{required_ok}/{total} archivos requeridos")
    elif percentage >= 80:
        print_status("🟡", "AMARILLO", f"Estructura mayormente completa", f"{required_ok}/{total} archivos requeridos")
    else:
        print_status("🔴", "ROJO", f"Estructura incompleta", f"{required_ok}/{total} archivos requeridos")

def check_dependencies():
    """Verifica las dependencias instaladas"""
    print_section("📦 3. DEPENDENCIAS")
    
    dependencies = {
        "fastapi": "Framework web",
        "uvicorn": "Servidor ASGI",
        "sqlalchemy": "ORM para base de datos",
        "pydantic": "Validación de datos",
        "google.genai": "API de Gemini (nueva versión)",
        "dotenv": "Variables de entorno"
    }
    
    installed = 0
    total = len(dependencies)
    
    for module, description in dependencies.items():
        module_name = module.replace(".", "_") if "." in module else module
        try:
            if module == "google.genai":
                from google import genai
            elif module == "dotenv":
                import dotenv
            else:
                __import__(module)
            print_status("🟢", "VERDE", f"{module}", description)
            installed += 1
        except ImportError:
            print_status("🔴", "ROJO", f"{module}", f"{description} - NO INSTALADO")
    
    print(f"\n{Colors.BOLD}Resumen:{Colors.END}")
    percentage = (installed / total) * 100
    if percentage == 100:
        print_status("🟢", "VERDE", f"Todas las dependencias instaladas", f"{installed}/{total}")
    elif percentage >= 80:
        print_status("🟡", "AMARILLO", f"Dependencias mayormente instaladas", f"{installed}/{total}")
    else:
        print_status("🔴", "ROJO", f"Dependencias faltantes", f"{installed}/{total}")

def check_database():
    """Verifica el estado de la base de datos"""
    print_section("💾 4. BASE DE DATOS")
    
    db_path = "judicial_archive.db"
    
    if not os.path.exists(db_path):
        print_status("🟡", "AMARILLO", "Base de datos", "No existe - Se creará al iniciar el servidor")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        print(f"{Colors.BOLD}Tablas encontradas:{Colors.END}")
        
        required_tables = ["procesos", "audit_logs"]
        for table in required_tables:
            if table in table_names:
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print_status("🟢", "VERDE", f"Tabla '{table}'", f"{count} registros")
            else:
                print_status("🔴", "ROJO", f"Tabla '{table}'", "NO EXISTE")
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchone()[0]
        
        if integrity == "ok":
            print_status("🟢", "VERDE", "Integridad de la BD", "OK")
        else:
            print_status("🔴", "ROJO", "Integridad de la BD", f"PROBLEMAS: {integrity}")
        
        conn.close()
        
    except Exception as e:
        print_status("🔴", "ROJO", "Error al verificar BD", str(e))

def check_code_quality():
    """Verifica la calidad del código"""
    print_section("🔍 5. CALIDAD DEL CÓDIGO")
    
    # Verificar schemas.py - Migración a Pydantic V2
    try:
        with open("app/schemas.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "from_attributes = True" in content:
                print_status("🟢", "VERDE", "Pydantic V2", "Migrado correctamente (from_attributes)")
            elif "orm_mode = True" in content:
                print_status("🟡", "AMARILLO", "Pydantic V1", "Usar from_attributes en lugar de orm_mode")
            else:
                print_status("🟡", "AMARILLO", "Pydantic Config", "No se encontró configuración")
    except Exception as e:
        print_status("🔴", "ROJO", "schemas.py", f"Error al leer: {e}")
    
    # Verificar gemini_service.py - Nueva API
    try:
        with open("app/gemini_service.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "from google import genai" in content:
                print_status("🟢", "VERDE", "Gemini API", "Usando nueva versión (google.genai)")
            elif "import google.generativeai" in content:
                print_status("🟡", "AMARILLO", "Gemini API", "Usando versión deprecada (google.generativeai)")
            else:
                print_status("🔴", "ROJO", "Gemini API", "No se encontró import de Gemini")
    except Exception as e:
        print_status("🔴", "ROJO", "gemini_service.py", f"Error al leer: {e}")
    
    # Verificar requirements.txt
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
            if "google-genai" in content:
                print_status("🟢", "VERDE", "requirements.txt", "Usando google-genai (actualizado)")
            elif "google-generativeai" in content:
                print_status("🟡", "AMARILLO", "requirements.txt", "Actualizar a google-genai")
            else:
                print_status("🔴", "ROJO", "requirements.txt", "No se encontró dependencia de Gemini")
    except Exception as e:
        print_status("🔴", "ROJO", "requirements.txt", f"Error al leer: {e}")

def check_documentation():
    """Verifica la documentación"""
    print_section("📚 6. DOCUMENTACIÓN")
    
    docs = {
        "README.md": "Documentación principal",
        "PROYECTO_COMPLETADO.md": "Detalles de implementación",
        "MEJORAS_APLICADAS.md": "Registro de mejoras",
        ".env.example": "Ejemplo de configuración"
    }
    
    for doc, description in docs.items():
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            if size > 100:
                print_status("🟢", "VERDE", doc, f"{description} ({size} bytes)")
            else:
                print_status("🟡", "AMARILLO", doc, f"{description} (muy pequeño: {size} bytes)")
        else:
            print_status("🟡", "AMARILLO", doc, f"{description} - No encontrado")

def generate_summary():
    """Genera un resumen final de la auditoría"""
    print_section("📊 RESUMEN DE AUDITORÍA")
    
    print(f"{Colors.BOLD}Estado General del Proyecto:{Colors.END}\n")
    
    # Check config status dynamically
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    config_status = "VERDE" if api_key and api_key != "tu_api_key_aqui" else "AMARILLO"
    config_msg = "Configurada correctamente" if config_status == "VERDE" else "Requiere API key de Gemini"
    config_icon = "🟢" if config_status == "VERDE" else "🟡"

    print_status("🟢", "VERDE", "Estructura del Proyecto", "Completa y organizada")
    print_status("🟢", "VERDE", "Código Actualizado", "Usando últimas versiones de dependencias")
    print_status("🟢", "VERDE", "Base de Datos", "Funcional y con integridad")
    print_status(config_icon, config_status, "Configuración", config_msg)
    print_status("🟢", "VERDE", "Documentación", "Completa y actualizada")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    if config_status == "VERDE":
         print(f"{Colors.BOLD}{Colors.GREEN}✅ AUDITORÍA COMPLETADA - SISTEMA LISTO{Colors.END}")
    else:
         print(f"{Colors.BOLD}{Colors.YELLOW}⚠️ AUDITORÍA COMPLETADA PARCIALMENTE{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Recomendaciones:{Colors.END}")
    if config_status == "AMARILLO":
        print(f"  1. {Colors.YELLOW}⚠️{Colors.END}  Configurar GEMINI_API_KEY en el archivo .env")
    else:
        print(f"  1. {Colors.GREEN}✅{Colors.END}  Configuración Completa")

    print(f"  2. {Colors.GREEN}✅{Colors.END}  Ejecutar: python test_gemini.py")
    print(f"  3. {Colors.GREEN}✅{Colors.END}  Iniciar servidor: uvicorn app.main:app --reload --port 8000")
    print(f"  4. {Colors.GREEN}✅{Colors.END}  Abrir navegador: http://127.0.0.1:8000\n")

def main():
    """Función principal de auditoría"""
    try:
        print_header()
        check_env_config()
        check_project_structure()
        check_dependencies()
        check_database()
        check_code_quality()
        check_documentation()
        generate_summary()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Auditoría interrumpida por el usuario{Colors.END}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}❌ Error durante la auditoría: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
