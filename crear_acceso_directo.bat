@echo off
echo ============================================================
echo   CREANDO ACCESO DIRECTO DE CHECHYLEGIS
echo ============================================================
echo.

cd /d "%~dp0"

REM Crear acceso directo en el escritorio usando PowerShell
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\ChechyLegis.lnk'); $SC.TargetPath = '%~dp0IniciarChechyLegis.bat'; $SC.WorkingDirectory = '%~dp0'; $SC.Description = 'Archivo Virtual de Procesos Judiciales con IA'; $SC.Save()"

echo.
echo OK: Acceso directo creado en el escritorio
echo.
echo Ubicacion: %USERPROFILE%\Desktop\ChechyLegis.lnk
echo.
echo NOTA: Para agregar el icono de balanza:
echo   1. Primero ejecuta: python convertir_icono.py
echo   2. Luego clic derecho en el acceso directo ^> Propiedades
echo   3. Click en "Cambiar icono"
echo   4. Click en "Examinar" y selecciona icon.ico
echo   5. Click en Aceptar
echo.

pause
