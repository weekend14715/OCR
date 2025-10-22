; Vietnamese OCR Tool - Inno Setup Script
; Tác giả: Vietnamese OCR Tool
; Mô tả: Script cài đặt cho ứng dụng OCR tiếng Việt

#define MyAppName "Vietnamese OCR Tool"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Vietnamese OCR Team"
#define MyAppExeName "ocr_tool.exe"
#define MyAppIcon "app_icon.ico"

[Setup]
; Thông tin cơ bản
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=VietnameseOCRTool_Setup
SetupIconFile={#MyAppIcon}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppIcon}

; Ngôn ngữ
ShowLanguageDialog=no

; Thư mục cài đặt
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "startup"; Description: "Launch at Windows startup"; GroupDescription: "Startup options:"

[Files]
; File thực thi chính (giả sử bạn đã build bằng PyInstaller)
Source: "dist\ocr_tool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icon
Source: "{#MyAppIcon}"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Tesseract OCR và dữ liệu
Source: "Tesseract-OCR\*"; DestDir: "{app}\Tesseract-OCR"; Flags: ignoreversion recursesubdirs createallsubdirs

; File dữ liệu tiếng Việt
Source: "tesseract-main\tessdata\vie.traineddata"; DestDir: "{app}\Tesseract-OCR\tessdata"; Flags: ignoreversion

; Các file cấu hình bổ sung (nếu có)
Source: "tesseract-main\tessdata\configs\*"; DestDir: "{app}\Tesseract-OCR\tessdata\configs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "tesseract-main\tessdata\tessconfigs\*"; DestDir: "{app}\Tesseract-OCR\tessdata\tessconfigs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "tesseract-main\tessdata\pdf.ttf"; DestDir: "{app}\Tesseract-OCR\tessdata"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: desktopicon

[Registry]
; Thêm vào registry để chạy cùng Windows (nếu được chọn)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --startup"; Flags: uninsdeletevalue; Tasks: startup

[Run]
; Launch application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Xóa file cấu hình khi gỡ cài đặt
Type: filesandordirs; Name: "{localappdata}\VietnameseOCRTool"

[Code]
procedure InitializeWizard;
begin
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;

