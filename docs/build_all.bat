@echo off
REM ============================================
REM Script Maestro de Construcción Completa
REM Ejecuta todo el proceso de build + instalador
REM ============================================

echo.
echo ========================================
echo   ChechyLegis - Build Completo
echo   Ejecutable + Instalador
echo ========================================
echo.

echo Este script realizara:
echo   1. Construccion del ejecutable (PyInstaller)
echo   2. Creacion del instalador (Inno Setup)
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM Paso 1: Construir ejecutable
echo.
echo ========================================
echo   PASO 1: Construyendo Ejecutable
echo ========================================
call build_exe.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la construccion del ejecutable
    pause
    exit /b 1
)

REM Paso 2: Crear instalador
echo.
echo ========================================
echo   PASO 2: Creando Instalador
echo ========================================
call build_installer.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la creacion del instalador
    pause
    exit /b 1
)

echo.
echo ========================================
echo   PROCESO COMPLETO EXITOSO!
echo ========================================
echo.
echo Archivos generados:
echo   - Ejecutable: dist\ChechyLegis\ChechyLegis.exe
echo   - Instalador: installers\ChechyLegis_Setup_v1.0.0.exe
echo.
echo El proyecto esta listo para distribucion!
echo.

pause
