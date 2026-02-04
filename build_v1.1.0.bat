@echo off
echo Building ChechyLegis v1.1.0 Release...
set VERSION=v1.1.0-windows

REM 1. Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 2. Run PyInstaller
echo Running PyInstaller...
pyinstaller ChechyLegis.spec --noconfirm --clean

REM 3. Create ZIP
echo Creating ZIP archive...
powershell Compress-Archive -Path "dist\ChechyLegis" -DestinationPath "Chechy-%VERSION%.zip" -Force

REM 4. Generate SHA256
echo Generating Checksum...
powershell Get-FileHash -Algorithm SHA256 "Chechy-%VERSION%.zip" > SHA256_%VERSION%.txt

echo.
echo Build Complete!
echo ZIP: Chechy-%VERSION%.zip
type SHA256_%VERSION%.txt
