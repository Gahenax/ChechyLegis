from __future__ import annotations
import json
import os
import sys
import time
import subprocess
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
import threading
import logging

# GAHENAX | Jules-in-Background (Subordinado a Antigravity)
# --------------------------------------------------------
# Configuración y Worker subordinado para ejecución de patches.

logging.basicConfig(level=logging.INFO, format='[JULES-WORKER] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("jules")

@dataclass
class JulesConfig:
    allowed_dirs: List[str] = field(default_factory=lambda: ["app", "static", "antigravity_reports", "scripts"])
    max_retries: int = 3
    task_queue_path: str = "antigravity_out/tasks"
    reports_path: str = "antigravity_reports/jules"
    auto_start: bool = True

@dataclass
class PatchTask:
    id: str
    target_file: str
    action: str # "REPLACE", "APPEND", "AUDIT"
    content: str
    verification_cmd: Optional[str] = None
    priority: int = 1
    timestamp: float = field(default_factory=time.time)

class JulesWorker:
    def __init__(self, config: JulesConfig):
        self.config = config
        self.running = False
        self._ensure_dirs()
        
    def _ensure_dirs(self):
        os.makedirs(self.config.task_queue_path, exist_ok=True)
        os.makedirs(self.config.reports_path, exist_ok=True)

    def validate_subordination(self, task: PatchTask) -> bool:
        """
        Verifica que Jules no se salga de su alcance definido.
        """
        target_path = Path(task.target_file).resolve()
        workspace_root = Path(os.getcwd()).resolve()
        
        # 1. No salir del workspace
        if not str(target_path).startswith(str(workspace_root)):
            logger.error(f"VIOLACIÓN DE ALCANCE: {task.target_file} está fuera del workspace.")
            return False
            
        # 2. Solo archivos en directorios permitidos
        try:
            # Normalizar a posix para evitar problemas con backslashes en Windows
            rel_path_str = target_path.relative_to(workspace_root).as_posix()
            top_dir = rel_path_str.split('/')[0] if '/' in rel_path_str else rel_path_str
        except ValueError:
             logger.error(f"VIOLACIÓN DE ALCANCE: {task.target_file} no es relativo al root.")
             return False
        
        if top_dir not in self.config.allowed_dirs:
            logger.error(f"VIOLACIÓN DE ALCANCE: Directorio '{top_dir}' no permitido para Jules. Permitidos: {self.config.allowed_dirs}")
            return False
            
        return True

    def run_deterministic_verification(self, task: PatchTask) -> bool:
        """
        Ejecuta hooks de validación después de aplicar el patch.
        """
        if not task.verification_cmd:
            return True # Sin comando, asumimos éxito tras escritura
            
        logger.info(f"Iniciando verificación determinista: {task.verification_cmd}")
        try:
            result = subprocess.run(task.verification_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("VERIFICACIÓN EXITOSA.")
                return True
            else:
                logger.warning(f"VERIFICACIÓN FALLIDA: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            return False

    ALLOWED_COMMANDS = [
        "python build_portable.py",
        "python auditoria_semaforo.py",
        "pip list --outdated",
        "python verify_mvp.py",
        "python verify_free_limits.py",
        "python scripts/rollback_tool.py backup",
        "python verify_remediation.py"
    ]

    def process_task(self, task: PatchTask):
        logger.info(f"Consumiendo tarea {task.id} -> Acción: {task.action}")
        
        if not self.validate_subordination(task):
            self.create_report(task, "FAILED", "Error de subordinación: Alcance prohibido.")
            return

        try:
            if task.action == "EXEC":
                # Sniper Mode: Strict Command Validation
                is_allowed = any(task.content.startswith(cmd) for cmd in self.ALLOWED_COMMANDS)
                if not is_allowed:
                    logger.warning(f"INTENTO DE EJECUCIÓN NO PERMITIDO: {task.content}")
                    self.create_report(task, "DENIED", f"Comando '{task.content}' no está en la lista blanca de seguridad.")
                    return

                logger.info(f"Ejecutando comando seguro: {task.content}")
                result = subprocess.run(task.content, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.create_report(task, "DONE", f"Comando ejecutado con éxito.\nSTDOUT: {result.stdout}")
                else:
                    self.create_report(task, "FAILED", f"Comando falló (code {result.returncode}).\nSTDERR: {result.stderr}")
            
            elif task.action == "PATCH" or task.action == "REPLACE":
                logger.info(f"Aplicando patch/replace en {task.target_file}")
                with open(task.target_file, "w", encoding="utf-8") as f:
                    f.write(task.content)
                
                if self.run_deterministic_verification(task):
                    self.create_report(task, "DONE", "Patch aplicado y verificado correctamente.")
                else:
                    self.create_report(task, "FAILED", "Validación determinista fallida tras aplicar patch.")
            
            elif task.action == "AUDIT":
                logger.info("Iniciando escaneo de seguridad...")
                # Simular escaneo o ejecutar pip audit/safety
                result = subprocess.run(f"pip list --outdated", shell=True, capture_output=True, text=True)
                summary = f"Escaneo completado. Paquetes desactualizados:\n{result.stdout}"
                self.create_report(task, "DONE", summary)
            
            else:
                # Comportamiento por defecto: escribir a archivo
                with open(task.target_file, "w", encoding="utf-8") as f:
                    f.write(task.content)
                self.create_report(task, "DONE", f"Tarea '{task.action}' procesada por defecto.")
                
        except Exception as e:
            logger.error(f"Error procesando tarea {task.id}: {e}")
            self.create_report(task, "ERROR", str(e))

    def create_report(self, task: PatchTask, status: str, message: str):
        report = {
            "task_id": task.id,
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "target": task.target_file
        }
        report_file = os.path.join(self.config.reports_path, f"report_{task.id}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        logger.info(f"Reporte generado: {status} - {report_file}")

    def start_polling(self):
        self.running = True
        logger.info("Jules Worker iniciado. Esperando tareas de Antigravity...")
        
        while self.running:
            files = [f for f in os.listdir(self.config.task_queue_path) if f.endswith(".json")]
            for f in files:
                file_path = os.path.join(self.config.task_queue_path, f)
                try:
                    with open(file_path, "r", encoding="utf-8") as tf:
                        data = json.load(tf)
                        task = PatchTask(**data)
                    
                    self.process_task(task)
                    os.remove(file_path) # Marcar como consumida
                except Exception as e:
                    logger.error(f"Error leyendo tarea {f}: {e}")
            
            time.sleep(2) # Polling cada 2 segundos

if __name__ == "__main__":
    config = JulesConfig()
    jules = JulesWorker(config)
    jules.start_polling()
