import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Force UTF-8 for console output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def launch_component(name, command, cwd=None):
    print(f"🛎️  Iniciando {name}...")
    return subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=True
    )

def main():
    app_dir = Path(__file__).parent
    os.chdir(app_dir)

    print("=" * 60)
    print("  🏨 GAHENAX HOTEL - MASTER ECOSYSTEM CONTROL")
    print("=" * 60)
    print()

    # 1. Iniciar LA OFICINA (Gahenax CRM)
    office_cmd = f"{sys.executable} -m uvicorn office.main:app --host 127.0.0.1 --port 5000"
    office_proc = launch_component("LA OFICINA (Gahenax CRM)", office_cmd)

    # 2. Iniciar EL LOBBY & HABITACIONES (FastAPI Server)
    app_cmd = f"{sys.executable} -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
    app_proc = launch_component("EL LOBBY & HABITACIONES", app_cmd)

    # 3. Iniciar JULES (Background Worker)
    jules_cmd = f"{sys.executable} jules_worker.py"
    jules_proc = launch_component("JULES WORKER", jules_cmd)

    print()
    print("⏳ Sincronizando ecosistema...")
    time.sleep(3)

    print()
    print("✅ Ecosistema GAHENAX activo!")
    print("📍 Lobby: http://127.0.0.1:8000/lobby")
    print("📍 Oficina (API): http://127.0.0.1:5000")
    print()
    
    # Abrir el Lobby automáticamente
    webbrowser.open("http://127.0.0.1:8000/lobby")

    print("=" * 60)
    print("Presiona Ctrl+C para apagar el Hotel...")
    print("=" * 60)

    try:
        while True:
            # Mantener vivo y monitorear (opcional)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Apagando el Hotel...")
        office_proc.terminate()
        app_proc.terminate()
        jules_proc.terminate()
        print("✅ Ecosistema detenido correctamente.")

if __name__ == "__main__":
    main()
