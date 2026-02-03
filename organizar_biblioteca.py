"""
📂 ORGANIZADOR DE BIBLIOTECA - LegisChechy
Crea la estructura de carpetas física basada en la base de datos.
"""
import os
import sys
import sqlite3
import re
from datetime import datetime
from pathlib import Path

# Force UTF-8 output for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configuración
DB_PATH = "judicial_archive.db"
BASE_DIR = os.path.join(os.getcwd(), "Biblioteca_Digital")

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def sanitize_name(name):
    """Limpia caracteres inválidos para nombres de carpeta"""
    # Reemplazar caracteres no permitidos en path de Windows
    clean = re.sub(r'[<>:"/\\|?*]', '_', str(name))
    return clean.strip()

def create_readme(path, proceso):
    """Crea un archivo de información en la carpeta"""
    info = f"""EXPEDIENTE DIGITAL
==================================================
Número de Proceso: {proceso['numero']}
Estado: {proceso['estado']}
Fecha Radicación: {proceso['fecha']}
--------------------------------------------------
Partes:
{proceso['partes']}

Clase: {proceso['clase']}
Cuantía: {proceso['cuantia']}

Observaciones:
{proceso['observaciones']}
==================================================
Generado automáticamente: {datetime.now()}
"""
    file_path = os.path.join(path, "INFO_EXPEDIENTE.txt")
    # Solo escribir si ha cambiado o no existe para preservar timestamp de modificación si no es necesario
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Simplificación: si ya existe, lo sobrescribimos para asegurar que está sync
    except:
        pass
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(info)

def main():
    print(f"{Colors.BLUE}📚 Iniciando Organización de Biblioteca Digital...{Colors.END}")
    
    if not os.path.exists(DB_PATH):
        print(f"{Colors.YELLOW}❌ No se encontró la base de datos.{Colors.END}")
        return

    # Crear directorio base
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"{Colors.GREEN}✅ Directorio base creado: {BASE_DIR}{Colors.END}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Verificar tabla documentos si existe para futuras integraciones
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
        
        cursor.execute("SELECT * FROM procesos")
        procesos = cursor.fetchall()
        
        if not procesos:
            print(f"{Colors.YELLOW}⚠️ No hay procesos en la base de datos para organizar.{Colors.END}")
            return

        print(f"🔄 Procesando {len(procesos)} expedientes...")
        
        created_count = 0
        updated_count = 0
        
        for p in procesos:
            # 1. Definir criterios de jerarquía
            estado = sanitize_name(p['estado'])
            fecha = p['fecha_radicacion'] # YYYY-MM-DD
            year = fecha.split('-')[0] if '-' in str(fecha) else "Sin_Fecha"
            # clase = sanitize_name(p['clase_proceso']) if p['clase_proceso'] else "Sin_Clase"
            numero = sanitize_name(p['numero_proceso'])
            
            # Estructura: Biblioteca / Estado / Año / Numero
            # Organizado primero por Estado para separar Activos de Terminados
            target_path = os.path.join(BASE_DIR, estado, year, numero)
            
            # 2. Crear carpetas
            is_new = False
            if not os.path.exists(target_path):
                os.makedirs(target_path)
                is_new = True
                
            # 3. Generar ficha (INFO_EXPEDIENTE.txt)
            proceso_dict = {
                'numero': p['numero_proceso'],
                'estado': p['estado'],
                'fecha': p['fecha_radicacion'],
                'partes': p['partes'],
                'clase': p['clase_proceso'] or "N/A",
                'cuantia': p['cuantia_tipo'] or "N/A",
                'observaciones': p['observaciones'] or ""
            }
            create_readme(target_path, proceso_dict)
            
            if is_new:
                created_count += 1
                print(f"   {Colors.GREEN}+ Creado:{Colors.END} {estado}/{year}/{numero}")
            else:
                updated_count += 1
                
        print("\n" + "="*50)
        print(f"{Colors.GREEN}✅ Organización Completada{Colors.END}")
        print(f"📂 Carpetas Nuevas/Creadas: {created_count}")
        print(f"🔄 Carpetas Verificadas: {updated_count}")
        print(f"📍 Ubicación: {BASE_DIR}")
        print("="*50)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
