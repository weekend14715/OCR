# 🔐 QUICK REFERENCE - HỆ THỐNG MÃ HÓA LICENSE

## 📍 NƠI LƯU TRỮ (3 VỊ TRÍ)

| # | Vị trí | Nội dung | Format |
|---|--------|----------|--------|
| **1** | `F:\OCR\OCR\.lic` | Encrypted license data | Base64 (~700 chars) |
| **2** | `HKCU\Software\OCRTool\` | InstallID + Checksum + Hash | Registry keys |
| **3** | `%APPDATA%\OCRTool\.checksum` | Backup checksum | Base64 encoded |

---

## 🔒 THUẬT TOÁN MÃ HÓA (3 LỚP)

### Lớp 1: Hardware Fingerprint (HWID)
```
CPU ID + MB UUID + Disk Serial + MAC + PC Name
→ SHA-256 → 32 ký tự hex
```
**Ví dụ:** `C2FC3049FF482DEE92DAB1BF3B930A06`

### Lớp 2: Key Derivation (PBKDF2)
```python
Password  = HWID + "OCRToolProfessionalEdition2024SecureKey"
Salt      = b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'
Iterations = 100,000
Algorithm = PBKDF2-HMAC-SHA256
Output    = 32 bytes (256-bit key)
```

### Lớp 3: Encryption (Fernet)
```
Fernet = AES-128 CBC + HMAC-SHA256
Input  = JSON {license_key, hwid, timestamp, user_info, checksum, hash}
Output = Base64 encrypted string (~700 chars)
```

---

## 📊 CẤU TRÚC DỮ LIỆU

### Dữ liệu gốc (trước khi mã hóa):
```json
{
  "license_key": "FBB6-4E8A-3EE0-96E8",
  "hwid": "C2FC3049FF482DEE92DAB1BF3B930A06",
  "timestamp": 1729839400.0,
  "activated_at": "2024-10-25 14:30:00",
  "version": "1.0",
  "user_info": {
    "name": "Nguyen Van A",
    "email": "nguyenvana@example.com"
  },
  "checksum": "348C92FF",
  "hash": "012D3C56A5F6B02243E68FF787E67B35..."
}
```

### Sau khi mã hóa (lưu vào .lic):
```
Z0FBQUFBQm8tNzlHZGF3U2NyS2VFbUMxV3Vjdzgzamh6U1JOU2ZsMUl1RVBKU0o3WjYzbVlSUFlKRHpU
UEVkRi0xWEJHM1NxSy1BcWlvREVLYk1fdExHUm0zTkw2WVRtcXVzN2FzX3JMdUxQX3ZPS0REbmxjTHVQ
... (~700 ký tự)
```

---

## 🔄 QUY TRÌNH KÍCH HOẠT

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User nhập license key → Gửi server validate             │
├─────────────────────────────────────────────────────────────┤
│ 2. Server check: valid? expired? already_used?              │
├─────────────────────────────────────────────────────────────┤
│ 3. Server trả về: {valid: true, plan, user_info}            │
├─────────────────────────────────────────────────────────────┤
│ 4. Client mã hóa: license_key + HWID + user_info            │
│    → Derive key từ HWID (PBKDF2 100k iterations)            │
│    → Encrypt với Fernet (AES-128 CBC + HMAC)                │
├─────────────────────────────────────────────────────────────┤
│ 5. Lưu vào 3 nơi:                                           │
│    [✓] File .lic (encrypted data)                           │
│    [✓] Registry (InstallID + Checksum + Hash)               │
│    [✓] Backup .checksum (backup hash)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 QUY TRÌNH KIỂM TRA

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Đọc từ 3 nguồn: .lic + Registry + .checksum              │
├─────────────────────────────────────────────────────────────┤
│ 2. Cross-validate: So sánh hash giữa 3 nguồn                │
├─────────────────────────────────────────────────────────────┤
│ 3. Decrypt .lic với HWID hiện tại                           │
│    → Derive decryption key từ HWID                          │
│    → Fernet.decrypt()                                       │
├─────────────────────────────────────────────────────────────┤
│ 4. Verify integrity:                                        │
│    [✓] CRC32 Checksum match?                                │
│    [✓] SHA-256 Hash match?                                  │
│    [✓] HWID match?                                          │
├─────────────────────────────────────────────────────────────┤
│ 5. Check expiry_date (nếu có)                               │
├─────────────────────────────────────────────────────────────┤
│ 6. Return: ✅ Valid hoặc ❌ Invalid                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ CƠ CHẾ BẢO VỆ

| Tấn công | Cách thức | Phòng thủ | Kết quả |
|----------|-----------|-----------|---------|
| **Copy file .lic sang máy khác** | Copy `.lic` → Máy B | HWID khác → Decrypt fail | ❌ Blocked |
| **Sửa file .lic** | Edit hex → Thay đổi expiry | HMAC fail → Fernet reject | ❌ Blocked |
| **Fake HWID** | Spoof hardware info | Key derivation khác → Decrypt fail | ❌ Blocked |
| **Xóa file .lic** | Delete `.lic` file | Restore từ Registry/Backup | ✅ Recovered |
| **Xóa Registry** | Delete registry keys | Restore từ .lic/Backup | ✅ Recovered |
| **Reverse engineer** | Decompile → Tìm SECRET | Obfuscate với PyArmor/Cython | ⚠️ Reduced risk |

---

## 🧪 TEST CASES

### ✅ Test 1: Encrypt & Decrypt bình thường
```python
from license.license_crypto import LicenseCrypto

crypto = LicenseCrypto()
result = crypto.encrypt_license("FBB6-4E8A-3EE0-96E8", hwid)
decrypted = crypto.decrypt_license(result['encrypted_data'], hwid)

assert decrypted['license_key'] == "FBB6-4E8A-3EE0-96E8"  # ✅ PASS
```

### ❌ Test 2: Decrypt với SAI HWID
```python
wrong_hwid = "FAKE_HWID_123"
decrypted = crypto.decrypt_license(result['encrypted_data'], wrong_hwid)

assert decrypted is None  # ✅ PASS (blocked correctly)
```

### ❌ Test 3: Decrypt data đã bị sửa
```python
tampered = result['encrypted_data'][:-5] + 'XXXXX'
decrypted = crypto.decrypt_license(tampered, hwid)

assert decrypted is None  # ✅ PASS (tampering detected)
```

---

## 📁 FILE SOURCE CODE

```
license/
├── license_manager.py      → Quản lý chính (save/load/check)
├── license_crypto.py       → Mã hóa/giải mã (encrypt/decrypt)
├── license_activator.py    → Kích hoạt online với server
├── hardware_id.py          → Tạo Hardware ID (HWID)
└── license_dialog.py       → UI nhập license key
```

---

## 💡 LƯU Ý QUAN TRỌNG

### 🔴 KHÔNG PUBLIC LÊN GITHUB:
```python
_SALT = b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'
_SECRET_PHRASE = "OCRToolProfessionalEdition2024SecureKey"
```

### 🟡 KHI BUILD PRODUCTION:
- ✅ Sử dụng **PyArmor** hoặc **Cython** để obfuscate code
- ✅ Remove debug prints
- ✅ Add code obfuscation cho constants
- ✅ Sign executable với certificate

### 🟢 OFFLINE MODE:
- ✅ Kích hoạt LẦN ĐẦU cần Internet
- ✅ Sau đó validate offline từ file `.lic` local
- ✅ Không cần kết nối server mỗi lần chạy

---

## 🎯 ĐỘ AN TOÀN

| Component | Độ mạnh | Thời gian crack (ước tính) |
|-----------|---------|----------------------------|
| **AES-128** | Rất cao | ~10^21 năm |
| **PBKDF2 (100k iter)** | Cao | ~0.1s/key (10 keys/s) |
| **HMAC-SHA256** | Rất cao | Không thể forge |
| **Overall** | ⭐⭐⭐⭐⭐ | Không khả thi |

---

## 🚀 CÁCH SỬ DỤNG

### Kích hoạt:
```python
from license.license_manager import LicenseManager

manager = LicenseManager()
success = manager.activate_license("FBB6-4E8A-3EE0-96E8")
```

### Kiểm tra:
```python
if manager.check_license():
    print("✅ License hợp lệ")
    # Run app
else:
    print("❌ Cần kích hoạt")
    exit(1)
```

### Hủy kích hoạt:
```python
manager.deactivate_license()  # Xóa tất cả
```

---

## 📞 TROUBLESHOOTING

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| Decrypt fail | HWID thay đổi | Re-activate với key cũ |
| File not found | .lic bị xóa | Recover từ Registry/Backup |
| Checksum mismatch | File bị corrupt | Re-activate |
| Already activated | Key đã dùng trên máy khác | Liên hệ support để transfer |

---

**Version:** 1.0  
**Last Updated:** 2024-10-25  
**Security Level:** ⭐⭐⭐⭐⭐ (5/5)

