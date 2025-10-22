# Vietnamese OCR Tool - Hướng dẫn tạo Installer

## Tóm tắt nhanh

### Cách nhanh nhất (Chỉ 1 lệnh!)

```bash
build_all.bat
```

Script này sẽ tự động:
1. ✅ Cài đặt các thư viện Python cần thiết
2. ✅ Tạo file icon.png (nếu chưa có)
3. ✅ Build Python thành EXE bằng PyInstaller
4. ✅ Copy Tesseract-OCR
5. ✅ Tạo installer bằng Inno Setup

### Yêu cầu trước khi chạy

1. **Python 3.8+** - [Tải tại đây](https://www.python.org/downloads/)
2. **Inno Setup 6** - [Tải tại đây](https://jrsoftware.org/isdl.php)
3. **Tesseract OCR** - [Tải tại đây](https://github.com/UB-Mannheim/tesseract/wiki)

---

## Hướng dẫn chi tiết từng bước

### Bước 1: Chuẩn bị môi trường

```bash
# Cài đặt thư viện Python
pip install -r requirements.txt
pip install pyinstaller

# Tạo icon.png từ app_icon.ico (nếu chưa có)
python -c "from PIL import Image; img = Image.open('app_icon.ico'); img.save('icon.png')"
```

### Bước 2: Build EXE

**Cách 1: Dùng file .spec**
```bash
pyinstaller ocr_tool.spec
```

**Cách 2: Dùng command line**
```bash
pyinstaller --name="ocr_tool" --onedir --windowed --icon="app_icon.ico" --add-data="icon.png;." --hidden-import="PIL._tkinter_finder" ocr_tool.py
```

Kết quả: Thư mục `dist/ocr_tool/` chứa file `ocr_tool.exe`

### Bước 3: Chuẩn bị Tesseract-OCR

**Option A: Copy từ cài đặt hiện tại**
```bash
xcopy "C:\Program Files\Tesseract-OCR" "Tesseract-OCR\" /E /I /H /Y
```

**Option B: Download Portable**
1. Tải Tesseract Windows portable
2. Giải nén vào thư mục `Tesseract-OCR/`
3. Đảm bảo có `tesseract.exe` và `tessdata/vie.traineddata`

### Bước 4: Tạo Installer

**Mở Inno Setup và compile:**
1. Mở `setup.iss` bằng Inno Setup Compiler
2. Nhấn `F9` hoặc Build → Compile
3. Đợi quá trình hoàn tất

**Hoặc dùng command line:**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

### Bước 5: Lấy file cài đặt

File installer sẽ nằm trong:
```
Output/VietnameseOCRTool_Setup.exe
```

Copy file này sang máy khác để cài đặt! 🎉

---

## Cấu trúc thư mục cần thiết

```
OCR/
├── 📁 dist/
│   └── 📁 ocr_tool/          ← Build bởi PyInstaller
│       ├── ocr_tool.exe      ← File chính
│       ├── icon.png
│       └── ... (DLLs, dependencies)
│
├── 📁 Tesseract-OCR/         ← Tesseract engine
│   ├── tesseract.exe
│   ├── 📁 tessdata/
│   │   └── vie.traineddata   ← Dữ liệu tiếng Việt
│   └── ... (DLLs)
│
├── 📁 Output/                ← Inno Setup sẽ tạo folder này
│   └── VietnameseOCRTool_Setup.exe  ← FILE CÀI ĐẶT
│
├── app_icon.ico
├── icon.png
├── ocr_tool.py
├── setup.iss                 ← Script Inno Setup
├── ocr_tool.spec             ← Spec PyInstaller
├── build_all.bat             ← Script tự động
└── requirements.txt
```

---

## Kiểm tra trên máy mới

Sau khi cài đặt trên máy khác, kiểm tra:

✅ **Cài đặt thành công**
- Ứng dụng xuất hiện trong Start Menu
- Icon trên Desktop (nếu chọn)

✅ **Chức năng hoạt động**
- Mở ứng dụng không báo lỗi
- Có thể đặt phím tắt
- OCR nhận dạng được tiếng Việt
- Icon hiển thị trên System Tray

✅ **Tự khởi động (nếu chọn)**
- Kiểm tra Registry: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Restart máy và kiểm tra ứng dụng có tự chạy không

---

## Xử lý lỗi thường gặp

### ❌ "PyInstaller: command not found"
```bash
pip install pyinstaller
```

### ❌ "icon.png not found" khi build
```bash
python -c "from PIL import Image; img = Image.open('app_icon.ico'); img.save('icon.png')"
```

### ❌ "Tesseract not found" khi chạy ứng dụng
- Đảm bảo thư mục `Tesseract-OCR` có trong installer
- Kiểm tra file `setup.iss` dòng `Source: "Tesseract-OCR\*"`

### ❌ "Failed to load language 'vie'"
- Kiểm tra file `vie.traineddata` có trong `tessdata/`
- Download từ: https://github.com/tesseract-ocr/tessdata/raw/main/vie.traineddata

### ❌ Inno Setup không compile được
- Kiểm tra tất cả file trong `[Files]` section có tồn tại
- Đặc biệt là `dist/ocr_tool/*` và `Tesseract-OCR/*`

---

## Tùy chỉnh

### Đổi tên ứng dụng
Sửa trong `setup.iss`:
```pascal
#define MyAppName "Tên Ứng Dụng Của Bạn"
#define MyAppVersion "2.0.0"
```

### Thay đổi icon
1. Thay thế `app_icon.ico` và `icon.png`
2. Build lại với PyInstaller
3. Compile lại với Inno Setup

### Thêm ngôn ngữ OCR khác
1. Download file `.traineddata` từ [Tesseract tessdata](https://github.com/tesseract-ocr/tessdata)
2. Copy vào `Tesseract-OCR/tessdata/`
3. Build lại installer

---

## Giấy phép & Phân phối

Khi phân phối, lưu ý:
- 📜 **Tesseract OCR**: Apache License 2.0
- 📜 **Python**: PSF License
- 📜 Các thư viện khác: Kiểm tra license riêng

---

## Hỗ trợ

📧 **Có vấn đề?**
1. Kiểm tra file log: `%LOCALAPPDATA%\VietnameseOCRTool\`
2. Chạy `ocr_tool.exe` từ Command Prompt để xem lỗi
3. Kiểm tra Event Viewer của Windows

**Phiên bản:** 1.0.0  
**Cập nhật:** 2025

---

🎉 **Chúc bạn tạo installer thành công!**

