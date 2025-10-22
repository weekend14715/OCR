# 📋 Tổng Quan Các File Trong Project

## 🚨 Windows Defender False Positive

Windows Defender phát hiện `ocr_tool.exe` là `Trojan:Win32/Wacatac.B!ml` - Đây là **FALSE POSITIVE**!

---

## 📁 File Structure

### 🔴 CÁC FILE QUAN TRỌNG - ĐỌC NGAY

| File | Mục đích | Khi nào dùng |
|------|----------|--------------|
| **`_START_HERE.txt`** | Hướng dẫn nhanh nhất | Đọc đầu tiên khi gặp Windows Defender |
| **`KHAC_PHUC_NGAY.txt`** | Hướng dẫn khắc phục chi tiết | Windows Defender chặn file |
| **`FIX_WINDOWS_DEFENDER.md`** | Tài liệu đầy đủ về false positive | Cần hiểu sâu về vấn đề |

### 🔧 BUILD SCRIPTS

| File | Chức năng | Khi nào dùng |
|------|-----------|--------------|
| **`Add_Exclusion_Admin.ps1`** | Thêm exclusion tự động | Chạy đầu tiên (cần Admin) |
| **`rebuild_after_exclusion.bat`** | Build sau khi thêm exclusion | Sau khi chạy script PowerShell |
| **`build_safe.bat`** | Build với tùy chọn SAFE (no UPX) | Alternative build method |
| **`build_all.bat`** | Build tất cả (EXE + Installer) | Build phiên bản đầy đủ |
| **`build.bat`** | Build EXE đơn giản | Build nhanh chỉ EXE |

### 📖 DOCUMENTATION

| File | Nội dung | Đối tượng |
|------|----------|-----------|
| **`README.md`** | Tổng quan dự án | Developers |
| **`README_SETUP.md`** | Hướng dẫn setup chi tiết | Developers |
| **`CHO_NGUOI_DUNG_CUOI.txt`** | Hướng dẫn sử dụng | End Users |
| **`HUONG_DAN_NHANH.txt`** | Quick start guide | Developers |
| **`FILES_OVERVIEW.md`** | File này - Tổng quan | All |

### 🐍 PYTHON CODE

| File | Chức năng |
|------|-----------|
| **`ocr_tool.py`** | Code chính của ứng dụng |
| **`create_icon.py`** | Tool convert ICO → PNG |
| **`requirements.txt`** | Python dependencies |

### ⚙️ CONFIG FILES

| File | Mục đích |
|------|----------|
| **`ocr_tool.spec`** | PyInstaller configuration (UPX=False) |
| **`setup.iss`** | Inno Setup installer script |

### 🎨 ASSETS

| File | Loại |
|------|------|
| **`app_icon.ico`** | Icon file (Windows format) |
| **`icon.png`** | Icon file (PNG format, tạo từ .ico) |

---

## 🎯 WORKFLOW KHUYẾN NGHỊ

### Lần đầu build:

```
1. Đọc: _START_HERE.txt
2. Đọc: KHAC_PHUC_NGAY.txt
3. Chạy: Add_Exclusion_Admin.ps1 (as Admin)
4. Chạy: rebuild_after_exclusion.bat
5. Test: dist\ocr_tool\ocr_tool.exe
```

### Build lại sau này:

```
1. Chạy: build_safe.bat
   Hoặc: build_all.bat (tạo cả installer)
```

### Nếu Windows Defender vẫn chặn:

```
1. Đọc: FIX_WINDOWS_DEFENDER.md
2. Kiểm tra exclusion đã thêm chưa
3. Thử tắt Real-time Protection tạm thời
4. Build lại
```

---

## 📦 OUTPUT FILES

### Sau khi build thành công:

```
dist/
└── ocr_tool/
    ├── ocr_tool.exe          ← Executable chính
    ├── icon.png
    ├── app_icon.ico
    ├── Tesseract-OCR/        ← Tesseract runtime
    └── [các DLL khác]
```

### Sau khi build installer:

```
Output/
└── VietnameseOCRTool_Setup.exe   ← Installer cho end users
```

---

## 🛠️ TROUBLESHOOTING

### Windows Defender chặn file

**Files cần đọc:**
1. `_START_HERE.txt` - Quick guide
2. `KHAC_PHUC_NGAY.txt` - Detailed steps
3. `FIX_WINDOWS_DEFENDER.md` - Technical details

**Scripts cần chạy:**
1. `Add_Exclusion_Admin.ps1` - Thêm exclusion
2. `rebuild_after_exclusion.bat` - Build lại

### Build bị lỗi

**Kiểm tra:**
- Python đã cài đúng version chưa (3.8+)
- Đã cài các dependencies chưa: `pip install -r requirements.txt`
- Icon files có tồn tại không: `icon.png`, `app_icon.ico`
- Tesseract đã cài đúng chưa

**Files tham khảo:**
- `README_SETUP.md` - Setup instructions
- `HUONG_DAN_NHANH.txt` - Quick troubleshooting

### Installer không tạo được

**Kiểm tra:**
- Inno Setup 6 đã cài chưa
- File `setup.iss` có đúng không
- Đường dẫn trong `setup.iss` có đúng không

---

## 📊 FILE PRIORITY

### 🔴 HIGH PRIORITY (Phải đọc/chạy)

1. `_START_HERE.txt`
2. `Add_Exclusion_Admin.ps1`
3. `rebuild_after_exclusion.bat`

### 🟡 MEDIUM PRIORITY (Nên đọc)

1. `KHAC_PHUC_NGAY.txt`
2. `FIX_WINDOWS_DEFENDER.md`
3. `README.md`

### 🟢 LOW PRIORITY (Đọc khi cần)

1. `README_SETUP.md`
2. `CHO_NGUOI_DUNG_CUOI.txt`
3. `HUONG_DAN_NHANH.txt`

---

## 🎓 FOR DEVELOPERS

### Muốn hiểu code:
→ Đọc `ocr_tool.py` (có comments đầy đủ)

### Muốn build:
→ Đọc `README_SETUP.md` hoặc `HUONG_DAN_NHANH.txt`

### Muốn fix Windows Defender:
→ Đọc `FIX_WINDOWS_DEFENDER.md`

### Muốn tùy chỉnh build:
→ Sửa `ocr_tool.spec` và `setup.iss`

---

## 👤 FOR END USERS

### Muốn cài đặt app:
→ Đọc `CHO_NGUOI_DUNG_CUOI.txt`

### Gặp Windows Defender warning:
→ Xem phần "Windows Defender chặn file?" trong `CHO_NGUOI_DUNG_CUOI.txt`

### Muốn biết cách dùng:
→ Xem phần "Sử dụng" trong `CHO_NGUOI_DUNG_CUOI.txt`

---

## 💡 TIPS

### Khi build:

✅ **LÀM:**
- Thêm exclusion TRƯỚC KHI build
- Dùng `build_safe.bat` (tắt UPX)
- Clean build folder trước khi build lại
- Kiểm tra icon files tồn tại

❌ **KHÔNG LÀM:**
- Build mà không thêm exclusion
- Dùng UPX compression (sẽ bị chặn chắc chắn)
- Build nhiều lần liên tiếp mà không clean
- Bỏ qua warnings

### Khi phân phối:

✅ **LÀM:**
- Cung cấp file `CHO_NGUOI_DUNG_CUOI.txt`
- Giải thích về Windows Defender false positive
- Hướng dẫn thêm exclusion
- Test trên máy sạch trước

❌ **KHÔNG LÀM:**
- Phân phối mà không warning về Windows Defender
- Bỏ qua documentation
- Không test installer

---

## 🔗 RELATED FILES

### Build Process Chain:

```
Add_Exclusion_Admin.ps1
    ↓
rebuild_after_exclusion.bat
    ↓
ocr_tool.spec
    ↓
PyInstaller
    ↓
dist/ocr_tool/ocr_tool.exe
    ↓
setup.iss
    ↓
Inno Setup
    ↓
Output/VietnameseOCRTool_Setup.exe
```

---

## 📞 SUPPORT FILES

Nếu cần hỗ trợ, gửi kèm:
- Windows version
- Python version: `python --version`
- PyInstaller version: `pyinstaller --version`
- Error logs
- Screenshots of errors

---

**Version:** 1.0.0  
**Updated:** October 21, 2025  
**Purpose:** File navigation guide for Vietnamese OCR Tool project

