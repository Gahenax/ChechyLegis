@echo off
echo ========================================
echo CONFIGURACION DE GIT PARA CHECHYLEGIS
echo ========================================
echo.

echo PASO 1: Configurar tu identidad en Git
echo.
set /p nombre="Ingresa tu nombre: "
set /p email="Ingresa tu email: "

git config --global user.name "%nombre%"
git config --global user.email "%email%"

echo.
echo ✅ Identidad configurada correctamente
echo.

echo PASO 2: Hacer commit inicial
git commit -m "Initial commit: Archivo Virtual de Procesos Judiciales con IA (Gemini)"

echo.
echo ✅ Commit realizado
echo.

echo ========================================
echo PROXIMOS PASOS MANUALES:
echo ========================================
echo.
echo 1. Ve a: https://github.com/new
echo 2. Nombre del repositorio: ChechyLegis
echo 3. Descripcion: Archivo Virtual de Procesos Judiciales con IA (Gemini)
echo 4. NO marques README, .gitignore, o licencia
echo 5. Click en "Create repository"
echo.
echo 6. Luego ejecuta estos comandos (REEMPLAZA TU_USUARIO):
echo.
echo    git remote add origin https://github.com/TU_USUARIO/ChechyLegis.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo ========================================
pause
