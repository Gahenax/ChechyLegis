#!/usr/bin/env python3
"""
Chechy Portable ZIP Builder
- Creates a zero-install portable folder (Chechy/)
- Generates run scripts (run.bat, run.sh)
- Ensures config/data/logs/docs structure
- Zips to Chechy-vX.Y.Z-<platform>.zip (+ optional SHA256)

Usage:
  python build_portable.py --src ./dist --out ./release --name Chechy --version 0.1.0 --platform windows
  python build_portable.py --src ./app --out ./release --name Chechy --version 0.1.0 --platform linux

Notes:
- --src should point to the folder that contains the runnable app entrypoint.
- This script does NOT modify your app; it only packages it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform as py_platform
import shutil
import stat
import sys
import zipfile
from pathlib import Path
from typing import Dict, Any, Tuple


DEFAULT_SETTINGS: Dict[str, Any] = {
    "mode": "portable",
    "storage": {
        "data_dir": "./data",
        "logs_dir": "./logs"
    },
    "server": {
        "host": "127.0.0.1",
        "port": 8080
    }
}


README_TEXT = """CHECHY — PORTABLE (SIN INSTALACIÓN)

Cómo ejecutar
1) Descomprime esta carpeta donde quieras.
2) Windows: doble clic en run.bat
   Linux/macOS: abre terminal en esta carpeta y ejecuta: ./run.sh

Datos y persistencia
- Tus datos viven en: ./data
- Tus logs viven en: ./logs
- Tu configuración vive en: ./config/settings.json

Actualizar sin perder datos
- Sustituye SOLO la carpeta ./app por la nueva versión.
- Conserva: ./data y ./config

Problemas comunes
1) "No se puede ejecutar" (Windows SmartScreen)
   - Click derecho → Propiedades → Desbloquear (si aparece) o “Más información” → Ejecutar.

2) "Permission denied" (Linux/macOS)
   - Ejecuta: chmod +x run.sh

3) Puerto ocupado
   - Cambia el puerto en ./config/settings.json o cierra el proceso que usa ese puerto.
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Chechy portable ZIP artifact.")
    p.add_argument("--src", required=True, help="Source folder containing runnable app (e.g., ./dist or ./app).")
    p.add_argument("--out", required=True, help="Output folder for release artifacts (e.g., ./release).")
    p.add_argument("--name", default="Chechy", help="App/package name (default: Chechy).")
    p.add_argument("--version", required=True, help="Version string like 0.1.0.")
    p.add_argument(
        "--platform",
        default="auto",
        choices=["auto", "windows", "linux", "macos"],
        help="Target platform label for zip name. Default auto-detect.",
    )
    p.add_argument(
        "--entry",
        default="auto",
        help=(
            "Entrypoint inside ./app for run scripts. "
            "Examples: chechy.exe OR python -m chechy OR node server.js. "
            "Default: auto (tries to detect)."
        ),
    )
    p.add_argument("--with-sha256", action="store_true", help="Generate SHA256SUMS.txt for the zip.")
    return p.parse_args()


def detect_platform_label(arg_value: str) -> str:
    if arg_value != "auto":
        return arg_value
    sys_plat = sys.platform.lower()
    if sys_plat.startswith("win"):
        return "windows"
    if sys_plat.startswith("darwin"):
        return "macos"
    return "linux"


def safe_rmtree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f"--src folder not found or not a directory: {src}")
    shutil.copytree(src, dst, dirs_exist_ok=True)


def ensure_dirs(base: Path) -> None:
    for d in ["app", "config", "data", "logs", "docs"]:
        (base / d).mkdir(parents=True, exist_ok=True)


def write_json_if_missing(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def detect_entry(app_dir: Path) -> Tuple[str, str]:
    """
    Returns: (kind, command)
      kind: "exe" | "python" | "node" | "unknown"
      command: command to run inside run scripts (relative to package root)
    """
    # Prefer exe
    exes = list(app_dir.glob("*.exe"))
    if exes:
        # pick first deterministically sorted
        exe = sorted(exes)[0].name
        return ("exe", f".\\app\\{exe}")

    # common python entry guesses
    # 1) module package presence
    if (app_dir / "chechy.py").exists():
        return ("python", "python app/chechy.py")
    if (app_dir / "main.py").exists():
        return ("python", "python app/main.py")

    # node
    if (app_dir / "server.js").exists():
        return ("node", "node app/server.js")
    if (app_dir / "index.js").exists():
        return ("node", "node app/index.js")

    return ("unknown", "")


def make_run_bat(entry_cmd: str) -> str:
    # Windows bat: set working dir to script dir, ensure dirs, run entry
    return rf"""@echo off
setlocal enabledelayedexpansion

REM --- set working directory to this script's folder
cd /d "%~dp0"

REM --- ensure portable folders exist
if not exist "data" mkdir "data"
if not exist "logs" mkdir "logs"
if not exist "config" mkdir "config"
if not exist "docs" mkdir "docs"

REM --- run
echo [Chechy] Starting...
{entry_cmd}
if errorlevel 1 (
  echo.
  echo [Chechy] ERROR: Chechy failed to start.
  echo - Check docs\README.txt
  echo - Verify entrypoint and dependencies
  pause
  exit /b 1
)

endlocal
"""


def make_run_sh(entry_cmd: str) -> str:
    # POSIX sh: cd to script dir, ensure dirs, run entry
    return f"""#!/usr/bin/env bash
set -euo pipefail

# --- set working directory to this script's folder
cd "$(dirname "$0")"

# --- ensure portable folders exist
mkdir -p data logs config docs

echo "[Chechy] Starting..."
{entry_cmd}

# if the command returns non-zero, bash will exit due to set -e
"""


def normalize_entry_for_platform(entry: str, platform_label: str, auto_detect_cmd: str) -> str:
    """
    Converts entry command to platform-specific form.
    - For windows exe path: .\\app\\x.exe
    - For sh: ./app/x or python app/main.py etc.
    """
    cmd = entry if entry != "auto" else auto_detect_cmd
    if not cmd:
        raise RuntimeError(
            "Could not auto-detect entrypoint. Provide --entry explicitly, e.g.:\n"
            "  --entry \"python app/main.py\"  OR  --entry \"node app/server.js\"  OR  --entry \"app/chechy\""
        )

    if platform_label == "windows":
        # If it's a relative path pointing to app/, keep slashes but prefer backslashes for .exe direct call.
        if cmd.startswith("app/") and cmd.endswith(".exe"):
            cmd = cmd.replace("/", "\\")
            cmd = f".\\{cmd}"
        elif cmd.startswith("./app/") and cmd.endswith(".exe"):
            cmd = cmd.replace("/", "\\").replace(".\\", "")
            cmd = f".\\{cmd}"
        return cmd

    # linux/macos
    # If it's an exe-like entry with backslashes, normalize
    cmd = cmd.replace("\\", "/")
    # If direct app binary (no spaces) and starts with app/, make it executable-friendly
    if " " not in cmd and cmd.startswith("app/"):
        cmd = f"./{cmd}"
    return cmd


def chmod_x(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def zip_folder(folder: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_dir():
                continue
            arcname = p.relative_to(folder.parent)  # include folder name in zip
            z.write(p, arcname.as_posix())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()

    src = Path(args.src).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    platform_label = detect_platform_label(args.platform)

    pkg_root = out / args.name
    safe_rmtree(pkg_root)
    ensure_dirs(pkg_root)

    # Copy app into ./app
    copy_tree(src, pkg_root / "app")

    # Detect entrypoint
    kind, auto_cmd = detect_entry(pkg_root / "app")
    entry_cmd = normalize_entry_for_platform(args.entry, platform_label, auto_cmd)

    # Write run scripts
    run_bat = pkg_root / "run.bat"
    run_sh = pkg_root / "run.sh"
    write_text(run_bat, make_run_bat(entry_cmd))
    write_text(run_sh, make_run_sh(entry_cmd))

    # On unix, ensure run.sh is executable
    try:
        chmod_x(run_sh)
    except Exception:
        # Not fatal on Windows
        pass

    # settings.json defaults
    settings_path = pkg_root / "config" / "settings.json"
    write_json_if_missing(settings_path, DEFAULT_SETTINGS)

    # docs + version
    write_text(pkg_root / "docs" / "README.txt", README_TEXT)
    write_text(pkg_root / "version.txt", f"{args.version}\n")

    # Create zip artifact
    zip_name = f"{args.name}-v{args.version}-{platform_label}.zip"
    zip_path = out / zip_name
    zip_folder(pkg_root, zip_path)

    # Optional SHA256
    if args.with_sha256:
        sums = out / "SHA256SUMS.txt"
        digest = sha256_file(zip_path)
        line = f"{digest}  {zip_name}\n"
        # append or create
        with sums.open("a", encoding="utf-8") as f:
            f.write(line)

    # Deterministic verification hints (printed)
    print("=== CHECHY PORTABLE BUILD OK ===")
    print(f"Source:    {src}")
    print(f"Package:   {pkg_root}")
    print(f"Zip:       {zip_path}")
    if args.with_sha256:
        print(f"SHA256:    {sha256_file(zip_path)}")
    print("")
    print("Next checks (manual but deterministic):")
    print(f"1) Extract: {zip_path} into a NEW folder")
    print("2) Run:")
    if platform_label == "windows":
        print("   - double-click run.bat")
    else:
        print("   - chmod +x run.sh && ./run.sh")
    print("3) Confirm it creates/uses ONLY ./data ./logs ./config inside the extracted folder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
