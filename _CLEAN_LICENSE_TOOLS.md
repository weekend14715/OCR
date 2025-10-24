# 🧹 CLEAN LICENSE TOOLS - TÓM TẮT

## ✅ ĐÃ TẠO 3 FILES

### 1. `clean_license.bat` - Batch File (Đơn giản)
```batch
# Cách dùng:
clean_license.bat

# Sẽ xóa:
✓ File .lic
✓ Registry HKCU\Software\OCRTool
✓ Backup %APPDATA%\OCRTool\.checksum
```

**Ưu điểm:**
- ⭐ Đơn giản, chỉ double-click
- ⭐ Không cần Python
- ⭐ Nhanh (< 1 giây)

---

### 2. `clean_license_advanced.py` - Python Script (Nâng cao)
```python
# Cách dùng:
python clean_license_advanced.py

# Output chi tiết:
[1/3] Xóa file .lic...
   ✅ Đã xóa: F:\OCR\OCR\.lic

[2/3] Xóa Registry...
   ✅ Đã xóa registry key:
      - InstallID
      - Checksum
      - Hash

[3/3] Xóa backup checksum...
   ✅ Đã xóa: C:\Users\...\AppData\...
```

**Ưu điểm:**
- ⭐ Chi tiết từng bước
- ⭐ Verify kết quả
- ⭐ Error handling tốt
- ⭐ Cross-platform (Windows/Linux/Mac)

---

### 3. `HOW_TO_CLEAN_LICENSE.md` - Hướng dẫn đầy đủ
```markdown
📖 Bao gồm:
- Cách sử dụng 2 tools
- Workflow test nhiều license keys
- Troubleshooting
- Tips & tricks
```

---

## 🚀 QUICK START

### Test với license key mới:

#### Bước 1: Clean license cũ
```batch
clean_license.bat
→ Nhấn Y để confirm
```

#### Bước 2: Chạy app để nhập key mới
```bash
python ocr_tool.py
→ Dialog hiện lên
→ Nhập license key mới
→ Activate
```

---

## 📊 NHỮNG GÌ SẼ BỊ XÓA

### Vị trí 1: File `.lic`
```
Location: F:\OCR\OCR\.lic
Content: Z0FBQUFBQm8tNzlHZGF3U2NyS2VFbU... (encrypted)
Size: ~700 bytes
Status: ❌ DELETED
```

### Vị trí 2: Registry
```
Location: HKCU\Software\OCRTool\
Keys:
  - InstallID = C2FC3049FF482DEE
  - Checksum  = 348C92FF
  - Hash      = D30C19E96A0B0597...
Status: ❌ DELETED
```

### Vị trí 3: Backup Checksum
```
Location: C:\Users\[User]\AppData\Roaming\OCRTool\.checksum
Content: MTFCMDg2NDkwMUYzNUE5MTFGRjMw... (base64)
Size: ~200 bytes
Status: ❌ DELETED
```

---

## 🔄 WORKFLOW TEST NHIỀU KEYS

```
┌─────────────────────────────────────────────────┐
│ Test Key 1: FBB6-4E8A-3EE0-96E8                 │
├─────────────────────────────────────────────────┤
│ 1. clean_license.bat                            │
│ 2. python ocr_tool.py → Nhập key 1              │
│ 3. Test features...                             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Test Key 2: 1234-5678-ABCD-EFGH                 │
├─────────────────────────────────────────────────┤
│ 1. clean_license.bat                            │
│ 2. python ocr_tool.py → Nhập key 2              │
│ 3. Test features...                             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Test Key 3: AAAA-BBBB-CCCC-DDDD                 │
├─────────────────────────────────────────────────┤
│ 1. clean_license.bat                            │
│ 2. python ocr_tool.py → Nhập key 3              │
│ 3. Test features...                             │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. KHÔNG CÓ UNDO
```
❌ Sau khi clean → License mất vĩnh viễn
✅ Cần activate lại với license key
```

### 2. ĐÓNG APP TRƯỚC KHI CLEAN
```
❌ File đang được sử dụng → Không xóa được
✅ Đóng app → Chạy clean → OK
```

### 3. KHÔNG CẦN QUYỀN ADMIN
```
✅ Chỉ xóa:
   - File trong thư mục hiện tại
   - Registry HKCU (user's registry)
   - File trong %APPDATA% (user's folder)
```

---

## 🎯 KẾT QUẢ SAU KHI CLEAN

### Chạy app:
```bash
python ocr_tool.py
```

### Sẽ thấy:
```
❌ License không hợp lệ hoặc chưa kích hoạt

┌─────────────────────────────────────┐
│  🔐 KÍCH HOẠT BẢN QUYỀN             │
│                                     │
│  License Key: [________________]    │
│                                     │
│  [✓ KÍCH HOẠT]  [✗ HỦY]            │
└─────────────────────────────────────┘
```

→ **Sẵn sàng test với key mới!** ✅

---

## 🔍 VERIFY CLEAN THÀNH CÔNG

### Manual Check:
```batch
:: Check file .lic
dir /a:h .lic
→ File Not Found ✅

:: Check Registry
reg query "HKCU\Software\OCRTool"
→ ERROR: The system was unable to find... ✅

:: Check Backup
dir "%APPDATA%\OCRTool\.checksum"
→ File Not Found ✅
```

### Hoặc dùng Python:
```python
from license.license_manager import LicenseManager

manager = LicenseManager()
if manager.check_license():
    print("❌ Vẫn còn license")
else:
    print("✅ Đã clean sạch")
```

---

## 💡 TIPS HAY

### Tip 1: Tạo shortcut clean nhanh
```batch
:: File: c.bat
@echo off
clean_license.bat
```
→ Gõ `c` để clean nhanh

### Tip 2: Backup trước khi clean
```batch
copy .lic license_backup.lic
reg export "HKCU\Software\OCRTool" backup.reg
```

### Tip 3: Auto-workflow
```batch
@echo off
title Test License Auto

echo Cleaning...
call clean_license.bat

echo Testing...
python test_license_real_key.py

echo Running app...
python ocr_tool.py
```

---

## 🐛 TROUBLESHOOTING

| Vấn đề | Giải pháp |
|--------|-----------|
| File .lic không xóa được | Đóng app → Chạy lại |
| Registry không xóa được | Xóa thủ công bằng regedit |
| Backup không xóa được | Xóa thủ công folder %APPDATA%\OCRTool |

---

## 📚 TÀI LIỆU LIÊN QUAN

1. **Clean Tools:** (You are here)
2. **Test License:** `test_license_real_key.py`
3. **License System:** `LICENSE_SYSTEM_SUMMARY.md`
4. **Encryption:** `QUICK_REFERENCE_ENCRYPTION.md`

---

**Version:** 1.0  
**Date:** 2024-10-25  
**Tools Created:** 3 files (2 scripts + 1 doc)

