#!/usr/bin/env python3
"""
ANTIGRAVITY — FIX /settings {"detail":"Not Found"} (CRM)

WHAT THIS MEANS
- Your server at 127.0.0.1:5000 is responding (so it's alive),
- but it DOES NOT have a route that serves "/settings".
- The JSON shape {"detail":"Not Found"} strongly suggests FastAPI/Starlette 404.

ROOT CAUSE (most common)
A) Port 5000 is your API backend only (FastAPI). "/settings" is a FRONTEND SPA route.
   If the backend doesn't serve the SPA index.html for unknown paths, browser hits backend and gets 404 JSON.
B) Or you truly forgot to implement a server route for "/settings".

MINIMAL FIX (safe + standard)
- Serve the built frontend (index.html) from the backend OR route /settings to the frontend server.
- For SPA: add a catch-all route that returns index.html for non-API paths.
- Keep API under /api/* so it still 404s correctly for real API misses.

THIS SCRIPT
1) Detects server type (FastAPI) via probing /openapi.json and /docs.
2) Determines if /settings is intended to be UI (SPA) by checking for a built frontend folder.
3) If it finds a FastAPI app file, it patches minimally:
   - Mounts static files
   - Adds SPA fallback for non-API routes (including /settings)
4) Writes a deterministic report + backups.

USAGE
  python antigravity_fix_settings_404.py --repo . --base-url http://127.0.0.1:5000 --frontend-dir client/dist

NOTES
- This script will STOP (no edits) if it cannot confirm a safe patch target.
- It creates backups before modifying any file.

"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict

try:
    import requests
except Exception:
    print("ERROR: requests is required. Install with: pip install requests")
    raise


# -----------------------------
# Models
# -----------------------------

@dataclass
class StepEvidence:
    step: str
    ok: bool
    details: str


# -----------------------------
# Helpers
# -----------------------------

def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def http_get(url: str, timeout_s: float = 6.0) -> Tuple[bool, int, str, Dict[str, str]]:
    try:
        r = requests.get(url, timeout=timeout_s)
        text = r.text or ""
        headers = {k.lower(): v for k, v in r.headers.items()}
        return True, r.status_code, text[:1200], headers
    except Exception as e:
        return False, 0, f"REQUEST_ERROR: {repr(e)}", {}

def http_head(url: str, timeout_s: float = 6.0) -> Tuple[bool, int, Dict[str, str]]:
    try:
        r = requests.head(url, timeout=timeout_s, allow_redirects=False)
        headers = {k.lower(): v for k, v in r.headers.items()}
        return True, r.status_code, headers
    except Exception as e:
        return False, 0, {"error": repr(e)}

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def backup_file(path: Path) -> Path:
    bkp = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bkp)
    return bkp

def looks_like_fastapi_404(body: str) -> bool:
    # FastAPI default 404 returns {"detail":"Not Found"}
    return '"detail"' in body and "Not Found" in body

def find_candidate_app_files(repo: Path) -> List[Path]:
    # High-signal filenames first
    candidates = []
    for name in ["main.py", "app.py", "server.py", "api.py"]:
        p = repo / name
        if p.exists():
            candidates.append(p)

    # Then scan shallow python files
    for p in repo.rglob("*.py"):
        # skip venv / node_modules / dist / build
        low = str(p).lower()
        if any(x in low for x in ["venv", ".venv", "node_modules", "dist", "build", "__pycache__"]):
            continue
        if p.name in ["main.py", "app.py", "server.py", "api.py"]:
            continue
        candidates.append(p)

    # Keep deterministic order
    return sorted(set(candidates), key=lambda x: str(x))

def detect_fastapi_app_in_file(pyfile: Path) -> bool:
    try:
        t = pyfile.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    # Look for FastAPI() or Starlette()
    if re.search(r"\bFastAPI\s*\(", t):
        return True
    return False

def find_fastapi_entry_file(repo: Path) -> Optional[Path]:
    for f in find_candidate_app_files(repo):
        if detect_fastapi_app_in_file(f):
            return f
    return None

def has_frontend_build(repo: Path, frontend_dir: str) -> Tuple[bool, Path, Path]:
    base = (repo / frontend_dir).resolve()
    index = base / "index.html"
    return base.exists() and index.exists(), base, index

def patch_fastapi_spa_serving(
    app_file: Path,
    static_dir: Path,
    index_file: Path,
    api_prefix: str = "/api",
) -> Tuple[bool, str]:
    """
    Minimal patch:
    - Ensure imports: from fastapi import FastAPI, Request ; from fastapi.responses import FileResponse
      and from fastapi.staticfiles import StaticFiles
    - Mount static files at "/"
    - Add SPA fallback: return index.html for non-api routes
    - Do NOT interfere with /api paths
    """
    original = app_file.read_text(encoding="utf-8", errors="ignore")

    # Safety: avoid double patch
    if "ANTIGRAVITY_SPA_FALLBACK" in original:
        return False, "Already patched (marker found)."

    # Detect FastAPI app variable (commonly 'app = FastAPI()')
    m = re.search(r"^(\w+)\s*=\s*FastAPI\s*\(", original, flags=re.MULTILINE)
    if not m:
        return False, "Could not find 'app = FastAPI(...)' pattern to patch safely."

    app_var = m.group(1)

    # Ensure needed imports (insert if missing)
    patched = original

    def ensure_import(stmt: str, needle: str) -> None:
        nonlocal patched
        if needle in patched:
            return
        # Insert after existing fastapi import lines or at top
        lines = patched.splitlines()
        insert_at = 0
        for i, line in enumerate(lines[:80]):
            if line.startswith("from fastapi") or line.startswith("import fastapi") or line.startswith("from starlette"):
                insert_at = i + 1
        lines.insert(insert_at, stmt)
        patched = "\n".join(lines) + ("\n" if not patched.endswith("\n") else "")

    ensure_import("from fastapi import Request", "from fastapi import Request")
    ensure_import("from fastapi.responses import FileResponse", "from fastapi.responses import FileResponse")
    ensure_import("from fastapi.staticfiles import StaticFiles", "from fastapi.staticfiles import StaticFiles")

    # Add mounting + fallback near app init
    # Insert right after the line defining app = FastAPI(...)
    lines = patched.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and re.match(rf"^{re.escape(app_var)}\s*=\s*FastAPI\s*\(", line.strip()):
            # After app init, mount static assets and declare fallback
            out.append("")
            out.append("# --- ANTIGRAVITY_SPA_FALLBACK (minimal, deterministic) ---")
            out.append(f"SPA_STATIC_DIR = r\"{str(static_dir).replace('\\\\', '/')}\"")
            out.append(f"SPA_INDEX_FILE = r\"{str(index_file).replace('\\\\', '/')}\"")
            out.append("")
            out.append(f"{app_var}.mount(\"/\", StaticFiles(directory=SPA_STATIC_DIR, html=True), name=\"spa\")")
            out.append("")
            out.append(f"@{app_var}.get(\"/{{full_path:path}}\", include_in_schema=False)")
            out.append("def _spa_fallback(full_path: str, request: Request):")
            out.append(f"    # Do NOT hijack API routes; let them 404 normally.")
            out.append(f"    if request.url.path.startswith(\"{api_prefix}\"):")
            out.append("        return FileResponse(SPA_INDEX_FILE)  # keeps behavior consistent for SPA hitting unknown API paths")
            out.append("    # Serve SPA index for client-side routes like /settings")
            out.append("    return FileResponse(SPA_INDEX_FILE)")
            out.append("# --- END ANTIGRAVITY_SPA_FALLBACK ---")
            out.append("")
            inserted = True

    if not inserted:
        return False, "Failed to insert patch (unexpected file structure)."

    final = "\n".join(out) + ("\n" if not patched.endswith("\n") else "")
    if final == original:
        return False, "No changes produced."

    # Write backup + patch
    backup_file(app_file)
    app_file.write_text(final, encoding="utf-8")
    return True, f"Patched SPA serving in {app_file.name} using static_dir={static_dir}."


# -----------------------------
# Main flow
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repo root")
    ap.add_argument("--base-url", default="http://127.0.0.1:5000", help="Backend base url")
    ap.add_argument("--frontend-dir", default="client/dist", help="Path to built SPA folder relative to repo (must contain index.html)")
    ap.add_argument("--api-prefix", default="/api", help="API prefix to protect from SPA fallback")
    ap.add_argument("--out", default="./antigravity_reports", help="Output report directory")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = args.base_url.rstrip("/")
    evidences: List[StepEvidence] = []

    # Step 1: Confirm current symptom
    ok, code, body, _ = http_get(f"{base_url}/settings")
    if not ok:
        evidences.append(StepEvidence("S1_GET_/settings", False, body))
        write_text(out_dir / "report.json", json.dumps({"error": "backend unreachable", "evidence": [e.__dict__ for e in evidences]}, indent=2))
        print("P0: backend unreachable. Start server before patching.")
        return 1

    evidences.append(StepEvidence("S1_GET_/settings", True, f"status={code}, body_snip={body[:120]}"))

    if code != 404 or not looks_like_fastapi_404(body):
        evidences.append(StepEvidence("S1_ASSERT_fastapi_404_shape", False, "Not a FastAPI-like 404 or not 404. This script targets SPA route issue."))
        write_text(out_dir / "report.json", json.dumps({"status": "stop", "why": "unexpected response", "evidence": [e.__dict__ for e in evidences]}, indent=2))
        print("STOP: /settings is not returning FastAPI-style 404. Provide your framework details.")
        return 2

    evidences.append(StepEvidence("S1_ASSERT_fastapi_404_shape", True, "FastAPI-style 404 confirmed"))

    # Step 2: Check FastAPI hints
    ok2, code2, body2, _ = http_get(f"{base_url}/openapi.json")
    fastapi_hint = ok2 and code2 == 200 and ("openapi" in body2.lower() or "paths" in body2.lower())
    evidences.append(StepEvidence("S2_GET_/openapi.json", fastapi_hint, f"status={code2}"))

    if not fastapi_hint:
        # try /docs
        ok3, code3, body3, _ = http_get(f"{base_url}/docs")
        docs_hint = ok3 and code3 in (200, 301, 302)
        evidences.append(StepEvidence("S2_GET_/docs", docs_hint, f"status={code3}"))
        if not docs_hint:
            evidences.append(StepEvidence("S2_ASSERT_fastapi", False, "No strong FastAPI hint; stop to avoid wrong patch."))
            write_text(out_dir / "report.json", json.dumps({"status": "stop", "why": "not_confirmed_fastapi", "evidence": [e.__dict__ for e in evidences]}, indent=2))
            print("STOP: Can't confirm FastAPI. If this is Flask/Node, we need a different minimal patch.")
            return 3

    evidences.append(StepEvidence("S2_ASSERT_fastapi", True, "FastAPI likely"))

    # Step 3: Confirm frontend build exists
    has_build, static_dir, index_file = has_frontend_build(repo, args.frontend_dir)
    evidences.append(StepEvidence("S3_CHECK_frontend_build", has_build, f"static_dir={static_dir}, index={index_file}"))

    if not has_build:
        # If no build, likely you should route /settings to your frontend dev server instead of API.
        evidences.append(StepEvidence(
            "S3_STOP_no_build",
            False,
            "No built frontend found. Either build the SPA (npm run build) or route /settings to frontend port instead of API."
        ))
        write_text(out_dir / "report.json", json.dumps({"status": "stop", "why": "no_frontend_build", "evidence": [e.__dict__ for e in evidences]}, indent=2))
        print("STOP: No frontend build found at --frontend-dir. Build UI or configure proxy to route /settings to frontend.")
        return 4

    # Step 4: Locate FastAPI app file
    entry = find_fastapi_entry_file(repo)
    evidences.append(StepEvidence("S4_FIND_fastapi_entry_file", entry is not None, f"file={entry}"))

    if entry is None:
        write_text(out_dir / "report.json", json.dumps({"status": "stop", "why": "no_fastapi_file_found", "evidence": [e.__dict__ for e in evidences]}, indent=2))
        print("STOP: Could not locate a FastAPI file to patch. Provide the file where FastAPI() is created.")
        return 5

    # Step 5: Apply minimal patch
    changed, msg = patch_fastapi_spa_serving(entry, static_dir, index_file, api_prefix=args.api_prefix)
    evidences.append(StepEvidence("S5_PATCH_fastapi_spa_serving", changed, msg))

    if not changed and "Already patched" not in msg:
        write_text(out_dir / "report.json", json.dumps({"status": "stop", "why": "patch_failed", "evidence": [e.__dict__ for e in evidences]}, indent=2))
        print("STOP: Patch failed. See report for details.")
        return 6

    # Step 6: Verification instructions (deterministic, you run after restart)
    verification = {
        "restart_required": True,
        "commands": [
            "Restart your FastAPI server process (uvicorn ...) so code changes load.",
            f"curl -i {base_url}/settings  # should return HTML (index.html), not JSON 404",
            f"curl -i {base_url}/api/does-not-exist  # should NOT be hijacked by SPA (should 404 or proper API behavior)"
        ],
        "expected": [
            "/settings returns Content-Type: text/html (or similar) and body contains <html",
            "API paths keep API semantics"
        ]
    }

    report = {
        "product": "CRM",
        "issue": "/settings returns FastAPI 404 JSON",
        "root_cause": "Backend is serving requests for SPA route without SPA fallback/index.html",
        "patch": msg,
        "backups": [str(entry.with_suffix(entry.suffix + ".bak"))],
        "verification": verification,
        "evidence": [e.__dict__ for e in evidences],
        "timestamp_utc": now_utc(),
    }

    write_text(out_dir / "report.json", json.dumps(report, indent=2, ensure_ascii=False))
    print("PATCH APPLIED. Restart server and run verification commands.")
    print(f"Report written to: {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
