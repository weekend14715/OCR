# 🧹 HƯỚNG DẪN XÓA LICENSE ĐỂ TEST

## 📋 MỤC ĐÍCH

Khi test các license key khác nhau, bạn cần xóa sạch license cũ để activate lại với key mới.

Tool này sẽ xóa **TOÀN BỘ** dữ liệu license từ 3 vị trí:
1. ✅ File `.lic` (encrypted license data)
2. ✅ Registry `HKCU\Software\OCRTool\` (hash + checksum)
3. ✅ Backup `%APPDATA%\OCRTool\.checksum` (backup checksum)

---

## 🚀 CÁCH 1: SỬ DỤNG BATCH FILE (Đơn giản)

### Bước 1: Chạy file batch
```batch
clean_license.bat
```

### Bước 2: Xác nhận
```
Bạn có chắc muốn XÓA toàn bộ license? (Y/N): Y
```

### Bước 3: Xem kết quả
```
[✓] File .lic đã bị xóa
[✓] Registry key đã bị xóa
[✓] Backup checksum đã bị xóa

✅ HOÀN TẤT! Đã xóa sạch toàn bộ license data
```

---

## 🔧 CÁCH 2: SỬ DỤNG PYTHON SCRIPT (Nâng cao)

### Bước 1: Chạy script
```bash
python clean_license_advanced.py
```

### Bước 2: Xác nhận
```
⚠️  Bạn có chắc muốn XÓA toàn bộ license? (Y/N): Y
```

### Bước 3: Xem báo cáo chi tiết
```
[1/3] Xóa file .lic...
   ✅ Đã xóa: F:\OCR\OCR\.lic

[2/3] Xóa Registry (HKCU\Software\OCRTool)...
   ✅ Đã xóa registry key:
      - InstallID
      - Checksum
      - Hash

[3/3] Xóa backup checksum (%APPDATA%\OCRTool)...
   ✅ Đá xóa: C:\Users\...\AppData\Roaming\OCRTool\.checksum

[✅] File .lic
[✅] Registry keys
[✅] Backup checksum

✅ HOÀN TẤT! Đã xóa sạch toàn bộ license data
```

---

## 📝 QUY TRÌNH TEST NHIỀU LICENSE KEY

### Scenario: Test 3 license keys khác nhau

#### Test Key 1:
```bash
# 1. Clean license cũ
clean_license.bat

# 2. Activate với key 1
python test_license_real_key.py
# Nhập key: FBB6-4E8A-3EE0-96E8

# 3. Test app
python ocr_tool.py
```

#### Test Key 2:
```bash
# 1. Clean license key 1
clean_license.bat

# 2. Activate với key 2
python test_license_real_key.py
# Nhập key: 1234-5678-ABCD-EFGH

# 3. Test app
python ocr_tool.py
```

#### Test Key 3:
```bash
# 1. Clean license key 2
clean_license.bat

# 2. Activate với key 3
python test_license_real_key.py
# Nhập key: AAAA-BBBB-CCCC-DDDD

# 3. Test app
python ocr_tool.py
```

---

## 🔍 XEM TRẠNG THÁI LICENSE HIỆN TẠI

### Check nhanh:
```bash
# Check file .lic
dir /a:h .lic

# Check Registry
reg query "HKCU\Software\OCRTool"

# Check Backup
dir "%APPDATA%\OCRTool\.checksum"
```

### Hoặc dùng script:
```python
from license.license_manager import LicenseManager

manager = LicenseManager()
if manager.check_license():
    print("✅ License hợp lệ")
else:
    print("❌ Chưa kích hoạt")
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. Đóng App Trước Khi Clean
```
❌ LỖI: File .lic đang được sử dụng

Nguyên nhân: App OCR Tool đang chạy
Giải pháp: Đóng app → Chạy lại clean script
```

### 2. Không Cần Quyền Admin
```
ℹ️  Script clean license KHÔNG CẦN quyền admin
   Vì chỉ xóa:
   - File trong thư mục hiện tại
   - Registry HKCU (user's registry)
   - File trong %APPDATA% (user's folder)
```

### 3. Backup Trước Khi Clean (Optional)
```bash
# Backup license hiện tại
copy .lic license_backup.lic
reg export "HKCU\Software\OCRTool" ocr_registry_backup.reg
```

### 4. Restore License Sau Khi Test (Optional)
```bash
# Restore từ backup
copy license_backup.lic .lic
reg import ocr_registry_backup.reg
```

---

## 🐛 TROUBLESHOOTING

### Vấn đề 1: File .lic không xóa được
```
Lỗi: Access denied hoặc file in use

Giải pháp:
1. Đóng tất cả ứng dụng OCR Tool
2. Kiểm tra Task Manager → Kill process nếu cần
3. Chạy lại script
```

### Vấn đề 2: Registry không xóa được
```
Lỗi: Cannot delete registry key

Giải pháp:
1. Mở Registry Editor (regedit)
2. Navigate: HKEY_CURRENT_USER\Software\OCRTool
3. Right-click → Delete
4. Hoặc chạy: reg delete "HKCU\Software\OCRTool" /f
```

### Vấn đề 3: Backup checksum không xóa được
```
Lỗi: Cannot delete file in %APPDATA%

Giải pháp:
1. Mở File Explorer
2. Gõ: %APPDATA%\OCRTool
3. Xóa thủ công folder OCRTool
```

---

## 🎯 KẾT QUẢ SAU KHI CLEAN

### Khi chạy app sau khi clean:
```python
python ocr_tool.py
```

**Sẽ thấy:**
```
❌ License không hợp lệ hoặc chưa kích hoạt

[Dialog hiện lên]
┌─────────────────────────────────────┐
│  🔐 KÍCH HOẠT BẢN QUYỀN             │
│                                     │
│  Vui lòng nhập License Key          │
│  Định dạng: XXXX-XXXX-XXXX-XXXX     │
│                                     │
│  License Key: [________________]    │
│                                     │
│  [✓ KÍCH HOẠT]  [✗ HỦY]            │
└─────────────────────────────────────┘
```

→ **Nhập license key mới để test!** ✅

---

## 📊 SO SÁNH 2 CÁCH

| Tiêu chí | Batch File | Python Script |
|----------|------------|---------------|
| **Độ đơn giản** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Chi tiết** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Verify** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cross-platform** | ❌ Windows only | ✅ Cross-platform |

**Khuyến nghị:** 
- **Test nhanh:** Dùng `clean_license.bat`
- **Debug chi tiết:** Dùng `clean_license_advanced.py`

---

## 🔐 BẢO MẬT

### Script này có an toàn không?
✅ **AN TOÀN 100%**

**Lý do:**
1. Chỉ xóa file license (không ảnh hưởng app)
2. Chỉ xóa registry của OCRTool (không động đến registry khác)
3. Không cần quyền admin
4. Open-source → Bạn xem được toàn bộ code

### Có thể undo không?
⚠️ **KHÔNG CÓ UNDO**

Sau khi xóa → License mất vĩnh viễn → Cần activate lại với key.

**Nếu muốn giữ license cũ:**
```bash
# Backup trước
copy .lic license_backup.lic

# Restore sau
copy license_backup.lic .lic
```

---

## 💡 MẸO HAY

### Tạo alias cho clean nhanh:
```batch
:: Tạo file clean.bat
@echo off
call clean_license.bat
```

Sau đó chỉ cần gõ:
```bash
clean
```

### Tạo test workflow:
```batch
@echo off
title Test License Workflow

echo [1] Clean old license...
call clean_license.bat

echo.
echo [2] Activate new license...
python test_license_real_key.py

echo.
echo [3] Test app...
python ocr_tool.py

pause
```

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. 📖 Đọc troubleshooting ở trên
2. 🔍 Check xem file/registry có tồn tại không
3. 💬 Liên hệ support

---

**Version:** 1.0  
**Last Updated:** 2024-10-25  
**Compatibility:** Windows 10/11

