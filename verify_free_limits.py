import requests
import time
import subprocess
import os
import signal
import sys

def test_limits():
    print("=== INICIANDO VERIFICACIÓN DE LÍMITES (FREE EDITION) ===")
    
    # Iniciar servidor en segundo plano
    print("[1/4] Iniciando servidor de prueba...")
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8008"], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3) # Esperar a que inicie
    
    base_url = "http://127.0.0.1:8008/api"
    headers = {"X-User-Role": "admin", "X-User-Name": "Tester"}

    try:
        # 1. Probar límite de 3 casos
        print("[2/4] Probando límite de 3 casos...")
        for i in range(4):
            res = requests.post(f"{base_url}/procesos", json={
                "numero_proceso": f"TEST-2026-{i}",
                "fecha_radicacion": "2026-02-03",
                "estado": "ACTIVO",
                "partes": "Tester vs Machine"
            }, headers=headers)
            
            if i < 3:
                if res.status_code == 200:
                    print(f"   ✅ Caso {i+1} creado ok")
                else:
                    print(f"   ❌ Error al crear caso {i+1}: {res.text}")
            else:
                if res.status_code == 403:
                    print(f"   ✅ Límite de 3 casos bloqueado correctamente (403 Forbidden)")
                else:
                    print(f"   ❌ ERROR: El 4to caso NO fue bloqueado (Status: {res.status_code})")

        # 2. Probar bloqueo de CRM
        print("[3/4] Probando bloqueo de CRM...")
        res_crm = requests.post(f"{base_url}/support/ticket", json={
            "subject": "Test Issue",
            "description": "This should be blocked",
            "priority": "low"
        }, headers=headers)
        
        if res_crm.status_code == 403:
            print("   ✅ CRM bloqueado correctamente en versión FREE")
        else:
            print(f"   ❌ ERROR: CRM no bloqueado (Status: {res_crm.status_code})")

        # 3. Verificar disclaimer en metadata/UI (vía health o similar)
        print("[4/4] Verificando salud del sistema...")
        res_health = requests.get(f"{base_url}/health")
        if res_health.status_code == 200:
            print("   ✅ Sistema saludable")

    finally:
        print("=== VERIFICACIÓN FINALIZADA ===")
        # Terminar servidor
        if os.name == 'nt':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
        else:
            process.terminate()

if __name__ == "__main__":
    test_limits()
