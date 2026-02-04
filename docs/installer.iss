; Script de Inno Setup para ChechyLegis
; Crea un instalador profesional de Windows

#define MyAppName "ChechyLegis"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ChechyLegis Team"
#define MyAppURL "https://github.com/yourusername/ChechyLegis"
#define MyAppExeName "ChechyLegis.exe"
#define MyAppIcon "icon.ico"

[Setup]
; Información de la aplicación
AppId={{8F9A2B3C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALACION_INFO.txt
OutputDir=installers
OutputBaseFilename=ChechyLegis_Setup_v{#MyAppVersion}
SetupIconFile={#MyAppIcon}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Iniciar ChechyLegis al arrancar Windows"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Files]
; Ejecutable principal y archivos de la aplicación
Source: "dist\ChechyLegis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Iconos del menú de inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{group}\Configuración"; Filename: "notepad.exe"; Parameters: "{app}\.env"; IconFilename: "{sys}\shell32.dll"; IconIndex: 70
Name: "{group}\Documentación"; Filename: "{app}\README.md"; IconFilename: "{sys}\shell32.dll"; IconIndex: 71
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Icono del escritorio
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: desktopicon

; Icono de inicio rápido
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Ejecutar después de la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Código Pascal para funcionalidades avanzadas

// Verificar si .NET Framework está instalado (si es necesario)
function IsDotNetInstalled(): Boolean;
begin
  Result := True; // Modificar según necesidades
end;

// Crear archivo .env si no existe
procedure CreateEnvFile();
var
  EnvFile: string;
  EnvExampleFile: string;
begin
  EnvFile := ExpandConstant('{app}\.env');
  EnvExampleFile := ExpandConstant('{app}\.env.example');
  
  if not FileExists(EnvFile) then
  begin
    if FileExists(EnvExampleFile) then
      FileCopy(EnvExampleFile, EnvFile, False);
  end;
end;

// Después de la instalación
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateEnvFile();
  end;
end;

// Antes de desinstalar
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DbFile: string;
  EnvFile: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    DbFile := ExpandConstant('{app}\judicial_archive.db');
    EnvFile := ExpandConstant('{app}\.env');
    
    // Preguntar si desea conservar la base de datos
    if FileExists(DbFile) then
    begin
      if MsgBox('¿Desea conservar la base de datos de procesos judiciales?', mbConfirmation, MB_YESNO) = IDNO then
        DeleteFile(DbFile);
    end;
    
    // Preguntar si desea conservar la configuración
    if FileExists(EnvFile) then
    begin
      if MsgBox('¿Desea conservar la configuración (API keys)?', mbConfirmation, MB_YESNO) = IDNO then
        DeleteFile(EnvFile);
    end;
  end;
end;

[UninstallDelete]
; Limpiar archivos temporales
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.pyc"
Type: filesandordirs; Name: "{app}\*.log"
