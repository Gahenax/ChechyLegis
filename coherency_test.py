import sys
import os
import re
import codecs
from fastapi.testclient import TestClient
from app.main import app

# Force UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

client = TestClient(app)

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧩 {title}")
    print(f"{'='*60}")

def print_result(name, passed, detail=""):
    icon = "✅" if passed else "❌"
    print(f"{icon} {name}")
    if detail:
        print(f"   └─ {detail}")

def check_endpoint_consistency():
    print_header("CONSISTENCIA ENDPOINTS (Frontend vs Backend)")
    
    # 1. Extraer rutas del Backend
    backend_routes = set()
    for route in app.routes:
        if hasattr(route, "path"):
            backend_routes.add(route.path)
            
    # 2. Extraer rutas llamads en Frontend (app.js)
    frontend_routes = set()
    try:
        with open("static/app.js", "r", encoding="utf-8") as f:
            content = f.read()
            # Buscar llamadas a apiCall('/ruta'...) o fetch(`${API_BASE}/ruta`...)
            # Simplificación: buscar strings que empiecen por / y parezcan rutas API
            matches = re.findall(r"apiCall\(['\"]([^'\"]+)['\"]", content)
            for m in matches:
                # Normalizar: /procesos?query -> /procesos
                clean_route = "/api" + m.split('?')[0]
                frontend_routes.add(clean_route)
    except Exception as e:
        print_result("Lectura de app.js", False, str(e))
        return

    # 3. Comparar
    print_result(f"Rutas Backend detectadas: {len(backend_routes)}", True)
    print_result(f"Rutas Frontend detectadas: {len(frontend_routes)}", True)
    
    warnings = 0
    for f_route in frontend_routes:
        # Manejo de parámetros de ruta (ej: /procesos/123 -> /procesos/{proceso_id})
        # Esta es una heurística simple
        matched = False
        for b_route in backend_routes:
            # Convertir {param} a regex simple
            b_regex = re.sub(r"\{[^}]+\}", "[^/]+", b_route)
            if re.fullmatch(b_regex, f_route):
                matched = True
                break
        
        if not matched:
            print_result(f"Ruta Frontend '{f_route}'", False, "No coincide con ninguna ruta Backend explícita")
            warnings += 1
        else:
            # print_result(f"Ruta Frontend '{f_route}'", True, "Confirmada en Backend")
            pass
            
    if warnings == 0:
        print_result("Coherencia Frontend-Backend", True, "Todas las llamadas del frontend tienen endpoint correspondiente")

def functional_crud_test():
    print_header("PRUEBA FUNCIONAL CRUD (Simulación Cliente)")
    
    headers = {"X-User-Role": "admin", "X-User-Name": "CoherenceBot"}
    
    # 1. CREATE
    payload = {
        "numero_proceso": "COHERENCE-TEST-001",
        "fecha_radicacion": "2024-12-01",
        "estado": "ACTIVO",
        "partes": "Test System vs Bug",
        "clase_proceso": "Automated",
        "cuantia_tipo": "MINIMA"
    }
    
    try:
        response = client.post("/api/procesos", json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            pid = data["id"]
            print_result("CREATE Proceso", True, f"ID: {pid}")
            
            # 2. READ
            r2 = client.get(f"/api/procesos/{pid}", headers=headers)
            print_result("READ Proceso", r2.status_code == 200, f"Status: {r2.status_code}")
            
            # 3. UPDATE
            r3 = client.put(f"/api/procesos/{pid}", json={"estado": "TERMINADO"}, headers=headers)
            print_result("UPDATE Proceso", r3.status_code == 200, f"Nuevo estado: TERMINADO")
            
            # 4. DELETE
            r4 = client.delete(f"/api/procesos/{pid}", headers=headers)
            print_result("DELETE Proceso", r4.status_code == 200, "Soft delete ejecutado")
            
        else:
            print_result("CREATE Proceso", False, f"Error {response.status_code}: {response.text}")

    except Exception as e:
        print_result("Error Crítico CRUD", False, str(e))

def gemini_integration_check():
    print_header("VERIFICACIÓN INTEGRACIÓN GEMINI")
    
    api_key = os.getenv("GEMINI_API_KEY")
    has_key = bool(api_key and api_key != "tu_api_key_aqui")
    
    print_result("Variable GEMINI_API_KEY", has_key)
    
    if not has_key:
        print("   ⚠️  Saltando pruebas de conexión real (Falta API Key)")
        return

    # Intentar instanciar servicio (sin hacer llamada real para no gastar quota/tiempo excesivo si no se pide)
    try:
        from app.gemini_service import GeminiService
        service = GeminiService(api_key)
        print_result("Inicialización GeminiService", True, "Clase instanciada correctamente")
    except Exception as e:
        print_result("Inicialización GeminiService", False, str(e))

def main():
    print("\n🚀 INICIANDO PRUEBAS DE COHERENCIA SISTÉMICA")
    check_endpoint_consistency()
    functional_crud_test()
    gemini_integration_check()
    print("\n✅ PRUEBAS FINALIZADAS\n")

if __name__ == "__main__":
    main()
