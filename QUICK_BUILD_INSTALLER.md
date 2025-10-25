# ⚡ Build Installer Nhanh - 3 Bước

## 🎯 Chuẩn Bị (Chỉ làm 1 lần)

### 1. Cài Inno Setup
- Tải: https://jrsoftware.org/isdl.php
- Cài đặt bình thường

### 2. Tạo Certificate (Miễn phí, cho testing)
```powershell
# Right-click PowerShell as Administrator
.\create_self_signed_cert.ps1
```
Nhập mật khẩu (VD: `123456`), nhớ mật khẩu này!

---

## 🚀 Build Ngay (3 Bước)

### Bước 1: Chạy Script
```bash
# Right-click "build_installer.bat" và chọn "Run as Administrator"
build_installer.bat
```

### Bước 2: Nhập Mật Khẩu
Khi được hỏi:
```
Nhập mật khẩu certificate: [nhập mật khẩu đã tạo]
```

### Bước 3: Lấy File
File sẽ có trong thư mục `Output`:
```
Output/VietnameseOCRTool_Setup_v1.0.0.exe
```

---

## ✅ Xong!

**File cài đặt đã sẵn sàng với:**
- ✅ Chữ ký số
- ✅ Giao diện đẹp
- ✅ Đầy đủ tính năng

**Dung lượng:** ~60-100 MB

**Thời gian:** 3-5 phút

---

## 🐛 Lỗi?

### "Inno Setup not found"
→ Cài Inno Setup từ link trên

### "Certificate not found"
→ Chạy `.\create_self_signed_cert.ps1`

### "Access denied"
→ Right-click và "Run as Administrator"

---

## 📚 Hướng Dẫn Chi Tiết

Xem file: `INSTALLER_BUILD_GUIDE.md`

---

*Easy peasy! 🎉*

