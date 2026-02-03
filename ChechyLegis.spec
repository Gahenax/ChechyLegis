# -*- mode: python ; coding: utf-8 -*-
"""
Especificación de PyInstaller para ChechyLegis
Genera un ejecutable empaquetado de la aplicación
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

block_cipher = None

# Datos adicionales a incluir
added_files = [
    ('static', 'static'),
    ('app', 'app'),
    ('.env.example', '.'),
    ('icon.ico', '.'),
    ('icon.png', '.'),
    ('README.md', '.'),
]

# Módulos ocultos necesarios
hidden_imports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.ext.baked',
    'google.generativeai',
    'google.ai.generativelanguage',
    'passlib.handlers.bcrypt',
    'jose',
    'multipart',
]

# Análisis del script principal
a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'pytest',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Archivos Python compilados
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Ejecutable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChechyLegis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

# Colección de archivos
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChechyLegis',
)
