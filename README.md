# Vietnamese OCR Tool 🇻🇳

Công cụ OCR (Optical Character Recognition) tối ưu hóa cho tiếng Việt, hỗ trợ chụp và nhận dạng văn bản từ bất kỳ vùng nào trên màn hình.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.8+-green)

## ✨ Tính năng

- 🎯 **Nhận dạng tiếng Việt chính xác** - Sử dụng Tesseract OCR với dữ liệu tiếng Việt
- ⌨️ **Phím tắt tùy chỉnh** - Tự đặt tổ hợp phím yêu thích
- 🖼️ **Chọn vùng màn hình** - Chọn chính xác vùng cần OCR
- 📋 **Tự động copy** - Kết quả tự động copy vào clipboard
- 🎨 **Xử lý ảnh thông minh** - Tối ưu hóa ảnh trước khi OCR
- 🚀 **Chạy nền** - Luôn sẵn sàng trên system tray
- 🔄 **Khởi động cùng Windows** - Tùy chọn tự động khởi động

## 🎨 Xử lý ảnh tối ưu

Ứng dụng tự động áp dụng các kỹ thuật xử lý ảnh:

- ✅ Grayscale conversion (chuyển màu xám)
- ✅ Image upscaling 3x (tăng độ phân giải)
- ✅ Histogram equalization (cân bằng độ sáng)
- ✅ Contrast enhancement (tăng độ tương phản)
- ✅ Sharpness enhancement (tăng độ sắc nét)
- ✅ Adaptive thresholding (ngưỡng hóa thông minh)
- ✅ Noise reduction (khử nhiễu)
- ✅ Morphological smoothing (làm mịn viền chữ)

## 🚀 Hướng dẫn sử dụng

### Cài đặt từ Installer (Đơn giản nhất)

1. Download file `VietnameseOCRTool_Setup.exe`
2. Double-click để cài đặt
3. Làm theo hướng dẫn trên màn hình
4. Chọn "Chạy cùng Windows" nếu muốn

### Sử dụng

1. Sau khi cài đặt, ứng dụng sẽ hiển thị icon trên System Tray
2. Lần đầu chạy, bạn sẽ được yêu cầu đặt phím tắt
3. Nhấn phím tắt đã đặt để bắt đầu chọn vùng
4. Kéo chuột để chọn vùng chứa văn bản
5. Nhả chuột - văn bản sẽ tự động được nhận dạng và copy vào clipboard
6. Paste (Ctrl+V) vào bất kỳ đâu bạn muốn!

**Thay đổi phím tắt:**
- Chuột phải vào icon trên System Tray
- Chọn "Thay đổi phím tắt"
- Nhấn tổ hợp phím mới

## 📦 Đóng gói Installer

### Cách nhanh nhất

```bash
# Chạy script tự động
build_all.bat
```

File installer sẽ được tạo tại: `Output/VietnameseOCRTool_Setup.exe`

### Yêu cầu để build

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Inno Setup 6** - [Download](https://jrsoftware.org/isdl.php)
- **Tesseract OCR** - [Download](https://github.com/UB-Mannheim/tesseract/wiki)

### Hướng dẫn chi tiết

Xem file [README_SETUP.md](README_SETUP.md) hoặc [HUONG_DAN_NHANH.txt](HUONG_DAN_NHANH.txt)

## 📁 Cấu trúc dự án

```
OCR/
├── ocr_tool.py              # Code chính
├── app_icon.ico             # Icon ứng dụng
├── icon.png                 # Icon PNG (tạo từ .ico)
├── requirements.txt         # Thư viện Python
├── setup.iss                # Script Inno Setup
├── ocr_tool.spec           # Config PyInstaller
├── build_all.bat           # Script build tự động
├── create_icon.py          # Tool tạo icon PNG
│
├── tesseract-main/         # Source code Tesseract
│   └── tessdata/
│       └── vie.traineddata # Dữ liệu tiếng Việt
│
├── dist/                   # Output PyInstaller
│   └── ocr_tool/
│       └── ocr_tool.exe
│
├── Tesseract-OCR/          # Tesseract runtime
│   ├── tesseract.exe
│   └── tessdata/
│
└── Output/                 # Output Inno Setup
    └── VietnameseOCRTool_Setup.exe  # 🎯 File cài đặt
```

## 🛠️ Phát triển

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Chạy từ source

```bash
python ocr_tool.py
```

### Build EXE

```bash
pyinstaller ocr_tool.spec
```

### Tạo icon.png

```bash
python create_icon.py
```

## 📚 Dependencies

- `keyboard` - Xử lý phím tắt toàn cục
- `Pillow` - Xử lý ảnh
- `pytesseract` - Python wrapper cho Tesseract
- `pyperclip` - Copy text vào clipboard
- `pystray` - Icon trên system tray
- `numpy` - Xử lý mảng cho image processing

## 📄 Giấy phép

- **Tesseract OCR**: Apache License 2.0
- **Python**: Python Software Foundation License
- Các thư viện khác: Xem license của từng thư viện

## 🛡️ Windows Defender chặn file?

**ĐÂY LÀ FALSE POSITIVE!** File hoàn toàn an toàn.

### Tại sao bị chặn?

Windows Defender phát hiện `Trojan:Win32/Wacatac.B!ml` - Đây là cảnh báo sai cực kỳ phổ biến với PyInstaller:
- UPX compression 
- PyInstaller bootloader signature
- Keyboard hooks + Clipboard access
- File chưa có Code Signing Certificate

### Khắc phục NGAY:

**Cách 1: Chạy PowerShell Script (Nhanh nhất)**
```powershell
# Chuột phải "Add_Exclusion_Admin.ps1" → Run with PowerShell
# Hoặc mở PowerShell as Admin:
cd F:\OCR\OCR
.\Add_Exclusion_Admin.ps1
```

**Cách 2: Thêm Exclusion thủ công**
1. Mở **Windows Security**
2. **Virus & threat protection** → **Manage settings**
3. **Exclusions** → **Add or remove exclusions**
4. **Add an exclusion** → **Folder** → Chọn thư mục project
5. Build lại: `.\rebuild_after_exclusion.bat`

**Cách 3: Restore file đã bị xóa**
1. **Windows Security** → **Protection history**
2. Tìm `Trojan:Win32/Wacatac.B!ml`
3. **Actions** → **Allow on device**

### Files hỗ trợ:

- `KHAC_PHUC_NGAY.txt` - Hướng dẫn nhanh
- `FIX_WINDOWS_DEFENDER.md` - Hướng dẫn chi tiết
- `Add_Exclusion_Admin.ps1` - Script tự động thêm exclusion
- `rebuild_after_exclusion.bat` - Build lại sau khi thêm exclusion
- `build_safe.bat` - Build với tùy chọn safe (tắt UPX)
- `CHO_NGUOI_DUNG_CUOI.txt` - Hướng dẫn cho user cuối

Xem chi tiết trong `FIX_WINDOWS_DEFENDER.md`

## 🐛 Báo lỗi

Nếu gặp vấn đề:

1. Kiểm tra log files: `%LOCALAPPDATA%\VietnameseOCRTool\`
2. Chạy `ocr_tool.exe` từ Command Prompt để xem error
3. Kiểm tra Windows Event Viewer

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 TODO

- [ ] Hỗ trợ nhiều ngôn ngữ OCR
- [ ] Giao diện cấu hình settings
- [ ] Lịch sử OCR
- [ ] Export kết quả ra file
- [ ] Dark mode cho UI
- [ ] Hỗ trợ chụp cửa sổ cụ thể
- [ ] Cloud sync cho settings

## 💡 Tips

- **Chọn vùng rõ ràng**: Vùng có độ tương phản cao sẽ cho kết quả tốt hơn
- **Tránh nền phức tạp**: Nền đơn giản giúp OCR chính xác hơn
- **Kích thước phù hợp**: Chọn vùng đủ lớn nhưng không quá lớn
- **Font rõ ràng**: Chữ in rõ nét cho kết quả tốt nhất

## 📞 Liên hệ

- **Email**: your-email@example.com
- **GitHub**: https://github.com/yourusername/vietnamese-ocr-tool

## 🙏 Cảm ơn

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Engine OCR mạnh mẽ
- [PyTesseract](https://github.com/madmaze/pytesseract) - Python wrapper
- [Inno Setup](https://jrsoftware.org/isinfo.php) - Installer creator

---

**Phiên bản:** 1.0.0  
**Ngày cập nhật:** October 2025  
**Tác giả:** Vietnamese OCR Team

⭐ Nếu bạn thấy hữu ích, hãy cho dự án một star!

