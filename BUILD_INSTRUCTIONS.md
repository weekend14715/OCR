# Hướng dẫn đóng gói ứng dụng Vietnamese OCR Tool

## Yêu cầu

### 1. Phần mềm cần thiết
- **Python 3.8+** đã cài đặt
- **PyInstaller** để đóng gói Python thành EXE
- **Inno Setup 6** để tạo installer
- **Tesseract OCR** đã cài đặt trên máy

### 2. Thư viện Python
Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Các bước đóng gói

### Bước 1: Chuẩn bị file icon.png

Ứng dụng cần file `icon.png`. Bạn có thể:
- Tạo file icon.png (khuyến nghị 64x64 hoặc 128x128 pixels)
- Hoặc chuyển đổi từ `app_icon.ico` sang PNG

**Chuyển đổi ICO sang PNG (nếu cần):**
```python
from PIL import Image
img = Image.open('app_icon.ico')
img.save('icon.png')
```

### Bước 2: Build ứng dụng Python thành EXE

Chạy lệnh sau để đóng gói Python script:

```bash
pyinstaller --name="ocr_tool" ^
  --onedir ^
  --windowed ^
  --icon="app_icon.ico" ^
  --add-data="icon.png;." ^
  --hidden-import="PIL._tkinter_finder" ^
  ocr_tool.py
```

**Giải thích các tham số:**
- `--name="ocr_tool"`: Tên file exe
- `--onedir`: Tạo thư mục chứa exe và các file đi kèm
- `--windowed`: Không hiển thị cửa sổ console (cho ứng dụng GUI)
- `--icon`: Icon cho file exe
- `--add-data`: Thêm file icon.png vào package
- `--hidden-import`: Import các module ẩn cần thiết

Sau khi chạy xong, bạn sẽ có thư mục `dist/ocr_tool/` chứa file exe và các dependencies.

### Bước 3: Chuẩn bị Tesseract OCR

**Tùy chọn A: Copy từ cài đặt hiện tại**
```bash
xcopy "C:\Program Files\Tesseract-OCR" "Tesseract-OCR\" /E /I /H /Y
```

**Tùy chọn B: Tải Tesseract Portable**
1. Tải Tesseract Windows từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Giải nén vào thư mục `Tesseract-OCR/`

**Quan trọng:** Đảm bảo có file `vie.traineddata` cho tiếng Việt:
- File này đã có sẵn trong `tesseract-main/tessdata/vie.traineddata`
- Hoặc tải từ: https://github.com/tesseract-ocr/tessdata

### Bước 4: Cấu trúc thư mục chuẩn bị

Trước khi chạy Inno Setup, đảm bảo cấu trúc như sau:

```
OCR/
├── dist/
│   └── ocr_tool/          # Folder được tạo bởi PyInstaller
│       ├── ocr_tool.exe
│       ├── icon.png
│       └── ... (các file dll, pyd khác)
├── Tesseract-OCR/         # Thư mục Tesseract
│   ├── tesseract.exe
│   ├── tessdata/
│   │   ├── vie.traineddata
│   │   ├── configs/
│   │   └── tessconfigs/
│   └── ... (các file dll)
├── tesseract-main/        # Source code Tesseract (đã có)
├── app_icon.ico
├── icon.png
└── setup.iss              # Script Inno Setup
```

### Bước 5: Biên dịch với Inno Setup

**Phương pháp 1: Qua GUI**
1. Mở **Inno Setup Compiler**
2. File → Open → Chọn `setup.iss`
3. Build → Compile (hoặc nhấn Ctrl+F9)

**Phương pháp 2: Qua Command Line**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

### Bước 6: Lấy file cài đặt

Sau khi compile thành công, file installer sẽ nằm trong:
```
Output/VietnameseOCRTool_Setup.exe
```

## Kiểm tra và triển khai

### Kiểm tra trên máy khác
1. Copy file `VietnameseOCRTool_Setup.exe` sang máy khác
2. Chạy installer
3. Kiểm tra các chức năng:
   - Ứng dụng khởi động bình thường
   - Có thể đặt phím tắt
   - OCR hoạt động chính xác với tiếng Việt
   - Icon hiển thị trên system tray

### Các vấn đề thường gặp

**Lỗi 1: "Tesseract is not installed"**
- Kiểm tra file `tesseract.exe` có trong `{app}\Tesseract-OCR\`
- Kiểm tra đường dẫn trong code `ocr_tool.py` (dòng 28)

**Lỗi 2: "Failed to load language 'vie'"**
- Kiểm tra file `vie.traineddata` có trong `{app}\Tesseract-OCR\tessdata\`
- Đảm bảo file không bị corrupt

**Lỗi 3: "icon.png not found"**
- Đảm bảo file icon.png có trong thư mục `dist/ocr_tool/`
- Kiểm tra lại lệnh PyInstaller với `--add-data`

**Lỗi 4: Ứng dụng không chạy cùng Windows**
- Kiểm tra trong Registry: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Hoặc gỡ cài đặt và cài lại, chọn option "Chạy cùng Windows"

## Tùy chỉnh

### Thay đổi thông tin ứng dụng
Sửa trong file `setup.iss`:
```pascal
#define MyAppName "Vietnamese OCR Tool"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Vietnamese OCR Team"
```

### Thay đổi icon
- Thay thế file `app_icon.ico` và `icon.png`
- Build lại với PyInstaller

### Thêm ngôn ngữ khác
Thêm file `.traineddata` khác vào `Tesseract-OCR/tessdata/`:
- `eng.traineddata` - Tiếng Anh
- `chi_sim.traineddata` - Tiếng Trung giản thể
- Xem danh sách đầy đủ: https://github.com/tesseract-ocr/tessdata

## Giấy phép

Lưu ý về giấy phép khi phân phối:
- **Tesseract OCR**: Apache License 2.0
- **Python**: Python Software Foundation License
- Các thư viện khác: Kiểm tra giấy phép của từng thư viện

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Log files trong `%LOCALAPPDATA%\VietnameseOCRTool\`
2. Event Viewer của Windows
3. Chạy file exe từ Command Prompt để xem error messages

