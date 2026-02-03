
import requests
import sys
import os
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOG_FILE = "bug_scan_report.txt"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(message, type="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = Colors.GREEN if type == "PASS" else Colors.RED if type == "FAIL" else Colors.CYAN
    print(f"{Colors.BOLD}[{timestamp}]{Colors.END} {color}[{type}]{Colors.END} {message}")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{type}] {message}\n")

def check_server_health():
    log("Verificando estado del servidor...", "INFO")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            log("Servidor accesible y respondiendo 200 OK", "PASS")
            return True
        else:
            log(f"Servidor respondió con código {response.status_code}", "FAIL")
            return False
    except requests.ConnectionError:
        log("No se pudo conectar al servidor. ¿Está corriendo en puerto 8000?", "FAIL")
        return False

def test_crud_flow():
    log("Iniciando prueba de flujo CRUD...", "INFO")
    
    # 1. Crear
    test_proceso = {
        "numero_proceso": f"TEST-{int(time.time())}",
        "estado": "ACTIVO",
        "partes": "Test User vs System Bug",
        "clase_proceso": "Auditoria",
        "fecha_radicacion": datetime.now().strftime("%Y-%m-%d"),
        "cuantia_tipo": "MENOR",
        "observaciones": "Proceso de prueba automática"
    }
    
    proceso_id = None
    
    try:
        # CREATE
        log(f"Creando proceso de prueba: {test_proceso['numero_proceso']}", "INFO")
        create_res = requests.post(f"{BASE_URL}/api/procesos", json=test_proceso)
        
        if create_res.status_code == 200:
            data = create_res.json()
            proceso_id = data['id']
            log(f"Proceso creado exitosamente. ID: {proceso_id}", "PASS")
        else:
            log(f"Fallo al crear proceso: {create_res.text}", "FAIL")
            return

        # READ
        log(f"Leyendo proceso ID: {proceso_id}", "INFO")
        get_res = requests.get(f"{BASE_URL}/api/procesos/{proceso_id}")
        if get_res.status_code == 200 and get_res.json()['numero_proceso'] == test_proceso['numero_proceso']:
             log("Lectura de proceso correcta", "PASS")
        else:
             log("Fallo al leer proceso", "FAIL")

        # UPDATE
        log(f"Actualizando proceso ID: {proceso_id}", "INFO")
        update_data = {"estado": "TERMINADO", "observaciones": "Actualizado por scanner"}
        put_res = requests.put(f"{BASE_URL}/api/procesos/{proceso_id}", json=update_data)
        if put_res.status_code == 200 and put_res.json()['estado'] == "TERMINADO":
            log("Actualización correcta", "PASS")
        else:
            log("Fallo al actualizar proceso", "FAIL")

        # AI ANALYSIS CHECK (Si está disponible)
        log("Probando endpoint de Análisis IA...", "INFO")
        # Nota: Esto consume cuota de API, hacerlo solo si es necesario. Lo haremos ligero.
        ai_res = requests.get(f"{BASE_URL}/api/ai/analyze/{proceso_id}")
        if ai_res.status_code == 200:
            log("Endpoint de IA respondió correctamente", "PASS")
        else:
            # Puede fallar si la API key no es válida o hay errores de red
            log(f"Endpoint de IA reportó error (puede ser config): {ai_res.status_code}", "WARN")

        # DELETE
        log(f"Eliminando proceso ID: {proceso_id}", "INFO")
        del_res = requests.delete(f"{BASE_URL}/api/procesos/{proceso_id}")
        if del_res.status_code == 200:
            log("Eliminación correcta (Soft Delete)", "PASS")
        else:
            log("Fallo al eliminar proceso", "FAIL")

    except Exception as e:
        log(f"Excepción durante pruebas CRUD: {str(e)}", "FAIL")

def scan_code_quality():
    log("Escaneando calidad de código estática...", "INFO")
    
    issues_found = 0
    
    for root, dirs, files in os.walk("."):
        if "env" in root or "__pycache__" in root or ".git" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if "print(" in line and "#" not in line:
                                # Ignoramos scripts de CLI que usan print
                                if file not in ["auditoria_semaforo.py", "test_gemini.py", "list_models.py", "full_scan.py", "verify_mvp.py"]:
                                    log(f"Posible 'print' olvidado en {file}:{i+1}", "WARN")
                                    issues_found += 1
                            if "TODO" in line:
                                log(f"TODO pendiente en {file}:{i+1}: {line.strip()}", "INFO")
                            if "FIXME" in line:
                                log(f"FIXME crítico en {file}:{i+1}: {line.strip()}", "WARN")
                                issues_found += 1
                except Exception:
                    pass
    
    if issues_found == 0:
        log("No se encontraron problemas evidentes de código (prints olvidados, FIXMEs)", "PASS")
    else:
        log(f"Se encontraron {issues_found} puntos de atención en el código", "WARN")

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}🔍 INICIANDO ESCANEO COMPLETO DE BUGS Y OPTIMIZACIÓN{Colors.END}\n")
    
    # Limpiar log anterior
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    if check_server_health():
        test_crud_flow()
    else:
        log("Saltando pruebas funcionales porque el servidor no responde", "warn")
        
    scan_code_quality()
    
    print(f"\n{Colors.BOLD}📋 Escaneo finalizado. Reporte guardado en {LOG_FILE}{Colors.END}\n")
