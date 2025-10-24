# 🔐 Hệ Thống Quản Lý Bản Quyền OCR Tool

## 📋 Tổng Quan

Hệ thống bản quyền đa lớp bảo mật với các tính năng:

- ✅ **Hardware Fingerprint** - Bind license với phần cứng máy tính
- ✅ **AES-256 Encryption** - Mã hóa license file
- ✅ **Multi-Location Storage** - Lưu ở 3 nơi (File + Registry + Backup)
- ✅ **Online Activation** - Kích hoạt qua server
- ✅ **Offline Fallback** - Có thể kích hoạt offline
- ✅ **Cross Validation** - Kiểm tra tính toàn vẹn

---

## 📁 Cấu Trúc File

```
license/
├── __init__.py              # Package init
├── hardware_id.py           # Lấy Hardware Fingerprint
├── license_crypto.py        # Mã hóa/giải mã
├── license_activator.py     # Kích hoạt với server
├── license_manager.py       # Quản lý license (MAIN)
├── license_dialog.py        # Giao diện nhập key
└── README.md               # File này
```

---

## 🚀 Cách Sử Dụng

### 1. Tích hợp vào app

```python
from license import LicenseManager

def main():
    # Kiểm tra license
    license_manager = LicenseManager()
    
    if not license_manager.check_license():
        print("❌ License không hợp lệ")
        sys.exit(1)
    
    # ✅ License OK → Chạy app
    run_app()
```

### 2. Kích hoạt license thủ công

```python
from license import LicenseManager

manager = LicenseManager()
success = manager.activate_license("OCR24-XXXXX-XXXXX-XXXXX")

if success:
    print("✅ Kích hoạt thành công!")
```

### 3. Hủy kích hoạt

```python
from license import LicenseManager

manager = LicenseManager()
manager.deactivate_license()
```

---

## 🔑 Format License Key

```
OCR24-XXXXX-XXXXX-XXXXX
```

- **OCR24**: Prefix sản phẩm
- **XXXXX**: 3 phần random/hash (5 ký tự mỗi phần)
- Tổng: 29 ký tự (bao gồm dấu -)

---

## 🌐 Cấu Hình Server API

### File: `license_activator.py`

```python
# Thay đổi URL này thành server thật của bạn
API_BASE_URL = "https://your-website.com/api/license"
```

### Endpoints cần có:

#### 1. **POST /api/license/activate**

**Request:**
```json
{
  "license_key": "OCR24-XXXXX-XXXXX-XXXXX",
  "hwid": "A1B2C3D4E5F6...",
  "timestamp": 1234567890.0,
  "product": "OCR_TOOL",
  "version": "1.0"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "License activated successfully",
  "data": {
    "license_key": "OCR24-XXXXX-XXXXX-XXXXX",
    "user_info": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "expiry_date": null
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "License key không hợp lệ"
}
```

**Status Codes:**
- `200`: Success
- `401`: Invalid key
- `403`: Key đã bind với máy khác
- `410`: Key hết hạn

#### 2. **POST /api/license/verify** (Optional)

Kiểm tra license mà không kích hoạt

#### 3. **POST /api/license/deactivate** (Optional)

Hủy kích hoạt (giải phóng máy)

---

## 💾 Nơi Lưu Trữ License

### 1. File chính: `.lic`
```
F:\OCR\OCR\.lic (hidden)
```

### 2. Windows Registry:
```
HKEY_CURRENT_USER\Software\OCRTool\
├── InstallID  (16 ký tự đầu của HWID)
├── Checksum   (CRC32)
└── Hash       (SHA-256, 32 ký tự)
```

### 3. Backup file: `.checksum`
```
%APPDATA%\OCRTool\.checksum (hidden)
```

---

## 🔐 Bảo Mật

### Lớp 1: Hardware Fingerprint
- Kết hợp: CPU ID + Motherboard UUID + Disk Serial + MAC + Computer Name
- Hash SHA-256 → 32 ký tự hex

### Lớp 2: Encryption
- Thuật toán: **Fernet (AES-128 CBC + HMAC)**
- Key derivation: **PBKDF2** với 100,000 iterations
- Key = `PBKDF2(HWID + SECRET_PHRASE)`

### Lớp 3: Integrity Check
- **CRC32 Checksum** để phát hiện sửa đổi
- **SHA-256 Hash** để verify toàn bộ data
- Cross-validation giữa 3 nơi lưu trữ

### Lớp 4: Obfuscation (Khi build)
```bash
pyarmor obfuscate license_crypto.py
pyarmor obfuscate hardware_id.py
pyinstaller --onefile --noconsole ocr_tool.py
```

---

## 🧪 Testing

### Test từng module:

```bash
# Test Hardware ID
python -m license.hardware_id

# Test Crypto
python -m license.license_crypto

# Test Activator
python -m license.license_activator

# Test Manager
python -m license.license_manager

# Test Dialog
python -m license.license_dialog
```

---

## 🛠️ Troubleshooting

### Lỗi: "Cannot import LicenseManager"
- Đảm bảo thư mục `license/` có file `__init__.py`
- Chạy từ thư mục cha của `license/`

### Lỗi: "ModuleNotFoundError: No module named 'cryptography'"
```bash
pip install cryptography requests
```

### Lỗi: "Cannot connect to server"
- Hệ thống tự động fallback sang kích hoạt **offline**
- Kiểm tra URL API trong `license_activator.py`

### Lỗi: "HWID không khớp"
- License đã bind với máy khác
- Cần deactivate trên máy cũ hoặc mua license mới

### Lỗi: "License bị giả mạo"
- File `.lic` bị sửa đổi
- Xóa tất cả và kích hoạt lại

---

## 📝 Lưu Ý Quan Trọng

1. **Secret Keys**: Khi deploy, thay đổi các giá trị secret trong:
   - `license_crypto.py`: `_SALT`, `_SECRET_PHRASE`
   - `license_activator.py`: `API_BASE_URL`, check digit algorithm

2. **Obfuscation**: Bắt buộc obfuscate code trước khi phát hành:
   ```bash
   pyarmor obfuscate license/
   ```

3. **Server-side**: Implement API server với các endpoint cần thiết

4. **Backup**: User nên backup license key phòng trường hợp cần cài lại

---

## 📞 Support

Nếu có vấn đề về license, liên hệ:
- Email: support@your-website.com
- Website: https://your-website.com/support

---

## 📄 License

Copyright © 2024. All rights reserved.

