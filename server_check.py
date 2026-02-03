#!/usr/bin/env python3
"""
ANTIGRAVITY PROMPT — EXECUTABLE (Python)

RULES
- Deterministic steps only
- Strict causality order
- Minimal patches
- Evidence after each step
- No speculative changes

TARGET
Describe aquí el objetivo concreto (ej: recuperar /settings, auditar proxy, etc.)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ----------------------------
# CONFIG (EDIT PER TASK)
# ----------------------------
TARGET_URL = "http://127.0.0.1:5000/settings"
PORT = 5000
OUT_DIR = Path("./antigravity_out")
OUT_DIR.mkdir(exist_ok=True)

# ----------------------------
# UTILITIES
# ----------------------------
def run(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(p.stdout)
    if p.stderr:
        print("STDERR:", p.stderr)
    return p.returncode, p.stdout, p.stderr

def log(name: str, content: str):
    path = OUT_DIR / f"{name}.log"
    path.write_text(content, encoding="utf-8")
    print(f"[saved] {path}")

# ----------------------------
# PHASE 0 — LIVENESS CHECK
# ----------------------------
def phase_0_liveness():
    rc, out, err = run(f"curl -i {TARGET_URL}")
    log("phase_0_liveness", out + err)
    if "Connection refused" in out or rc != 0:
        print("P0: backend not accepting connections")
        return False
    return True

# ----------------------------
# PHASE 1 — PORT LISTENER
# ----------------------------
def phase_1_port():
    if sys.platform.startswith("win"):
        cmd = f"netstat -ano | findstr :{PORT}"
    else:
        cmd = f"lsof -i :{PORT}"
    rc, out, err = run(cmd)
    log("phase_1_port", out + err)
    return rc == 0

# ----------------------------
# MAIN
# ----------------------------
def main():
    print("ANTIGRAVITY EXECUTION START")
    print("Timestamp:", datetime.utcnow().isoformat(), "UTC")

    alive = phase_0_liveness()
    listening = phase_1_port()

    if not alive or not listening:
        print("STOP CONDITION MET — FIX BACKEND BEFORE UI/UX")
        sys.exit(1)

    print("Backend reachable. Ready to continue with API / UI/UX phases.")
    sys.exit(0)

if __name__ == "__main__":
    main()
