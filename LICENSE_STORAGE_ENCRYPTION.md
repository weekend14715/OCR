# 🔐 HỆ THỐNG LƯU TRỮ VÀ MÃ HÓA LICENSE

## 📋 Tổng Quan

Hệ thống license sử dụng **3 lớp bảo mật** và lưu trữ ở **3 vị trí khác nhau** để tránh crack/bypass.

---

## 💾 NƠI LƯU TRỮ LICENSE

### 1️⃣ File `.lic` (File Chính)

**Vị trí:**
```
F:\OCR\OCR\.lic
```

**Đặc điểm:**
- ✅ File ẩn (hidden attribute trên Windows)
- ✅ Chứa dữ liệu đã mã hóa hoàn toàn
- ✅ Format: Base64 của Fernet encrypted data
- ⚠️ Không thể đọc được nếu không có HWID đúng

**Ví dụ nội dung:**
```
Z0FBQUFBQm5kNXRrVGpxcWVRemlrYXdFNXZIc3pMWDNPd...
(~300-500 ký tự base64)
```

---

### 2️⃣ Windows Registry

**Vị trí:**
```
HKEY_CURRENT_USER\Software\OCRTool\
```

**Các giá trị lưu:**
```
├── InstallID   (REG_SZ)  → 16 ký tự đầu của HWID
├── Checksum    (REG_SZ)  → CRC32 checksum (8 ký tự hex)
└── Hash        (REG_SZ)  → SHA-256 hash (32 ký tự hex đầu)
```

**Mục đích:**
- Kiểm tra tính toàn vẹn (integrity check)
- Cross-validate với file `.lic`
- Phát hiện nếu user sửa file `.lic` thủ công

---

### 3️⃣ File Backup `.checksum`

**Vị trí:**
```
C:\Users\<YourName>\AppData\Roaming\OCRTool\.checksum
```

**Đặc điểm:**
- ✅ File ẩn (hidden)
- ✅ Chứa backup checksum được hash từ: `encrypted_data + HWID + SECRET_PHRASE`
- ✅ Base64 encoded thêm 1 lần nữa
- ⚠️ Dùng để recovery nếu file chính bị xóa

**Ví dụ nội dung:**
```
QTJCM0M0RDVFNkY3RzhIOUoxMEs=
```

---

## 🔒 HỆ THỐNG MÃ HÓA

### Lớp 1: Hardware Fingerprint (HWID)

**Nguồn dữ liệu:**
```python
CPU ID + Motherboard UUID + Disk Serial + MAC Address + Computer Name
→ SHA-256 Hash → 64 ký tự hex
```

**Ví dụ HWID:**
```
C2FC3049FF482DEE92DAB1BF3B930A0670D4AE3C1B5F8E9A7D6C4B2A1098FE45
```

**Đặc điểm:**
- ✅ Unique cho mỗi máy tính
- ✅ Không thay đổi trừ khi thay phần cứng
- ✅ Không thể giả mạo (bind với phần cứng thật)

---

### Lớp 2: Key Derivation (PBKDF2)

**Thuật toán:** PBKDF2-HMAC-SHA256

**Parameters:**
```python
Password = HWID + SECRET_PHRASE
Salt     = b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'
Iterations = 100,000
Length   = 32 bytes (256 bits)
```

**Ví dụ code:**
```python
def _derive_key(self, hwid):
    password = (hwid + self._SECRET_PHRASE).encode('utf-8')
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=self._SALT,
        iterations=100000,
    )
    key = kdf.derive(password)
    
    return base64.urlsafe_b64encode(key)  # Fernet key
```

**Kết quả:**
- ✅ Encryption key unique cho mỗi máy
- ✅ Không thể brute-force (100,000 iterations)
- ✅ File `.lic` copy sang máy khác sẽ không decrypt được

---

### Lớp 3: Encryption (Fernet)

**Thuật toán:** Fernet = **AES-128 CBC** + **HMAC-SHA256**

**Cấu trúc Fernet:**
```
Version (1 byte) | Timestamp (8 bytes) | IV (16 bytes) | Ciphertext | HMAC (32 bytes)
```

**Quy trình mã hóa:**

#### Bước 1: Chuẩn bị dữ liệu
```python
data = {
    'license_key': 'FBB6-4E8A-3EE0-96E8',
    'hwid': 'C2FC3049FF482DEE...',
    'timestamp': 1729839400.0,
    'activated_at': '2024-10-25 14:30:00',
    'version': '1.0',
    'user_info': {
        'name': 'John Doe',
        'email': 'john@example.com'
    }
}
```

#### Bước 2: Tính Checksum & Hash
```python
json_data = json.dumps(data, separators=(',', ':'))

# CRC32 Checksum
checksum = zlib.crc32(json_data.encode()) & 0xffffffff
# Ví dụ: 'A3F5B2C1'

# SHA-256 Hash
data_hash = hashlib.sha256((json_data + checksum).encode()).hexdigest()
# Ví dụ: 'D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9...'
```

#### Bước 3: Thêm Checksum & Hash vào data
```python
data['checksum'] = checksum
data['hash'] = data_hash
```

#### Bước 4: Mã hóa với Fernet
```python
json_data_final = json.dumps(data, separators=(',', ':'))

encryption_key = _derive_key(hwid)  # PBKDF2
f = Fernet(encryption_key)

encrypted_bytes = f.encrypt(json_data_final.encode('utf-8'))
encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
```

**Kết quả cuối cùng:**
```
Z0FBQUFBQm5kNXRrVGpxcWVRemlrYXdFNXZIc3pMWDNPd0k3UzRHcjhQdGZoNXBL...
(~300-500 ký tự)
```

---

## 🔓 QUY TRÌNH GIẢI MÃ

### Bước 1: Đọc encrypted data từ file `.lic`

### Bước 2: Derive decryption key từ HWID
```python
decryption_key = _derive_key(current_hwid)
```

### Bước 3: Decrypt với Fernet
```python
encrypted_bytes = base64.b64decode(encrypted_data)
f = Fernet(decryption_key)
decrypted_bytes = f.decrypt(encrypted_bytes)
data = json.loads(decrypted_bytes.decode('utf-8'))
```

⚠️ **Nếu HWID sai → Fernet.decrypt() sẽ raise Exception → Không decrypt được**

### Bước 4: Verify Checksum
```python
saved_checksum = data.pop('checksum')
json_for_check = json.dumps({k:v for k,v in data.items() 
                             if k not in ['checksum', 'hash']})

calculated_checksum = zlib.crc32(json_for_check.encode()) & 0xffffffff

if calculated_checksum != saved_checksum:
    return None  # Dữ liệu bị sửa đổi
```

### Bước 5: Verify Hash
```python
saved_hash = data.pop('hash')
calculated_hash = hashlib.sha256((json_for_check + saved_checksum).encode()).hexdigest()

if calculated_hash != saved_hash:
    return None  # Dữ liệu bị giả mạo
```

### Bước 6: Verify HWID
```python
if data['hwid'] != current_hwid:
    return None  # License không thuộc máy này
```

### Bước 7: Return decrypted data nếu pass tất cả checks

---

## 🛡️ CƠ CHẾ BẢO VỆ

### 1. Anti-Copy Protection

**Vấn đề:** User copy file `.lic` sang máy khác?

**Giải pháp:**
- ❌ File `.lic` được encrypt bằng key derive từ HWID
- ❌ HWID máy B khác HWID máy A
- ❌ Không decrypt được → License invalid

---

### 2. Anti-Tampering Protection

**Vấn đề:** User sửa file `.lic` để thay đổi expiry_date?

**Giải pháp:**
- ❌ File `.lic` là encrypted binary (base64)
- ❌ Sửa 1 byte → Fernet HMAC fail → Decrypt fail
- ❌ Ngay cả decrypt được → CRC32 checksum fail
- ❌ Ngay cả pass checksum → SHA-256 hash fail

---

### 3. Anti-Delete Protection

**Vấn đề:** User xóa file `.lic` để bypass?

**Giải pháp:**
- ✅ Có 2 nơi backup: Registry + `.checksum` file
- ✅ Nếu xóa 1 nơi → Vẫn validate được từ 2 nơi còn lại
- ✅ Xóa cả 3 nơi → Bắt nhập lại license key

---

### 4. Cross-Validation

**Cơ chế:**
```python
def _cross_validate(file_data, registry_data, backup_data):
    # Tính hash của file_data
    file_hash = calculate_hash(file_data)
    
    # So sánh với registry_data['hash']
    if file_hash != registry_data['hash']:
        return False  # Dữ liệu không khớp → Bị sửa
    
    return True
```

---

## 🔍 PHÂN TÍCH BẢO MẬT

### Độ An Toàn Mã Hóa

| Thuật toán | Key Size | Độ an toàn | Khả năng crack |
|------------|----------|------------|----------------|
| **PBKDF2-HMAC-SHA256** | 256-bit | Rất cao | ~2^256 operations |
| **AES-128 CBC** (Fernet) | 128-bit | Rất cao | ~2^128 operations |
| **HMAC-SHA256** | 256-bit | Rất cao | Không thể forge |

### Thời Gian Crack (Ước tính)

**Với supercomputer hiện đại (~10^18 ops/sec):**
- **AES-128**: ~10^21 năm
- **PBKDF2 (100k iterations)**: Mỗi key cần ~0.1 giây
- **Total**: Không khả thi với công nghệ hiện tại

---

## 📊 LƯU ĐỒ QUY TRÌNH

### Quy Trình Kích Hoạt

```
User nhập key → Server validate → Server return success
                                        ↓
                        Encrypt license (HWID + key)
                                        ↓
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
            Save .lic file      Save Registry      Save .checksum
            (Encrypted)         (Hash + Checksum)  (Backup Hash)
```

### Quy Trình Kiểm Tra

```
App Start
    ↓
Read 3 sources: .lic + Registry + .checksum
    ↓
Cross-validate (Check consistency)
    ↓
Decrypt .lic with current HWID
    ↓
Verify: Checksum → Hash → HWID
    ↓
Check expiry_date (if exists)
    ↓
✅ License Valid → Run App
❌ License Invalid → Show Activation Dialog
```

---

## 🧪 TEST MÃ HÓA

### Test 1: Encrypt & Decrypt với đúng HWID

```python
from license.license_crypto import LicenseCrypto

crypto = LicenseCrypto()
test_key = "FBB6-4E8A-3EE0-96E8"
test_hwid = "C2FC3049FF482DEE..."

# Encrypt
result = crypto.encrypt_license(test_key, test_hwid)
print(f"Encrypted: {result['encrypted_data'][:50]}...")
# Output: Z0FBQUFBQm5kNXRrVGpxcWVRemlrYXdFNXZIc3pMWD...

# Decrypt với đúng HWID
decrypted = crypto.decrypt_license(result['encrypted_data'], test_hwid)
print(f"License Key: {decrypted['license_key']}")
# Output: License Key: FBB6-4E8A-3EE0-96E8
```

**✅ Kết quả: SUCCESS**

---

### Test 2: Decrypt với SAI HWID

```python
wrong_hwid = "WRONG_HWID_12345678..."

decrypted = crypto.decrypt_license(result['encrypted_data'], wrong_hwid)
# Output: ❌ Lỗi decrypt license: Fernet decrypt failed
# Return: None
```

**✅ Kết quả: BLOCKED (đúng như mong đợi)**

---

### Test 3: Sửa encrypted data

```python
# Sửa 1 ký tự trong encrypted_data
tampered_data = result['encrypted_data'][:-1] + 'X'

decrypted = crypto.decrypt_license(tampered_data, test_hwid)
# Output: ❌ Lỗi decrypt license: Invalid token
# Return: None
```

**✅ Kết quả: BLOCKED (Fernet HMAC phát hiện tampering)**

---

## 🚀 CÁCH SỬ DỤNG TRONG CODE

### 1. Kích hoạt license

```python
from license.license_manager import LicenseManager

manager = LicenseManager()

# Kích hoạt với key từ user
success = manager.activate_license("FBB6-4E8A-3EE0-96E8")

if success:
    print("✅ Kích hoạt thành công!")
else:
    print("❌ Kích hoạt thất bại!")
```

**Kết quả:**
- ✅ Lưu file `.lic` (encrypted)
- ✅ Lưu Registry (hash + checksum)
- ✅ Lưu `.checksum` backup

---

### 2. Kiểm tra license

```python
from license.license_manager import LicenseManager

manager = LicenseManager()

# Check license (tự động đọc từ 3 nguồn)
is_valid = manager.check_license()

if is_valid:
    print("✅ License hợp lệ - Cho phép chạy app")
else:
    print("❌ License không hợp lệ - Yêu cầu kích hoạt")
    exit(1)
```

---

### 3. Hủy kích hoạt

```python
manager.deactivate_license()
# → Xóa .lic + Registry + .checksum
```

---

## 🔧 FILE QUAN TRỌNG

```
license/
├── license_manager.py     → Lớp quản lý chính (save/load/validate)
├── license_crypto.py      → Lớp mã hóa/giải mã (encrypt/decrypt)
├── license_activator.py   → Kích hoạt online với server
├── hardware_id.py         → Tạo Hardware Fingerprint (HWID)
└── license_dialog.py      → UI nhập license key
```

---

## 📝 LƯU Ý QUAN TRỌNG

### 1. SECRET_PHRASE & SALT

⚠️ **KHÔNG public lên GitHub!**

Khi build production:
```python
# Sử dụng PyArmor hoặc Cython để obfuscate
_SALT = b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'
_SECRET_PHRASE = "OCRToolProfessionalEdition2024SecureKey"
```

### 2. Thay HWID cần re-activate

Nếu user thay:
- CPU → HWID thay đổi → Cần kích hoạt lại
- Mainboard → HWID thay đổi → Cần kích hoạt lại
- Disk → HWID thay đổi → Cần kích hoạt lại

**Giải pháp:** Cho phép chuyển license sang máy mới (deactivate máy cũ)

### 3. Offline Mode

Nếu không có mạng:
- ✅ Vẫn validate được từ file `.lic` local
- ✅ Không cần kết nối server để kiểm tra
- ❌ Nhưng kích hoạt LẦN ĐẦU cần internet

---

## 🎯 KẾT LUẬN

**Hệ thống license này có:**
- ✅ **3 lớp mã hóa** (HWID → PBKDF2 → Fernet)
- ✅ **3 nơi lưu trữ** (.lic + Registry + .checksum)
- ✅ **Cross-validation** giữa 3 nguồn
- ✅ **Anti-copy**: Bind với HWID
- ✅ **Anti-tampering**: CRC32 + SHA256 + HMAC
- ✅ **Anti-crack**: AES-128 + PBKDF2 (100k iterations)

**Độ an toàn:** ⭐⭐⭐⭐⭐ (5/5 sao)

---

## 📞 SUPPORT

Nếu có vấn đề:
1. Kiểm tra file `.lic` có tồn tại không
2. Kiểm tra Registry `HKCU\Software\OCRTool`
3. Kiểm tra backup `%APPDATA%\OCRTool\.checksum`
4. Nếu cả 3 đều bị xóa → Yêu cầu nhập lại license key

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-25  
**Author:** OCR Tool Team

