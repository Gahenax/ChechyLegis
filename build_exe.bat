@echo off
REM ============================================
REM Script de Construcción de ChechyLegis
REM Genera el ejecutable empaquetado
REM ============================================

echo.
echo ========================================
echo   ChechyLegis - Build Script
echo   Construccion del Ejecutable
echo ========================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo [1/6] Verificando dependencias...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando PyInstaller...
    pip install pyinstaller
)

echo.
echo [2/6] Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "app\__pycache__" rmdir /s /q "app\__pycache__"

echo.
echo [3/6] Instalando dependencias del proyecto...
pip install -r requirements.txt

echo.
echo [4/6] Construyendo ejecutable con PyInstaller...
pyinstaller ChechyLegis.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] La construccion fallo
    pause
    exit /b 1
)

echo.
echo [5/6] Copiando archivos adicionales...
if not exist "dist\ChechyLegis\.env.example" (
    copy ".env.example" "dist\ChechyLegis\.env.example"
)
if not exist "dist\ChechyLegis\README.md" (
    copy "README.md" "dist\ChechyLegis\README.md"
)

echo.
echo [6/6] Verificando resultado...
if exist "dist\ChechyLegis\ChechyLegis.exe" (
    echo.
    echo ========================================
    echo   BUILD EXITOSO!
    echo ========================================
    echo.
    echo Ejecutable creado en: dist\ChechyLegis\
    echo.
    echo Archivos generados:
    dir /b "dist\ChechyLegis"
    echo.
    echo Para crear el instalador, ejecuta:
    echo   build_installer.bat
    echo.
) else (
    echo.
    echo [ERROR] No se pudo crear el ejecutable
    pause
    exit /b 1
)

pause
