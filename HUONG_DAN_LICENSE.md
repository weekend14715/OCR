# 📘 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG BẢN QUYỀN

## 🎯 Tổng Quan

OCR Tool giờ đây đã được tích hợp hệ thống bản quyền đa lớp bảo mật. Ứng dụng sẽ yêu cầu kích hoạt license trước khi sử dụng.

---

## 🚀 Lần Chạy Đầu Tiên

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
python ocr_tool.py
```

### 3. Nhập License Key

- Khi chạy lần đầu, cửa sổ nhập license sẽ tự động hiện ra
- Nhập license key theo định dạng: **OCR24-XXXXX-XXXXX-XXXXX**
- Nhấn **KÍCH HOẠT**

### 4. Kích hoạt thành công

- License sẽ được lưu tự động
- Lần sau chạy sẽ không cần nhập lại
- License được bind với máy tính này

---

## 🔑 Lấy License Key

### Cách 1: Mua trực tuyến
- Truy cập: `https://your-website.com/buy-license`
- Mua license và nhận key qua email

### Cách 2: Liên hệ trực tiếp
- Email: support@your-website.com
- Cung cấp thông tin để nhận key

---

## 📍 Nơi Lưu Trữ License

License được lưu ở **3 nơi** để đảm bảo bảo mật:

### 1. File ẩn trong thư mục app
```
F:\OCR\OCR\.lic
```

### 2. Windows Registry
```
HKEY_CURRENT_USER\Software\OCRTool\
```

### 3. File backup trong AppData
```
%APPDATA%\OCRTool\.checksum
```

⚠️ **Lưu ý**: Không xóa hoặc sửa đổi các file/registry này!

---

## 🔧 Các Tình Huống Thường Gặp

### ❌ Tình huống 1: License không hợp lệ

**Nguyên nhân:**
- Key nhập sai định dạng
- Key đã hết hạn
- Key đã bị thu hồi

**Giải pháp:**
- Kiểm tra lại key (phân biệt chữ hoa/thường)
- Liên hệ support để gia hạn hoặc lấy key mới

---

### 🖥️ Tình huống 2: "License không khớp với máy này"

**Nguyên nhân:**
- License đã được kích hoạt trên máy khác

**Giải pháp:**
1. Deactivate license trên máy cũ (nếu có thể)
2. Hoặc mua thêm license cho máy mới

---

### 🔌 Tình huống 3: Không có kết nối internet

**Giải pháp:**
- Hệ thống tự động chuyển sang chế độ **kích hoạt offline**
- Key vẫn được validate bằng thuật toán cục bộ
- Kích hoạt được với key hợp lệ

---

### 💻 Tình huống 4: Cài lại Windows / Thay phần cứng

**Nguyên nhân:**
- Hardware ID thay đổi → License không nhận

**Giải pháp:**

#### Cách 1: Tự động (khuyên dùng)
1. Deactivate trên máy cũ trước khi cài lại:
   ```bash
   python deactivate_license.py
   ```
2. Sau khi cài lại, nhập lại key

#### Cách 2: Liên hệ support
- Gửi email với license key cũ
- Yêu cầu reset license
- Nhận key mới hoặc được mở khóa

---

### 🗑️ Tình huống 5: Muốn hủy kích hoạt (chuyển máy)

**Cách làm:**

```bash
python deactivate_license.py
```

Hoặc:

```python
from license import LicenseManager

manager = LicenseManager()
manager.deactivate_license()
```

Sau đó có thể dùng key để kích hoạt máy khác.

---

## 🧪 Kiểm Tra License

### Test thủ công

```bash
python test_license_system.py
```

### Test trong code

```python
from license import LicenseManager

manager = LicenseManager()

# Kiểm tra license
if manager.check_license():
    print("✅ License hợp lệ")
else:
    print("❌ License không hợp lệ")
```

---

## 🛠️ Công Cụ Hỗ Trợ

### 1. Test giao diện nhập key
```bash
python test_license_dialog.py
```

### 2. Kiểm tra Hardware ID
```bash
python -c "from license.hardware_id import get_hardware_id; print(get_hardware_id())"
```

### 3. Test mã hóa/giải mã
```bash
python -m license.license_crypto
```

---

## 📞 Hỗ Trợ

### Khi cần trợ giúp, cung cấp thông tin:

1. **License Key** (nếu có)
2. **Hardware ID** (chạy lệnh trên)
3. **Thông báo lỗi** (chụp màn hình)
4. **Hệ điều hành**: Windows version

### Liên hệ:
- Email: support@your-website.com
- Website: https://your-website.com/support

---

## ⚠️ Lưu Ý Quan Trọng

### ✅ Nên làm:
- Backup license key ở nơi an toàn
- Deactivate trước khi cài lại Windows
- Giữ license key bí mật

### ❌ Không nên:
- Chia sẻ license key cho người khác
- Xóa file `.lic` hoặc Registry
- Crack hoặc can thiệp vào code

---

## 🔐 Bảo Mật

### Hệ thống sử dụng:
- ✅ **AES-256 encryption** - Mã hóa quân sự
- ✅ **Hardware binding** - Bind với máy tính
- ✅ **Multi-location storage** - Lưu 3 nơi
- ✅ **Integrity checks** - Phát hiện giả mạo
- ✅ **Online validation** - Xác thực với server

### Dữ liệu được bảo vệ:
- License key
- Hardware fingerprint
- Thông tin kích hoạt
- Checksum và hash

---

## 📄 FAQ

### Q: Một license dùng được cho mấy máy?
**A:** Mặc định 1 license = 1 máy. Nếu cần dùng nhiều máy, mua thêm license.

### Q: License có hết hạn không?
**A:** Tùy loại:
- **Lifetime**: Không hết hạn
- **Annual**: 1 năm (cần gia hạn)
- **Trial**: 30 ngày

### Q: Nếu mất key thì sao?
**A:** Liên hệ support với email đã mua. Chúng tôi sẽ gửi lại key.

### Q: Có thể dùng offline không?
**A:** Có! Sau khi kích hoạt lần đầu, có thể dùng offline.

### Q: Thay CPU/RAM có ảnh hưởng không?
**A:** Thay 1-2 linh kiện thường không sao. Nếu thay nhiều → liên hệ support.

---

## 🎓 Cho Developer

### Tùy chỉnh URL API server

File: `license/license_activator.py`

```python
API_BASE_URL = "https://your-website.com/api/license"
```

### Tùy chỉnh secret keys

File: `license/license_crypto.py`

```python
_SALT = b'YOUR_CUSTOM_SALT'
_SECRET_PHRASE = "YOUR_SECRET_PHRASE"
```

### Build với obfuscation

```bash
# Cài PyArmor
pip install pyarmor

# Obfuscate license module
pyarmor obfuscate -r license/

# Build EXE
pyinstaller --onefile --noconsole ocr_tool.py
```

---

**Copyright © 2024. All rights reserved.**

