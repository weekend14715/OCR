; Vietnamese OCR Tool - Inno Setup Script with Code Signing
; Tác giả: Vietnamese OCR Tool
; Mô tả: Script cài đặt có chữ ký số cho ứng dụng OCR tiếng Việt

#define MyAppName "Vietnamese OCR Tool"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Vietnamese OCR Team"
#define MyAppURL "https://github.com/yourusername/vietnamese-ocr-tool"
#define MyAppExeName "ocr_tool.exe"
#define MyAppIcon "app_icon.ico"

[Setup]
; Thông tin cơ bản
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=VietnameseOCRTool_Setup_v{#MyAppVersion}
SetupIconFile={#MyAppIcon}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppIcon}

; ============================================
; CODE SIGNING - Chữ ký số
; ============================================
; Ký file cài đặt (setup.exe)
; SignTool=signtool sign /f "MyCert.pfx" /p "123456" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /d "OCR License System Setup" /du "https://github.com/your-repo" $f
; Ký các file bên trong gói cài đặt
SignedUninstaller=no

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
Source: "dist\ocr_tool.exe"; DestDir: "{app}"; Flags: ignoreversion

; Icon
Source: "{#MyAppIcon}"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Tesseract OCR và dữ liệu
Source: "Tesseract-OCR\*"; DestDir: "{app}\Tesseract-OCR"; Flags: ignoreversion recursesubdirs createallsubdirs

; File dữ liệu tiếng Việt
Source: "tesseract-main\tessdata\vie.traineddata"; DestDir: "{app}\Tesseract-OCR\tessdata"; Flags: ignoreversion

; Các file cấu hình bổ sung (nếu có)
Source: "tesseract-main\tessdata\configs\*"; DestDir: "{app}\Tesseract-OCR\tessdata\configs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Thư mục license
Source: "license\*"; DestDir: "{app}\license"; Flags: ignoreversion recursesubdirs createallsubdirs

; License file (nếu có)
Source: ".lic"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: ".checksum"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
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

