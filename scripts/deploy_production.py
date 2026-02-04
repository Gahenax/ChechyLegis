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
        # Avoid non-ascii in error messages too
        err_msg = result.stderr.encode('ascii', 'ignore').decode('ascii')
        print(f"FAILED: {err_msg}")
        return False

def main():
    print("Iniciando despliegue de produccion via Jules...")
    
    # 1. Asegurar que estamos en el root
    # Get the directory of the current script, then get its parent (scripts -> root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # 2. Sincronizar cambios
    if not run_command("git add ."):
        return
        
    # Silently handle 'nothing to commit'
    run_command('git commit -m "deploy: Production sync via Jules worker"')
    
    # 3. Empujar a producción (GitHub Main)
    if run_command("git push origin main"):
        print("Despliegue completado. Hostinger deberia iniciar la sincronizacion.")
    else:
        print("Error al empujar a produccion.")

if __name__ == "__main__":
    main()
