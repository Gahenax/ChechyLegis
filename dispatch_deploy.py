import json
import os

def dispatch():
    TASK_QUEUE = "antigravity_out/tasks"
    if not os.path.exists(TASK_QUEUE):
        os.makedirs(TASK_QUEUE)
        
    task_id = "task_deploy_prod_v2"
    payload = {
        "id": task_id,
        "target_file": "antigravity_reports/jules/deploy_log_v2.txt",
        "action": "EXEC",
        "content": "python scripts/deploy_production.py",
        "priority": 1
    }
    
    task_file = f"{TASK_QUEUE}/{task_id}.json"
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
    
    print(f"Task {task_id} dispatched to Jules.")

if __name__ == "__main__":
    dispatch()
