; Inno Setup script for LyricsAPP
; Compile with Inno Setup Compiler

#define AppName "LyricsAPP"
#define AppVersion "1.0.0"
#define AppPublisher "Yotzuga"
#define AppExeName "LyricsAPP.exe"

[Setup]
AppId={{B3F74E7F-6C2A-4E7B-9C92-4F2B2A9D7D51}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputBaseFilename=LyricsAPP-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
AppPublisherURL=https://github.com/Yotzuga/LyricsAPP
AppSupportURL=https://github.com/Yotzuga/LyricsAPP/issues
AppUpdatesURL=https://github.com/Yotzuga/LyricsAPP/releases
InfoBeforeFile=installer_info.txt

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Soporta build onefile (dist\LyricsAPP.exe) o onedir (dist\LyricsAPP\*)
#ifexist "dist\LyricsAPP.exe"
Source: "dist\LyricsAPP.exe"; DestDir: "{app}"; Flags: ignoreversion
#else
Source: "dist\LyricsAPP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName}"; Flags: nowait postinstall skipifsilent

[Messages]
BeveledLabel=Instalador de {#AppName}
