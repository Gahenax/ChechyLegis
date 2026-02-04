@echo off
REM ============================================
REM Script de Creación del Instalador
REM Genera el instalador .exe con Inno Setup
REM ============================================

echo.
echo ========================================
echo   ChechyLegis - Installer Builder
echo   Creacion del Instalador
echo ========================================
echo.

REM Verificar que el ejecutable existe
if not exist "dist\ChechyLegis\ChechyLegis.exe" (
    echo [ERROR] El ejecutable no existe
    echo Por favor ejecuta primero: build_exe.bat
    pause
    exit /b 1
)

REM Buscar Inno Setup en ubicaciones comunes
set INNO_SETUP=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP="C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set INNO_SETUP="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)

if %INNO_SETUP%=="" (
    echo.
    echo [ERROR] Inno Setup no esta instalado
    echo.
    echo Por favor descarga e instala Inno Setup desde:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo [1/3] Verificando archivos necesarios...
if not exist "LICENSE.txt" (
    echo [INFO] Creando LICENSE.txt...
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright (c) 2026 ChechyLegis Team >> LICENSE.txt
)

if not exist "INSTALACION_INFO.txt" (
    echo [INFO] Creando INSTALACION_INFO.txt...
    (
        echo ChechyLegis - Archivo Virtual de Procesos Judiciales con IA
        echo.
        echo Bienvenido al instalador de ChechyLegis.
        echo.
        echo Este software le permitira gestionar procesos judiciales
        echo con capacidades avanzadas de Inteligencia Artificial.
        echo.
        echo Requisitos:
        echo - Windows 10 o superior
        echo - 500 MB de espacio en disco
        echo - Conexion a Internet para funciones de IA
        echo.
        echo Despues de la instalacion, debera configurar su API Key
        echo de Google Gemini en el archivo .env
        echo.
        echo Para mas informacion, consulte README.md
    ) > INSTALACION_INFO.txt
)

echo.
echo [2/3] Creando directorio de instaladores...
if not exist "installers" mkdir "installers"

echo.
echo [3/3] Compilando instalador con Inno Setup...
%INNO_SETUP% installer.iss

if errorlevel 1 (
    echo.
    echo [ERROR] La creacion del instalador fallo
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALADOR CREADO EXITOSAMENTE!
echo ========================================
echo.
echo El instalador se encuentra en:
echo   installers\ChechyLegis_Setup_v1.0.0.exe
echo.
echo Tamano del instalador:
for %%A in ("installers\ChechyLegis_Setup_v*.exe") do echo   %%~zA bytes
echo.
echo Ya puedes distribuir este instalador!
echo.

pause
