; Instalator OmniTV dla Windows (Inno Setup 6+)
#define MyAppName "OmniTV"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "1bypl"
#define MyAppExeName "OmniTV.exe"

[Setup]
AppId={{B4E1C2D3-5A6F-47B8-9C0D-1E2F3A4B5C6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\..\dist
OutputBaseFilename=OmniTV-Setup-{#MyAppVersion}
SetupIconFile=omnity.ico
AppPublisherURL=https://github.com/1bypl
AppSupportURL=https://github.com/1bypl
AppUpdatesURL=https://github.com/1bypl
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "Utworz skrot na pulpicie"; GroupDescription: "Dodatkowe ikony:"

[Files]
Source: "..\..\dist\OmniTV\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Odinstaluj {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Uruchom {#MyAppName}"; Flags: nowait postinstall skipifsilent
