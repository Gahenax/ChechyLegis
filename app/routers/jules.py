from fastapi import APIRouter, Depends, HTTPException
import os
import json
import uuid
from typing import Dict
from ..core.config import settings
from ..core.security import role_required

router = APIRouter(
    prefix="/api/jules",
    tags=["Jules Background Worker"]
)

TASK_QUEUE = "antigravity_out/tasks"
REPORTS_DIR = "antigravity_reports/jules"

os.makedirs(TASK_QUEUE, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/dispatch")
def dispatch_task(
    task_data: Dict,
    user: dict = Depends(role_required(["admin"]))
):
    """
    Envía una tarea al worker Jules.
    """
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    task_file = os.path.join(TASK_QUEUE, f"{task_id}.json")
    
    # Adaptar para que Jules lo entienda (según jules_worker.py)
    # PatchTask(id, target_file, action, content, verification_cmd, priority, timestamp)
    
    payload = {
        "id": task_id,
        "target_file": task_data.get("target_file", "antigravity_reports/jules/log.txt"),
        "action": task_data.get("action", "APPEND"),
        "content": task_data.get("content", f"Task from UI by {user['name']}"),
        "verification_cmd": task_data.get("verification_cmd"),
        "priority": task_data.get("priority", 1)
    }
    
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
        
    return {"status": "dispatched", "task_id": task_id}

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """
    Consulta el estado de una tarea procesada por Jules.
    """
    report_file = os.path.join(REPORTS_DIR, f"report_{task_id}.json")
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Si el archivo de tarea aún existe en la cola, está pendiente
    task_file = os.path.join(TASK_QUEUE, f"{task_id}.json")
    if os.path.exists(task_file):
        return {"status": "PENDING", "task_id": task_id}
        
    return {"status": "NOT_FOUND", "task_id": task_id}
