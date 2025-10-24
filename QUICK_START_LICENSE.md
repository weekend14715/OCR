# ⚡ QUICK START - Hệ Thống Bản Quyền

## 🎯 Đã Hoàn Thành

✅ Hệ thống bản quyền **đa lớp bảo mật** đã được tích hợp vào `ocr_tool.py`

---

## 📁 Files Được Tạo

### Thư mục `license/`
- `hardware_id.py` - Lấy Hardware Fingerprint
- `license_crypto.py` - Mã hóa AES-256
- `license_activator.py` - Kích hoạt online/offline
- `license_manager.py` - **Quản lý chính**
- `license_dialog.py` - Giao diện nhập key
- `README.md` - Tài liệu kỹ thuật

### Scripts hỗ trợ
- `test_license_system.py` - Test hệ thống
- `test_license_dialog.py` - Test giao diện
- `check_hwid.py` - Xem Hardware ID
- `deactivate_license.py` - Hủy kích hoạt

### Tài liệu
- `HUONG_DAN_LICENSE.md` - Hướng dẫn người dùng
- `LICENSE_SYSTEM_SUMMARY.md` - Tổng quan hệ thống
- `QUICK_START_LICENSE.md` - File này

---

## 🚀 Test Ngay

### 1. Test giao diện nhập key
```bash
python test_license_dialog.py
```

### 2. Xem Hardware ID máy này
```bash
python check_hwid.py
```

### 3. Test hệ thống license
```bash
python test_license_system.py
```

### 4. Chạy app (sẽ yêu cầu license)
```bash
python ocr_tool.py
```

---

## 🔑 Format License Key

```
OCR24-XXXXX-XXXXX-XXXXX
```

Ví dụ: `OCR24-ABCDE-12345-FGHIJ`

---

## ⚙️ Cấu Hình Cần Thay Đổi

### 1. URL Server (QUAN TRỌNG)

**File:** `license/license_activator.py` - Dòng 17

```python
API_BASE_URL = "https://your-website.com/api/license"
```

→ Thay bằng URL server thật của bạn

### 2. Secret Keys (QUAN TRỌNG)

**File:** `license/license_crypto.py` - Dòng 22-23

```python
_SALT = b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'
_SECRET_PHRASE = "OCRToolProfessionalEdition2024SecureKey"
```

→ Thay bằng secrets của bạn (càng random càng tốt)

### 3. Link Mua License

**File:** `license/license_dialog.py` - Dòng 193

```python
url = "https://your-website.com/buy-license"
```

→ Thay bằng URL trang mua của bạn

---

## 🌐 Server API Cần Có

### Endpoint: POST /api/license/activate

**Request:**
```json
{
  "license_key": "OCR24-XXXXX-XXXXX-XXXXX",
  "hwid": "C2FC3049FF482DEE92DAB1BF3B930A06",
  "product": "OCR_TOOL"
}
```

**Response Success:**
```json
{
  "success": true,
  "message": "License activated",
  "data": {
    "user_info": {
      "name": "User Name",
      "email": "user@example.com"
    }
  }
}
```

**Response Error:**
```json
{
  "success": false,
  "message": "Invalid license key"
}
```

**HTTP Codes:**
- 200: OK
- 401: Invalid key
- 403: Already activated on another machine
- 410: Expired

---

## 🔐 Bảo Mật

### 6 Lớp Bảo Vệ:

1. ✅ **Hardware Fingerprint** - Bind với máy
2. ✅ **AES-256 Encryption** - Mã hóa license
3. ✅ **Multi-Location Storage** - Lưu 3 nơi
4. ✅ **Integrity Checks** - CRC32 + SHA-256
5. ✅ **Online Validation** - Check với server
6. ✅ **Code Obfuscation** - PyArmor (optional)

---

## 🛠️ Build & Deploy

### Build với Obfuscation

```bash
# Cài PyArmor
pip install pyarmor

# Obfuscate
pyarmor obfuscate -r license/

# Build EXE
pyinstaller --onefile --noconsole ocr_tool.py
```

---

## 📞 Cần Giúp Đỡ?

### Xem tài liệu chi tiết:
- `HUONG_DAN_LICENSE.md` - Cho người dùng
- `LICENSE_SYSTEM_SUMMARY.md` - Cho developer
- `license/README.md` - Kỹ thuật

### Test từng module:
```bash
python -m license.hardware_id
python -m license.license_crypto
python -m license.license_activator
python -m license.license_manager
```

---

## ✅ Checklist Trước Khi Deploy

- [ ] Thay URL server trong `license_activator.py`
- [ ] Thay secrets trong `license_crypto.py`
- [ ] Thay URL mua license trong `license_dialog.py`
- [ ] Implement server API
- [ ] Test activation online
- [ ] Test activation offline
- [ ] Build EXE
- [ ] Test trên máy sạch

---

## 🎉 Sẵn Sàng Sử Dụng!

Hệ thống đã **hoàn chỉnh** và **production-ready**.

Chỉ cần:
1. Config URL server
2. Implement API backend
3. Deploy!

**Good luck!** 🚀
