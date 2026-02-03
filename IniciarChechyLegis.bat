@echo off
title ChechyLegis - Archivo Virtual de Procesos Judiciales
color 0B

echo ============================================================
echo   CHECHYLEGIS - ARCHIVO VIRTUAL DE PROCESOS JUDICIALES
echo ============================================================
echo.
echo   Iniciando servidor...
echo.

cd /d "%~dp0"

REM Verificar si existe la carpeta app
if not exist "app" (
    echo ERROR: No se encuentra la carpeta 'app'
    echo Asegurate de ejecutar este archivo desde la carpeta del proyecto
    pause
    exit /b 1
)

REM Verificar .env
if not exist ".env" (
    echo ADVERTENCIA: No se encuentra el archivo .env
    echo Las funciones de IA no estaran disponibles.
    echo.
)

echo Iniciando servidor FastAPI...
echo URL: http://127.0.0.1:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor
start "" http://127.0.0.1:8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
