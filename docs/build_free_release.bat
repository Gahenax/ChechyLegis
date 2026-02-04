@echo off
echo Building ChechyLegis FREE Distributable...
set VERSION=1.0.0-FREE

REM 1. Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 2. Run PyInstaller
pyinstaller ChechyLegis.spec --noconfirm --clean

REM 3. Create ZIP
powershell Compress-Archive -Path "dist\ChechyLegis" -DestinationPath "ChechyLegis_FREE_%VERSION%.zip" -Force

REM 4. Generate SHA256
powershell Get-FileHash -Algorithm SHA256 "ChechyLegis_FREE_%VERSION%.zip" > SHA256_FREE.txt

echo.
echo Build Complete!
echo ZIP: ChechyLegis_FREE_%VERSION%.zip
echo SHA256: 
type SHA256_FREE.txt
