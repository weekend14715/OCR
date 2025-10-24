# 🛡️ Hệ Thống Bảo Vệ Nâng Cao - Vietnamese OCR Tool

## 📋 Tổng Quan

Hệ thống bảo vệ nâng cao được thiết kế để ngăn chặn việc sao chép và sử dụng trái phép ứng dụng Vietnamese OCR Tool. Hệ thống bao gồm nhiều lớp bảo vệ để đảm bảo chỉ người dùng có license hợp lệ mới có thể sử dụng ứng dụng.

## 🔒 Các Tính Năng Bảo Vệ

### 1. **Code Obfuscation & Encryption**
- **Mã hóa source code** bằng thuật toán AES-256
- **Obfuscation** tên biến, function, và strings
- **Compression** và encoding để che giấu logic
- **Dynamic loading** để tránh static analysis

### 2. **Hardware Binding**
- **Hardware fingerprinting** dựa trên:
  - CPU information (processor, frequency, cores)
  - Memory configuration
  - Disk information
  - Network interfaces (MAC addresses)
  - Boot time
- **Unique machine ID** được tạo từ hardware fingerprint
- **License binding** với machine ID cụ thể

### 3. **Online Verification**
- **Real-time verification** với license server
- **Session-based authentication** với timeout
- **Periodic re-verification** mỗi 5 phút
- **Anti-replay attacks** với timestamp validation
- **HMAC signature** để đảm bảo tính toàn vẹn

### 4. **Anti-Debugging & Anti-Reverse Engineering**
- **Debugger detection** (OllyDbg, x64dbg, IDA, etc.)
- **Process monitoring** cho debug tools
- **Memory protection** chống memory patching
- **Code integrity checking** để phát hiện modification
- **Anti-VM detection** để tránh chạy trong máy ảo

### 5. **Anti-Copy Protection**
- **File integrity checking** để phát hiện copy
- **Timestamp validation** để tránh copy nhanh
- **Directory structure validation**
- **License file binding** với executable

## 🚀 Cách Sử Dụng

### Bước 1: Cài Đặt Dependencies
```bash
pip install cryptography psutil requests pyinstaller
```

### Bước 2: Build Ứng Dụng Được Bảo Vệ
```bash
python build_protected_app.py
```

### Bước 3: Chạy License Server
```bash
cd license_server
python app.py
```

### Bước 4: Phân Phối Ứng Dụng
- File `VietnameseOCRTool_Protected.zip` chứa ứng dụng đã được bảo vệ
- Người dùng giải nén và chạy `VietnameseOCRTool_Protected.exe`
- Nhập license key khi được yêu cầu

## 🔧 Cấu Hình Hệ Thống

### Protection System Configuration
```python
# Trong protection_system.py
class AdvancedProtection:
    def __init__(self):
        self.server_url = "http://127.0.0.1:5000"  # License server URL
        self.verification_interval = 300  # 5 phút
        self.session_timeout = 3600  # 1 giờ
```

### License Server Configuration
```python
# Trong license_server/app.py
PROTECTION_KEY = b'vietnamese_ocr_protection_key_2024'
SESSION_TIMEOUT = 3600  # 1 giờ
VERIFICATION_INTERVAL = 300  # 5 phút
```

## 📊 API Endpoints

### 1. Protection Verification
```
POST /api/protection/verify
{
    "hardware_id": "unique-hardware-id",
    "timestamp": 1234567890,
    "signature": "hmac-signature",
    "app_name": "VietnameseOCRTool"
}
```

### 2. Session Check
```
POST /api/protection/check
{
    "session_token": "session-token",
    "hardware_id": "hardware-id"
}
```

### 3. License Validation (Enhanced)
```
POST /api/validate
{
    "license_key": "XXXX-XXXX-XXXX-XXXX",
    "machine_id": "hardware-id",
    "protection_token": "session-token"
}
```

## 🛠️ Troubleshooting

### Lỗi Thường Gặp

#### 1. "Debugger detected"
- **Nguyên nhân**: Phát hiện debugger hoặc reverse engineering tools
- **Giải pháp**: Đóng tất cả debug tools và chạy lại

#### 2. "Application integrity compromised"
- **Nguyên nhân**: File executable bị thay đổi hoặc copy
- **Giải pháp**: Tải lại ứng dụng từ nguồn chính thức

#### 3. "Online verification failed"
- **Nguyên nhân**: Không kết nối được license server
- **Giải pháp**: Kiểm tra kết nối internet và license server

#### 4. "Hardware ID mismatch"
- **Nguyên nhân**: License được kích hoạt trên máy khác
- **Giải pháp**: Sử dụng license key mới hoặc liên hệ support

### Debug Mode
Để debug hệ thống bảo vệ, set environment variable:
```bash
set PROTECTION_DEBUG=1
python ocr_tool_licensed.py
```

## 🔐 Bảo Mật

### Mã Hóa
- **AES-256** cho mã hóa dữ liệu
- **PBKDF2** với 100,000 iterations cho key derivation
- **HMAC-SHA256** cho signature validation

### Key Management
- **Hardware-based key generation** từ hardware fingerprint
- **Server-side key validation** với HMAC
- **Session-based tokens** với timeout

### Network Security
- **HTTPS** cho tất cả API calls (khuyến nghị)
- **Request signing** với HMAC
- **Timestamp validation** chống replay attacks

## 📈 Monitoring & Analytics

### License Server Logs
- **Validation attempts** với IP address
- **Hardware ID tracking** cho mỗi license
- **Session management** và timeout
- **Protection violations** và error logs

### Client-side Logs
- **Protection system status**
- **Verification attempts** và results
- **Error messages** và debugging info

## 🚨 Cảnh Báo Bảo Mật

### Không Nên Làm
- ❌ **Không share** license key với người khác
- ❌ **Không copy** thư mục ứng dụng sang máy khác
- ❌ **Không modify** executable file
- ❌ **Không chạy** trong debugger hoặc VM

### Nên Làm
- ✅ **Bảo mật** license key
- ✅ **Chạy** từ thư mục gốc
- ✅ **Cập nhật** ứng dụng thường xuyên
- ✅ **Báo cáo** các vấn đề bảo mật

## 📞 Hỗ Trợ

### Liên Hệ
- **Email**: support@vietnamese-ocr.com
- **Website**: https://vietnamese-ocr.com
- **Documentation**: [Link to docs]

### Báo Cáo Lỗi
Khi báo cáo lỗi, vui lòng cung cấp:
1. **Error message** đầy đủ
2. **Hardware ID** (nếu có)
3. **License key** (masked)
4. **System information** (OS, Python version)
5. **Steps to reproduce**

## 🔄 Cập Nhật Hệ Thống

### Version Control
- **Protection system version** được track trong database
- **Client version** được validate với server
- **Automatic updates** cho protection system

### Migration
Khi cập nhật hệ thống bảo vệ:
1. **Backup** database hiện tại
2. **Update** server code
3. **Test** với existing licenses
4. **Deploy** production version

---

**Lưu ý**: Hệ thống bảo vệ này được thiết kế để bảo vệ bản quyền phần mềm. Việc cố gắng bypass hoặc reverse engineer hệ thống có thể vi phạm pháp luật về bản quyền.
