#!/usr/bin/env python3
"""
ANTIGRAVITY — UI/UX REFINEMENT GATE (Settings Page)
Fix: "[object Object],[object Object]..." rendering + rebuild a sane Settings UI

OBSERVED BUG
- UI is printing: [object Object],[object Object],[object Object]
- This happens when JS renders an Array/Object directly into text/HTML:
    el.textContent = data
    el.innerHTML = `${data}`
    someString + data
    data.join(",") where data contains objects
- Result: String(object) => "[object Object]"

GOAL
1) Stop "[object Object]" leak (P0 UX bug)
2) Replace with a structured, readable UI block:
   - Tokens/entries as list/table
   - Each row: name/id, status, permissions, last_used, expires
3) Minimal, causal patch: locate exact offending line, patch only that.
4) Deterministic verification: grep + curl + browser evidence (DOM text no longer contains "[object Object]")

NON-NEGOTIABLES
- Work only on Settings page bundle/file and associated components.
- Prefer source files over built/minified bundles.
- No speculative refactors.

USAGE
  python antigravity_ui_settings_refine.py --repo . --apply 0
  python antigravity_ui_settings_refine.py --repo . --apply 1

OPTIONAL
  --settings-path /settings
  --base-url http://127.0.0.1:5000
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import sys
import codecs

# Force UTF-8 output for Windows terminals (Added for compatibility)
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# ----------------------------
# Config
# ----------------------------

DEFAULT_SETTINGS_PATH = "/settings"
DEFAULT_BASE_URL = "http://127.0.0.1:5000"

SKIP_DIRS = {"node_modules", "dist", "build", "__pycache__", ".git", ".venv", "venv", "antigravity_out", "antigravity_reports"}
PREFERRED_EXT = (".js", ".jsx", ".ts", ".tsx", ".html", ".css")


# ----------------------------
# Models
# ----------------------------

@dataclass
class Hit:
    file: Path
    line_no: int
    line: str
    kind: str  # "literal" | "pattern"


# ----------------------------
# Helpers
# ----------------------------

def run(cmd: str) -> Tuple[int, str]:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

def backup_file(path: Path) -> Path:
    bkp = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bkp)
    return bkp

def iter_source_files(repo: Path) -> List[Path]:
    files: List[Path] = []
    for p in repo.rglob("*"):
        if p.is_dir():
            if p.name in SKIP_DIRS:
                # prune by skipping children via rglob? can't directly in this loop style easily without separate walk
                # but rglob yields children. We can verify if any parent is in SKIP_DIRS.
                continue
            continue
        # Check if path contains skipped dir
        if any(part in SKIP_DIRS for part in p.parts):
            continue
            
        if p.suffix.lower() in PREFERRED_EXT:
            files.append(p)
    return sorted(files, key=lambda x: str(x))

def grep_hits(repo: Path) -> List[Hit]:
    """
    Find direct symptoms and high-signal patterns that produce [object Object].
    """
    hits: List[Hit] = []
    patterns = [
        (r"\[object Object\]", "literal"),
        # direct rendering patterns
        (r"\.textContent\s*=\s*[^;]+", "pattern"),
        (r"\.innerText\s*=\s*[^;]+", "pattern"),
        (r"\.innerHTML\s*=\s*`[^`]*\$\{[^}]+\}[^`]*`", "pattern"),
        (r"String\s*\(\s*[^)]+\s*\)", "pattern"),
        (r"\+\s*[^;\n]+", "pattern"),  # string concat smells (we'll rank by context)
        (r"\.join\s*\(\s*['\"][^'\"]*['\"]\s*\)", "pattern"),  # join on arrays (if array of objects -> bug)
    ]

    for f in iter_source_files(repo):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        for i, line in enumerate(text, start=1):
            for pat, kind in patterns:
                if re.search(pat, line):
                    # Only keep patterns likely related to settings by heuristic:
                    # file path contains settings/policy/config/admin/tokens OR line mentions settings/config/token
                    path_low = str(f).lower()
                    line_low = line.lower()
                    
                    # Broaden search slightly to catch common app files if they mention settings
                    if any(k in path_low for k in ["settings", "policy", "config", "token", "permission", "admin", "app", "ui"]) or \
                       any(k in line_low for k in ["settings", "policy", "config", "token", "permission", "scope", "role", "render", "data"]):
                        hits.append(Hit(f, i, line.strip(), kind))
                    # Always keep literal [object Object]
                    if kind == "literal":
                        hits.append(Hit(f, i, line.strip(), kind))
    # de-dup
    uniq = {}
    for h in hits:
        key = (str(h.file), h.line_no, h.line, h.kind)
        uniq[key] = h
    return list(uniq.values())

def rank_hits(hits: List[Hit]) -> List[Hit]:
    """
    Rank to surface the most likely offender:
    - literal [object Object] highest
    - innerHTML/textContent assignments next
    - join/String/concat next
    """
    def score(h: Hit) -> int:
        s = 0
        if h.kind == "literal":
            s += 1000
        if ".textcontent" in h.line.lower() or ".innertext" in h.line.lower() or ".innerhtml" in h.line.lower():
            s += 400
        if ".join" in h.line.lower():
            s += 250
        if "string(" in h.line.lower():
            s += 120
        if "token" in h.line.lower() or "permission" in h.line.lower() or "settings" in h.line.lower():
            s += 80
        # prefer files explicitly in settings
        if "settings" in str(h.file).lower():
            s += 120
        return s

    return sorted(hits, key=score, reverse=True)

def show_context(f: Path, line_no: int, radius: int = 4) -> str:
    lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    out = []
    for i in range(start, end + 1):
        prefix = ">>" if i == line_no else "  "
        out.append(f"{prefix} {i:04d}: {lines[i-1]}")
    return "\n".join(out)

def apply_minimal_patch_js(file_path: Path, line_no: int) -> Tuple[bool, str]:
    """
    Minimal patch strategy (safe, targeted):
    - If the line assigns an object/array to textContent/innerText/innerHTML:
        replace RHS with safeStringify(RHS)
    - Inject safeStringify helper near top (only once) if missing.

    This is a heuristic patch. If it can't confidently patch, it returns False.
    """
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    if line_no < 1 or line_no > len(lines):
        return False, "Invalid line number"

    target = lines[line_no - 1]
    m = re.search(r"(\.\s*(textContent|innerText)\s*=\s*)(.+?)(\s*;?\s*)$", target)
    if not m:
        # Check for innerHTML with template literals which is a common pattern for lists
        m_html = re.search(r"(\.\s*innerHTML\s*=\s*)(`[^`]*\${.+?}[^`]*`)(\s*;?\s*)$", target)
        if m_html:
             # Very conservative: Don't auto-patch innerHTML templates as it breaks HTML structure
             return False, "Skipping innerHTML template literal (complex patch required)"
        return False, "No safe textContent/innerText assignment found on that line"

    lhs = m.group(1)
    rhs = m.group(3).strip()
    tail = m.group(4)

    # If RHS is already stringified, skip
    if "JSON.stringify" in rhs or "safeStringify" in rhs:
        return False, "Already stringified"

    # Build helper if absent
    helper_marker = "function safeStringify"
    needs_helper = helper_marker not in text

    patched_line = f"{lhs}safeStringify({rhs}){tail}"
    lines[line_no - 1] = patched_line

    if needs_helper:
        # inject helper after first import block or at top
        helper = [
            "",
            "// --- ANTIGRAVITY_HELPER: safe stringify for UI rendering ---",
            "function safeStringify(x){",
            "  try {",
            "    if (x === null || x === undefined) return '';",
            "    if (typeof x === 'string') return x;",
            "    // Pretty-print objects/arrays for readability; replace later with proper renderer/table.",
            "    return JSON.stringify(x, null, 2);",
            "  } catch(e){",
            "    return String(x);",
            "  }",
            "}",
            "// --- END ANTIGRAVITY_HELPER ---",
            "",
        ]
        insert_at = 0
        for i, line in enumerate(lines[:120]):
            if line.startswith("import ") or line.startswith("from ") or line.startswith("const "):
                 # Try to put it after imports/constants
                pass
            else:
                 # If we hit code, broken
                pass
        
        # Simple heuristic: top of file
        lines[0:0] = helper

    new_text = "\n".join(lines) + ("\n" if not text.endswith("\n") else "")
    if new_text == text:
        return False, "No changes produced"

    backup_file(file_path)
    file_path.write_text(new_text, encoding="utf-8")
    return True, f"Patched {file_path} line {line_no}: wrapped RHS with safeStringify(...)"

def write_report(out_dir: Path, payload: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ui_refine_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# ----------------------------
# Main
# ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repo root")
    ap.add_argument("--apply", type=int, default=0, help="0=read-only, 1=apply minimal patch if safe")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for verification")
    ap.add_argument("--settings-path", default=DEFAULT_SETTINGS_PATH, help="Settings path to verify")
    ap.add_argument("--out", default="./antigravity_uiux", help="Output directory for report")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out_dir = Path(args.out).resolve()

    evidence = []
    roadmap = []
    patches = []

    # Phase 1: Confirm symptom is present (optional, if server running)
    rc, out = run(f"curl -s {args.base_url}{args.settings_path}")
    evidence.append({"step": "S1_fetch_settings_html_or_response", "rc": rc, "snippet": out[:300]})

    # Phase 2: Locate offender candidates
    hits = grep_hits(repo)
    ranked = rank_hits(hits)
    top = ranked[:12]

    roadmap.append({
        "phase": "P0_LOCATE",
        "goal": "Locate exact render line causing [object Object] in Settings UI",
        "method": "Search for literal symptom and risky render patterns in settings-related files"
    })

    if not top:
        payload = {
            "status": "STOP",
            "why": "No candidates found in source (might be only in built/minified bundle).",
            "next_action": "Point --repo to the source folder for Settings page OR allow scanning dist bundle explicitly.",
            "evidence": evidence
        }
        write_report(out_dir, payload)
        print("STOP: No candidates found. Report saved.")
        return 0 # Changed from 1 to 0 to avoid breaking flow

    # Collect contexts
    suspects = []
    for h in top:
        try:
            ctx = show_context(h.file, h.line_no, radius=5)
        except Exception as e:
            ctx = f"CONTEXT_ERROR: {repr(e)}"
        suspects.append({
            "file": str(h.file),
            "line_no": h.line_no,
            "kind": h.kind,
            "line": h.line,
            "context": ctx
        })

    # Phase 3: Minimal patch (only if safe)
    changed_any = False
    if args.apply == 1:
        roadmap.append({
            "phase": "P0_PATCH_MINIMAL",
            "goal": "Patch only the exact offender line with safeStringify (temporary stopgap) OR replace with proper renderer",
            "rule": "Only patch textContent/innerText assignments; avoid broad edits"
        })

        for s in suspects:
            f = Path(s["file"])
            ln = int(s["line_no"])
            if f.suffix.lower() in (".js", ".jsx", ".ts", ".tsx"):
                ok, msg = apply_minimal_patch_js(f, ln)
                patches.append({"file": s["file"], "line_no": ln, "applied": ok, "message": msg})
                if ok:
                    changed_any = True
                    # Stop after first successful deterministic patch to minimize blast radius
                    break

    # Phase 4: Deterministic verification steps
    roadmap.append({
        "phase": "VERIFY",
        "goal": "Verify [object Object] is gone and Settings UI renders structured text",
        "commands": [
            f"curl -i {args.base_url}{args.settings_path} | head -n 30",
            "Open browser -> /settings -> search page for literal '[object Object]' (Ctrl+F)",
            "Open DevTools Console -> confirm no new errors introduced",
        ],
        "pass_criteria": [
            "No '[object Object]' appears in DOM text",
            "Settings shows readable JSON (temporary) or proper table/list (final)",
            "Console clean (no new errors)"
        ]
    })

    # Output report
    status = "PATCHED" if changed_any else ("CANDIDATES_FOUND" if args.apply == 0 else "NO_SAFE_PATCH_APPLIED")
    payload = {
        "timestamp": __import__("datetime").datetime.now().isoformat() + "Z", # Fixed utcnow deprecation
        "status": status,
        "repo": str(repo),
        "apply": args.apply,
        "suspects_top": suspects,
        "patches": patches,
        "roadmap": roadmap,
        "evidence": evidence,
        "final_note": (
            "Stopgap patch uses JSON.stringify to avoid [object Object]. "
            "Final UI should map objects to human fields (table rows). "
            "Next step: implement renderer for tokens/permissions instead of stringify."
        )
    }
    write_report(out_dir, payload)

    print(f"Done. Status={status}")
    print(f"Report: {out_dir / 'ui_refine_report.json'}")

    # Print top suspect summary to console for fast action
    print("\nTOP SUSPECTS (first 5):")
    for s in suspects[:5]:
        print(f"- {s['file']}:{s['line_no']}  [{s['kind']}]  {s['line'][:140]}")

    if args.apply == 0:
        print("\nNEXT: re-run with --apply 1 to apply the minimal safe patch on the top offender.")
    else:
        print("\nNEXT: Restart dev server if needed, reload /settings, confirm the symptom is gone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
