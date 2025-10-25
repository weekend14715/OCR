# 📦 Hướng Dẫn Build Installer với Inno Setup

Hướng dẫn chi tiết cách tạo file cài đặt có chữ ký số cho Vietnamese OCR Tool.

---

## 🎯 Tổng Quan

File cài đặt sẽ có:
- ✅ Chữ ký số (Code Signing) để tránh cảnh báo Windows SmartScreen
- ✅ Giao diện cài đặt chuyên nghiệp
- ✅ Tự động cài đặt Tesseract OCR và dữ liệu tiếng Việt
- ✅ Tạo shortcuts trên Desktop và Start Menu
- ✅ Tùy chọn chạy cùng Windows
- ✅ Uninstaller đầy đủ

---

## 📋 Yêu Cầu

### 1. Inno Setup 6
- **Tải từ:** https://jrsoftware.org/isdl.php
- **Phiên bản:** 6.x trở lên
- **Cài đặt:** Chạy installer và làm theo hướng dẫn

### 2. Windows SDK (cho SignTool)
- **Tải từ:** https://developer.microsoft.com/windows/downloads/windows-sdk/
- **Cần thiết cho:** Ký file với chữ ký số
- **Bao gồm:** SignTool.exe

### 3. Certificate (Chứng chỉ số)
Có 2 lựa chọn:

#### Option A: Self-Signed Certificate (Miễn phí, cho testing)
```powershell
.\create_self_signed_cert.ps1
```

**Ưu điểm:**
- ✅ Miễn phí
- ✅ Tạo ngay lập tức
- ✅ Đủ để ký file

**Nhược điểm:**
- ❌ Vẫn có cảnh báo SmartScreen ban đầu
- ❌ Người dùng phải trust certificate thủ công
- ❌ Chỉ nên dùng cho testing

#### Option B: Commercial Certificate (Trả phí, cho production)
Mua từ các nhà cung cấp uy tín:

**Nhà cung cấp phổ biến:**
1. **DigiCert** (khuyến nghị)
   - Website: https://www.digicert.com/
   - Giá: ~$300-500/năm
   - Thời gian xử lý: 1-3 ngày làm việc
   - Trust ngay lập tức

2. **Sectigo (Comodo)**
   - Website: https://sectigo.com/
   - Giá: ~$200-400/năm
   - Thời gian xử lý: 1-2 ngày làm việc

3. **GlobalSign**
   - Website: https://www.globalsign.com/
   - Giá: ~$250-450/năm
   - Thời gian xử lý: 1-3 ngày làm việc

**Lưu ý quan trọng:**
- 🔒 Certificate cho Windows phải là **"Code Signing Certificate"**
- 📝 Cần xác minh danh tính công ty/cá nhân
- ⏱️ SmartScreen vẫn có thể cảnh báo với certificate mới (cần tích lũy reputation)

### 4. Python & PyInstaller
```bash
pip install pyinstaller
```

---

## 🚀 Cách Sử Dụng

### Method 1: Tự Động (Khuyến nghị)

#### Bước 1: Build và Ký (Có chữ ký)
```bash
# Right-click và chọn "Run as Administrator"
build_installer.bat
```

Script sẽ tự động:
1. ✅ Kiểm tra các công cụ cần thiết
2. ✅ Build app với PyInstaller
3. ✅ Ký file EXE chính
4. ✅ Build Installer với Inno Setup
5. ✅ Ký file Setup
6. ✅ Xác minh chữ ký

#### Bước 2: Nhập Mật Khẩu Certificate
Khi được hỏi, nhập mật khẩu của file `MyCert.pfx`.

#### Bước 3: Nhận File Cài Đặt
File sẽ được tạo trong thư mục `Output`:
```
Output/VietnameseOCRTool_Setup_v1.0.0.exe
```

### Method 2: PowerShell (Có Options)

#### Build với Signing (Mặc định)
```powershell
.\build_installer.ps1
```

#### Build không Signing (Nếu chưa có cert)
```powershell
.\build_installer.ps1 -SkipSigning
```

#### Build không PyInstaller (Nếu đã build rồi)
```powershell
.\build_installer.ps1 -SkipBuild
```

#### Truyền mật khẩu certificate
```powershell
.\build_installer.ps1 -CertPassword "your_password_here"
```

### Method 3: Thủ Công (Advanced)

#### 1. Build App với PyInstaller
```bash
pyinstaller ocr_tool.spec --clean --noconfirm
```

#### 2. Ký File EXE (nếu có cert)
```bash
signtool sign ^
  /f MyCert.pfx ^
  /p YOUR_PASSWORD ^
  /fd SHA256 ^
  /tr http://timestamp.digicert.com ^
  /td SHA256 ^
  /d "Vietnamese OCR Tool" ^
  dist\ocr_tool\ocr_tool.exe
```

#### 3. Build Installer với Inno Setup
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

---

## 📁 Cấu Trúc File

### File Chính
```
vietnamese-ocr-tool/
├── setup.iss                    # Inno Setup script (đã có signing config)
├── build_installer.ps1          # PowerShell script tự động
├── build_installer.bat          # Batch file chạy nhanh
├── MyCert.pfx                   # Certificate file (cần tạo/mua)
├── ocr_tool.py                  # Source code chính
├── ocr_tool.spec                # PyInstaller config
├── app_icon.ico                 # Icon ứng dụng
├── Tesseract-OCR/               # Tesseract engine
├── tesseract-main/              # Dữ liệu tiếng Việt
└── Output/                      # Thư mục chứa file setup (tự tạo)
    └── VietnameseOCRTool_Setup_v1.0.0.exe
```

---

## 🔧 Tùy Chỉnh

### 1. Thay Đổi Thông Tin App

Sửa file `setup.iss`:
```iss
#define MyAppName "Vietnamese OCR Tool"
#define MyAppVersion "1.0.0"              ; ← Thay đổi version
#define MyAppPublisher "Vietnamese OCR Team"  ; ← Thay đổi tên công ty
#define MyAppURL "https://your-website.com"   ; ← Thay đổi URL
```

### 2. Thay Đổi Icon

Thay thế file `app_icon.ico` bằng icon của bạn (khuyến nghị: 256x256px).

### 3. Thêm File Vào Installer

Sửa phần `[Files]` trong `setup.iss`:
```iss
[Files]
Source: "your_file.txt"; DestDir: "{app}"; Flags: ignoreversion
```

### 4. Thêm Registry Keys

Sửa phần `[Registry]` trong `setup.iss`:
```iss
[Registry]
Root: HKLM; Subkey: "Software\YourCompany\YourApp"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
```

---

## ✅ Xác Minh Chữ Ký

### Cách 1: Qua File Properties
1. Right-click file `VietnameseOCRTool_Setup_v1.0.0.exe`
2. Chọn **Properties**
3. Tab **Digital Signatures**
4. Kiểm tra thông tin chữ ký

### Cách 2: Qua SignTool
```bash
signtool verify /pa /v Output\VietnameseOCRTool_Setup_v1.0.0.exe
```

**Kết quả mong đợi:**
```
Successfully verified: Output\VietnameseOCRTool_Setup_v1.0.0.exe
```

### Cách 3: Qua PowerShell
```powershell
Get-AuthenticodeSignature "Output\VietnameseOCRTool_Setup_v1.0.0.exe"
```

---

## 🐛 Xử Lý Lỗi

### Lỗi 1: "Inno Setup not found"
**Nguyên nhân:** Chưa cài Inno Setup hoặc đường dẫn không đúng.

**Giải pháp:**
1. Cài Inno Setup từ https://jrsoftware.org/isdl.php
2. Hoặc sửa đường dẫn trong `build_installer.ps1`:
```powershell
$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

### Lỗi 2: "SignTool not found"
**Nguyên nhân:** Chưa cài Windows SDK.

**Giải pháp:**
1. Cài Windows SDK
2. Hoặc build không signing:
```powershell
.\build_installer.ps1 -SkipSigning
```

### Lỗi 3: "Certificate password incorrect"
**Nguyên nhân:** Mật khẩu certificate sai.

**Giải pháp:**
1. Kiểm tra lại mật khẩu
2. Nếu quên, tạo certificate mới:
```powershell
.\create_self_signed_cert.ps1
```

### Lỗi 4: "dist\ocr_tool\ocr_tool.exe not found"
**Nguyên nhân:** Chưa build app với PyInstaller.

**Giải pháp:**
```bash
pyinstaller ocr_tool.spec --clean --noconfirm
```

### Lỗi 5: "Access denied" khi build
**Nguyên nhân:** Cần quyền Administrator.

**Giải pháp:**
Right-click `build_installer.bat` và chọn **"Run as Administrator"**.

---

## 📊 Kích Thước File

**File cài đặt dự kiến:**
- App (PyInstaller): ~50-100 MB
- Tesseract OCR: ~30-50 MB
- Dữ liệu tiếng Việt: ~10-20 MB
- **Tổng cộng:** ~90-170 MB

**Nén với Inno Setup:**
- Với `Compression=lzma2/max`: ~60-100 MB
- Thời gian nén: 1-3 phút

---

## 🎯 Best Practices

### 1. Testing
```bash
# Test trên máy mới/máy ảo
- ✅ Windows 10 (64-bit)
- ✅ Windows 11
- ✅ Máy không có Python
- ✅ Máy không có Tesseract
```

### 2. Version Control
- Tăng version sau mỗi release
- Đặt tên file theo format: `YourApp_Setup_v1.0.0.exe`

### 3. Distribution
- Host trên website chính thức
- Tính toán băng thông: file_size × số_lượng_download
- Cung cấp checksum (SHA256) để người dùng xác minh

### 4. Update Mechanism
- Thêm auto-update checker trong app
- Thông báo khi có phiên bản mới
- Hướng dẫn cách update

---

## 🔐 Bảo Mật Certificate

### ⚠️ QUAN TRỌNG
**KHÔNG BAO GIỜ:**
- ❌ Commit file `.pfx` vào Git
- ❌ Share mật khẩu certificate công khai
- ❌ Để file certificate trên server không mã hóa

**NÊN:**
- ✅ Lưu file `.pfx` an toàn (encrypted backup)
- ✅ Sử dụng mật khẩu mạnh
- ✅ Giới hạn quyền truy cập
- ✅ Revoke certificate ngay nếu bị lộ

### .gitignore
Thêm vào `.gitignore`:
```
# Certificate files
*.pfx
*.p12
*.cer
*.crt
*.key
MyCert.*
```

---

## 📞 Hỗ Trợ

### Nếu Gặp Vấn Đề

1. **Kiểm tra log:** Script sẽ hiển thị lỗi chi tiết
2. **Đọc error message:** Thường có hướng dẫn fix
3. **Google error code:** Nhiều người đã gặp lỗi tương tự
4. **Tạo issue:** Trên GitHub repository

### Tài Liệu Tham Khảo

- **Inno Setup:** https://jrsoftware.org/ishelp/
- **Code Signing:** https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools
- **PyInstaller:** https://pyinstaller.org/

---

## 🎉 Hoàn Thành!

Sau khi build xong, bạn sẽ có:
- ✅ File cài đặt chuyên nghiệp
- ✅ Chữ ký số đầy đủ
- ✅ Giao diện cài đặt đẹp
- ✅ Sẵn sàng phân phối

**File Output:**
```
Output/VietnameseOCRTool_Setup_v1.0.0.exe  (~60-100 MB)
```

**Bước tiếp theo:**
1. Test trên nhiều máy khác nhau
2. Upload lên website/GitHub releases
3. Thông báo cho người dùng
4. Theo dõi feedback

---

*Cập nhật: 2024*
*Phiên bản: 1.0*

