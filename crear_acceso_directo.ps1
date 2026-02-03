# Script para crear acceso directo de ChechyLegis con icono de balanza

$SourcePath = "$PSScriptRoot\IniciarChechyLegis.bat"
$DestinationPath = "$env:USERPROFILE\Desktop\ChechyLegis.lnk"
$IconPath = "$PSScriptRoot\icon.png"

# Crear objeto WScript Shell
$WScriptShell = New-Object -ComObject WScript.Shell

# Crear el acceso directo
$Shortcut = $WScriptShell.CreateShortcut($DestinationPath)
$Shortcut.TargetPath = $SourcePath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Archivo Virtual de Procesos Judiciales con IA"
$Shortcut.WindowStyle = 1

# Intentar asignar el icono (PNG no es soportado directamente, necesita ICO)
# Por ahora usamos el icono por defecto del .bat
# $Shortcut.IconLocation = "$IconPath,0"

$Shortcut.Save()

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ACCESO DIRECTO CREADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ubicacion: $DestinationPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Nota: Para usar el icono de balanza personalizado," -ForegroundColor Gray
Write-Host "      necesitas convertir icon.png a icon.ico" -ForegroundColor Gray
Write-Host ""
Write-Host "Puedes usar una herramienta online como:" -ForegroundColor Gray
Write-Host "https://convertio.co/es/png-ico/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Luego, haz clic derecho en el acceso directo > Propiedades" -ForegroundColor Gray
Write-Host "> Cambiar icono > Examinar > Selecciona icon.ico" -ForegroundColor Gray
Write-Host ""

Read-Host "Presiona Enter para continuar"
