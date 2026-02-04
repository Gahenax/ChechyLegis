"""
Script de Verificación del MVP - Archivo Virtual de Procesos Judiciales
Verifica todos los criterios obligatorios definidos en la Fase 1
"""

import requests
import json
from datetime import date, datetime, timedelta

BASE_URL = "http://127.0.0.1:8001/api"

def print_test(name, passed, details=""):
    icon = "[OK]" if passed else "[FAIL]"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")
    print()

def clean_all_processes():
    """🗑️ Limpiar todos los procesos (requiere Rol Admin)"""
    print("   [CLEANUP] Eliminando procesos existentes para pruebas...")
    headers = {
        "Authorization": "Bearer admin-token",
        "X-User-Name": "admin_cleanup", 
        "X-User-Role": "admin"
    }
    
    # 1. Listar
    try:
        r = requests.get(f"{BASE_URL}/procesos", headers=headers)
        if r.status_code != 200:
            return
        items = r.json()
        
        # 2. Eliminar cada uno
        for item in items:
            pid = item["id"]
            requests.delete(f"{BASE_URL}/procesos/{pid}", headers=headers)
        
        print(f"   [CLEANUP] {len(items)} procesos eliminados.")
    except Exception as e:
        print(f"   [CLEANUP] Error: {e}")


def test_1_create_valid_proceso():
    """✅ Crear proceso válido -> aparece en listado"""
    print("=" * 60)
    print("TEST 1: Crear proceso válido")
    print("=" * 60)
    
    headers = {
        "Authorization": "Bearer operator-token",
        "X-User-Name": "test_user"
    }
    
    proceso_data = {
        "numero_proceso": "2024-TEST-001",
        "fecha_radicacion": datetime.now().strftime("%Y-%m-%d"),
        "estado": "ACTIVO",
        "partes": "Juan Pérez vs María García",
        "clase_proceso": "Civil",
        "cuantia_tipo": "MENOR"
    }
    
    # Crear proceso
    response = requests.post(f"{BASE_URL}/procesos", json=proceso_data, headers=headers)
    
    if response.status_code == 200:
        created = response.json()
        proceso_id = created["id"]
        
        # Verificar que aparece en el listado
        list_response = requests.get(f"{BASE_URL}/procesos", headers=headers)
        procesos = list_response.json()
        
        found = any(p["numero_proceso"] == "2024-TEST-001" for p in procesos)
        print_test("Crear proceso válido y aparece en listado", found, 
                   f"ID creado: {proceso_id}, Total procesos: {len(procesos)}")
        return proceso_id
    else:
        print_test("Crear proceso válido", False, f"Error: {response.status_code} - {response.text}")
        return None

def test_2_create_invalid_proceso():
    """❌ Crear proceso sin numero_proceso -> error controlado (400)"""
    print("=" * 60)
    print("TEST 2: Validación de campos obligatorios")
    print("=" * 60)
    
    headers = {
        "Authorization": "Bearer operator-token",
        "X-User-Name": "test_user"
    }
    
    # Intentar crear sin numero_proceso
    invalid_data = {
        "fecha_radicacion": datetime.now().strftime("%Y-%m-%d"),
        "estado": "ACTIVO",
        "partes": "Test vs Test"
    }
    
    response = requests.post(f"{BASE_URL}/procesos", json=invalid_data, headers=headers)
    
    is_400 = response.status_code == 422 or response.status_code == 400
    has_message = "detail" in response.json() if response.text else False
    
    print_test("Rechaza proceso sin numero_proceso con error 400/422", is_400,
               f"Status: {response.status_code}, Mensaje: {response.json().get('detail', 'N/A')}")

def test_3_filter_functionality():
    """🔍 Filtro por estado y rango de fechas funciona correctamente"""
    print("=" * 60)
    print("TEST 3: Filtros de búsqueda")
    print("=" * 60)
    
    headers = {
        "Authorization": "Bearer viewer-token",
        "X-User-Name": "test_user"
    }
    
    # Crear procesos de prueba con diferentes estados y fechas
    today = datetime.now()
    d1 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    d2 = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    d3 = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    
    test_procesos = [
        {"numero_proceso": "2024-FILTER-001", "fecha_radicacion": d1, "estado": "ACTIVO", "partes": "A vs B"},
        {"numero_proceso": "2024-FILTER-002", "fecha_radicacion": d2, "estado": "TERMINADO", "partes": "C vs D"},
        {"numero_proceso": "2024-FILTER-003", "fecha_radicacion": d3, "estado": "ACTIVO", "partes": "E vs F"},
    ]
    
    operator_headers = {"Authorization": "Bearer operator-token", "X-User-Name": "test_user"}
    for p in test_procesos:
        requests.post(f"{BASE_URL}/procesos", json=p, headers=operator_headers)
    
    # Test filtro por estado
    response = requests.get(f"{BASE_URL}/procesos?estado=ACTIVO", headers=headers)
    activos = response.json()
    activos_count = sum(1 for p in activos if p["estado"] == "ACTIVO")
    
    # Test filtro por rango de fechas
    # Ajustamos el rango para incluir hoy y los ultimos dias
    f_start = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    f_end = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/procesos?fecha_desde={f_start}&fecha_hasta={f_end}", headers=headers)
    filtered = response.json()
    
    print_test("Filtro por estado funciona", activos_count >= 2, 
               f"Procesos ACTIVO encontrados: {activos_count}")
    print_test("Filtro por rango de fechas funciona", len(filtered) >= 2,
               f"Procesos en rango encontrados: {len(filtered)}")

def test_4_audit_trail():
    """🧾 Editar proceso -> cada campo editado genera registro en audit_log"""
    print("=" * 60)
    print("TEST 4: Auditoría de cambios")
    print("=" * 60)
    
    headers = {
        "Authorization": "Bearer operator-token",
        "X-User-Name": "audit_tester"
    }
    
    # Crear proceso
    proceso_data = {
        "numero_proceso": "2024-AUDIT-001",
        "fecha_radicacion": datetime.now().strftime("%Y-%m-%d"),
        "estado": "ACTIVO",
        "partes": "Original vs Original"
    }
    
    create_response = requests.post(f"{BASE_URL}/procesos", json=proceso_data, headers=headers)
    proceso_id = create_response.json()["id"]
    
    # Editar múltiples campos
    update_data = {
        "estado": "TERMINADO",
        "partes": "Modificado vs Modificado"
    }
    
    requests.put(f"{BASE_URL}/procesos/{proceso_id}", json=update_data, headers=headers)
    
    # Obtener detalle con audit trail
    detail_response = requests.get(f"{BASE_URL}/procesos/{proceso_id}", headers=headers)
    detail = detail_response.json()
    
    audit_trail = detail.get("audit_trail", [])
    
    # Verificar que hay registros de CREATE y UPDATE
    has_create = any(log["accion"] == "CREATE" for log in audit_trail)
    has_updates = sum(1 for log in audit_trail if log["accion"] == "UPDATE")
    has_field_tracking = any(log.get("campo_modificado") for log in audit_trail)
    
    print_test("Registro CREATE en audit_log", has_create,
               f"Total registros de auditoría: {len(audit_trail)}")
    print_test("Registros UPDATE por cada campo modificado", has_updates >= 2,
               f"Registros UPDATE encontrados: {has_updates}")
    print_test("Tracking de campos específicos", has_field_tracking,
               "Campos modificados registrados correctamente")

def test_5_role_permissions():
    """🔒 Usuario viewer no puede crear/editar/eliminar (403)"""
    print("=" * 60)
    print("TEST 5: Control de acceso por roles")
    print("=" * 60)
    
    viewer_headers = {
        "Authorization": "Bearer viewer-token",
        "X-User-Name": "viewer_user"
    }
    
    # Intentar crear como viewer
    proceso_data = {
        "numero_proceso": "2024-FORBIDDEN-001",
        "fecha_radicacion": datetime.now().strftime("%Y-%m-%d"),
        "estado": "ACTIVO",
        "partes": "Test vs Test"
    }
    
    create_response = requests.post(f"{BASE_URL}/procesos", json=proceso_data, headers=viewer_headers)
    create_forbidden = create_response.status_code == 403
    
    # Crear un proceso como operator para intentar editarlo/eliminarlo como viewer
    operator_headers = {"Authorization": "Bearer operator-token", "X-User-Name": "operator_user"}
    test_proceso = requests.post(f"{BASE_URL}/procesos", json={
        "numero_proceso": "2024-ROLE-TEST",
        "fecha_radicacion": datetime.now().strftime("%Y-%m-%d"),
        "estado": "ACTIVO",
        "partes": "Test vs Test"
    }, headers=operator_headers).json()
    
    proceso_id = test_proceso["id"]
    
    # Intentar editar como viewer
    edit_response = requests.put(f"{BASE_URL}/procesos/{proceso_id}", 
                                 json={"estado": "TERMINADO"}, 
                                 headers=viewer_headers)
    edit_forbidden = edit_response.status_code == 403
    
    # Intentar eliminar como viewer
    delete_response = requests.delete(f"{BASE_URL}/procesos/{proceso_id}", headers=viewer_headers)
    delete_forbidden = delete_response.status_code == 403
    
    print_test("Viewer no puede crear (403)", create_forbidden,
               f"Status: {create_response.status_code}")
    print_test("Viewer no puede editar (403)", edit_forbidden,
               f"Status: {edit_response.status_code}")
    print_test("Viewer no puede eliminar (403)", delete_forbidden,
               f"Status: {delete_response.status_code}")

def test_6_performance():
    """⏱️ GET /api/procesos responde en < 1s con registros"""
    print("=" * 60)
    print("TEST 6: Performance básico")
    print("=" * 60)
    
    headers = {
        "Authorization": "Bearer viewer-token",
        "X-User-Name": "test_user"
    }
    
    start_time = datetime.now()
    response = requests.get(f"{BASE_URL}/procesos", headers=headers)
    end_time = datetime.now()
    
    elapsed = (end_time - start_time).total_seconds()
    count = len(response.json())
    
    print_test("GET /api/procesos responde en < 1s", elapsed < 1.0,
               f"Tiempo: {elapsed:.3f}s, Registros: {count}")

def main():
    print("\n")
    print("=" * 60)
    print("  VERIFICACION MVP - ARCHIVO VIRTUAL DE PROCESOS JUDICIALES")
    print("=" * 60)
    print("\n")
    
    try:
        # Verificar que el servidor está corriendo
        response = requests.get(f"{BASE_URL}/procesos", headers={"Authorization": "Bearer viewer-token", "X-User-Name": "test"})
        print(f"[OK] Servidor corriendo en {BASE_URL}\n")
    except Exception as e:
        print(f"[FAIL] Error: No se puede conectar al servidor en {BASE_URL}")
        print(f"   Asegúrate de que el servidor esté corriendo con: uvicorn app.main:app --reload")
        return
    
    # Ejecutar tests
    clean_all_processes()
    test_1_create_valid_proceso()
    
    clean_all_processes()
    test_2_create_invalid_proceso()
    
    clean_all_processes()
    test_3_filter_functionality()
    
    clean_all_processes()
    test_4_audit_trail()
    
    clean_all_processes()
    test_5_role_permissions()
    
    clean_all_processes()
    test_6_performance()
    
    print("=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Abre tu navegador en: http://127.0.0.1:8000")
    print("2. Prueba la interfaz manualmente")
    print("3. Verifica que los filtros funcionan correctamente")
    print("4. Cambia entre roles (Admin/Operator/Viewer) y verifica permisos")
    print("5. Revisa el historial de auditoría en el detalle de un proceso")
    print("\n")

if __name__ == "__main__":
    main()
