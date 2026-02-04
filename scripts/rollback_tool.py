import shutil
import os
import datetime
import sys

# Force UTF-8 for console output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
DB_PATH = "judicial_archive.db"
BACKUP_DIR = "backups"

def backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"{DB_PATH}_{timestamp}.bak")
    
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup creado: {backup_path}")

def rollback():
    if not os.path.exists(BACKUP_DIR):
        print("❌ Error: No existe carpeta de backups.")
        return

    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".bak")], reverse=True)
    if not backups:
        print("❌ Error: No se encontraron archivos de backup.")
        return

    latest_backup = os.path.join(BACKUP_DIR, backups[0])
    shutil.copy2(latest_backup, DB_PATH)
    print(f"✅ Rollback completado desde: {latest_backup}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python rollback_tool.py [backup|rollback]")
    elif sys.argv[1] == "backup":
        backup()
    elif sys.argv[1] == "rollback":
        rollback()
