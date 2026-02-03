"""
ChechyLegis - Launcher
Inicia el servidor del Archivo Virtual de Procesos Judiciales
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    # Obtener el directorio del script
    if getattr(sys, 'frozen', False):
        # Si está ejecutándose como .exe
        app_dir = Path(sys.executable).parent
    else:
        # Si está ejecutándose como .py
        app_dir = Path(__file__).parent
    
    os.chdir(app_dir)
    
    print("=" * 60)
    print("  CHECHYLEGIS - ARCHIVO VIRTUAL DE PROCESOS JUDICIALES")
    print("=" * 60)
    print()
    print("🏛️  Iniciando servidor...")
    print()
    
    # Verificar que existe la carpeta app
    if not (app_dir / "app").exists():
        print("❌ Error: No se encuentra la carpeta 'app'")
        print(f"   Directorio actual: {app_dir}")
        input("\nPresiona Enter para salir...")
        return
    
    # Verificar archivo .env
    env_file = app_dir / ".env"
    if not env_file.exists():
        print("⚠️  Advertencia: No se encuentra el archivo .env")
        print("   Las funciones de IA no estarán disponibles.")
        print("   Crea un archivo .env con tu GEMINI_API_KEY")
        print()
    
    try:
        # Iniciar el servidor
        print("🚀 Iniciando servidor FastAPI...")
        print("📍 URL: http://127.0.0.1:8000")
        print()
        print("⏳ Esperando que el servidor esté listo...")
        
        # Iniciar uvicorn
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Esperar a que el servidor esté listo
        server_ready = False
        for line in process.stdout:
            print(line, end='')
            if "Application startup complete" in line or "Uvicorn running" in line:
                server_ready = True
                break
        
        if server_ready:
            print()
            print("✅ Servidor iniciado correctamente!")
            print()
            print("🌐 Abriendo navegador...")
            time.sleep(1)
            webbrowser.open("http://127.0.0.1:8000")
            print()
            print("=" * 60)
            print("  SERVIDOR ACTIVO")
            print("=" * 60)
            print()
            print("📌 Para detener el servidor: Cierra esta ventana o presiona Ctrl+C")
            print()
            
            # Mantener el proceso corriendo
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Deteniendo servidor...")
                process.terminate()
                process.wait()
                print("✅ Servidor detenido correctamente")
        else:
            print("❌ Error: El servidor no pudo iniciarse correctamente")
            input("\nPresiona Enter para salir...")
            
    except FileNotFoundError:
        print("❌ Error: No se encontró uvicorn")
        print("   Instala las dependencias con: pip install -r requirements.txt")
        input("\nPresiona Enter para salir...")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
