import subprocess
import sys
import os

# GAHENAX | Production Deployment Script
# --------------------------------------
# Este script sincroniza el código auditado con el repositorio central
# para gatillar el despliegue automático en Hostinger.

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SUCCESS: {result.stdout}")
        return True
    else:
        print(f"FAILED: {result.stderr}")
        return False

def main():
    print("Iniciando despliegue de produccion via Jules...")
    
    # 1. Asegurar que estamos en el root
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 2. Sincronizar cambios (redundante pero seguro para Jules)
    if not run_command("git add ."):
        return
        
    if not run_command('git commit -m "deploy: Production sync via Jules worker"'):
        print("ℹ️ Nada nuevo que commitear.")
    
    # 3. Empujar a producción (GitHub Main)
    if run_command("git push origin main"):
        print("\n✅ Despliegue completado. Hostinger debería iniciar la sincronización.")
    else:
        print("\n❌ Error al empujar a producción.")

if __name__ == "__main__":
    main()
