# 📧 HỆ THỐNG EMAIL - OCR TOOL LICENSE

## 🎯 Tổng Quan

Hệ thống email tự động với **2 tài khoản Gmail** để gửi license key cho khách hàng sau khi thanh toán thành công.

---

## 📦 Cấu Trúc Files

```
license_server/
├── email_config.py       # ⚙️ Cấu hình 2 tài khoản Gmail
├── email_sender.py       # 📧 Module gửi email
├── app.py               # 🚀 License server (đã tích hợp email)
└── email_usage.json     # 📊 Tracking usage (tự động tạo)

test_email_config.py     # 🧪 Script test email
```

---

## 🔧 Cấu Hình

### **File: `license_server/email_config.py`**

```python
EMAIL_ACCOUNTS = [
    {
        'email': 'ocrtool.license@gmail.com',
        'password': 'gjxhqhqrflvjzurg',  # App Password
        'daily_limit': 500
    },
    {
        'email': 'ocrtool.system@gmail.com',
        'password': 'xjoqoaedkwzjfvxj',  # App Password
        'daily_limit': 500
    }
]
```

**Thông tin:**
- ✅ 2 tài khoản Gmail đã cấu hình
- ✅ App Password đã tạo
- ✅ Tổng: **1000 emails/ngày**
- ✅ Tự động chuyển đổi khi hết quota

---

## 🚀 Sử Dụng

### **1. Test Email**

```bash
# Test gửi email
python test_email_config.py
```

**Chức năng:**
- Gửi 1 email test
- Gửi nhiều emails (kiểm tra auto-switch)
- Xem trạng thái usage

### **2. Sử Dụng Trong Code**

```python
from license_server.email_sender import send_license_email

# Gửi license key
result = send_license_email(
    to_email="customer@example.com",
    license_key="ABCD-1234-EFGH-5678",
    customer_name="Nguyễn Văn A",
    order_id="ORDER-001",
    plan_type="lifetime"
)

if result['success']:
    print(f"✅ Email sent via {result['account_used']}")
    print(f"Remaining: {result['emails_remaining']}")
else:
    print(f"❌ Failed: {result['message']}")
```

### **3. Tích Hợp Vào License Server**

**Đã tự động tích hợp!** Khi khách hàng thanh toán thành công:

```
Thanh toán thành công
    ↓
Tạo license key
    ↓
Gửi email tự động ✅
    ↓
Khách hàng nhận license
```

---

## 📊 Theo Dõi Usage

### **Xem Trạng Thái**

```bash
# Chạy test script
python test_email_config.py

# Chọn: 3. Xem trạng thái
```

**Hoặc trong code:**

```python
from license_server.email_sender import LicenseEmailSender

sender = LicenseEmailSender()
status = sender.get_status()

print(f"Total sent today: {status['total_sent']}")
print(f"Total remaining: {status['total_remaining']}")

for acc in status['accounts']:
    print(f"{acc['email']}: {acc['sent_today']}/{acc['limit']}")
```

### **File Tracking**

File `license_server/email_usage.json` được tự động tạo:

```json
{
    "date": "2025-01-15",
    "accounts": {
        "ocrtool.license@gmail.com": {
            "sent_today": 45,
            "last_reset": "2025-01-15"
        },
        "ocrtool.system@gmail.com": {
            "sent_today": 12,
            "last_reset": "2025-01-15"
        }
    }
}
```

---

## 🔄 Chuyển Đổi Tự Động

Hệ thống **tự động chuyển** giữa 2 tài khoản:

```
Email #1 → Account 1
Email #2 → Account 1
...
Email #500 → Account 1 ✅ (đạt limit)
Email #501 → Account 2 🔄 (tự động chuyển)
Email #502 → Account 2
...
Email #1000 → Account 2 ✅ (đạt limit)
Email #1001 → ❌ Hết quota (chờ sang ngày mới)
```

---

## 📧 Email Template

Email được gửi đi có:

- ✅ Design đẹp (HTML responsive)
- ✅ License key nổi bật
- ✅ Hướng dẫn kích hoạt từng bước
- ✅ Thông tin support
- ✅ Thông tin đơn hàng

**Preview:**

```
┌─────────────────────────────────────┐
│  🎉 Cảm ơn bạn đã mua OCR Tool!     │
├─────────────────────────────────────┤
│                                     │
│  License Key:                       │
│  ┌─────────────────────────────┐   │
│  │   ABCD-1234-EFGH-5678       │   │
│  └─────────────────────────────┘   │
│                                     │
│  Hướng dẫn kích hoạt:              │
│  1. Mở OCR Tool                    │
│  2. Click "Kích hoạt bản quyền"    │
│  3. Paste license key              │
│  4. Click "Kích hoạt"              │
│                                     │
│  Support: hoangtuan.th484@gmail.com │
└─────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### **❌ Lỗi: Email không gửi được**

**Nguyên nhân:**
1. App Password sai
2. Chưa bật 2-Step Verification
3. Gmail blocked

**Giải pháp:**

```bash
# 1. Test lại cấu hình
python test_email_config.py

# 2. Kiểm tra email_config.py
# 3. Tạo lại App Password nếu cần
```

### **❌ Lỗi: Import email_sender failed**

```python
# Trong app.py sẽ hiện warning:
⚠️ Warning: Email sender not available
```

**Giải pháp:**
```bash
# Kiểm tra file tồn tại
ls license_server/email_config.py
ls license_server/email_sender.py

# Chạy thử
python -c "from license_server.email_sender import send_license_email; print('OK')"
```

### **❌ Lỗi: Hết quota**

```
❌ Hết quota! Đã gửi >1000 emails hôm nay.
```

**Giải pháp:**
- Chờ sang ngày mới (tự động reset)
- Hoặc thêm tài khoản thứ 3 trong `email_config.py`

---

## 📈 Nâng Cấp (Tương Lai)

### **Thêm Tài Khoản Thứ 3**

Edit `license_server/email_config.py`:

```python
EMAIL_ACCOUNTS = [
    # ... 2 tài khoản hiện tại ...
    {
        'email': 'ocrtool.backup@gmail.com',
        'password': 'app-password-here',
        'name': 'OCR License System',
        'daily_limit': 500
    }
]
```

→ Tổng: **1500 emails/ngày**

### **Tracking Nâng Cao**

Thêm vào database:

```sql
CREATE TABLE email_logs (
    id INTEGER PRIMARY KEY,
    to_email TEXT,
    license_key TEXT,
    sent_at TEXT,
    account_used TEXT,
    success INTEGER
);
```

### **Retry Logic**

Thêm retry khi gửi thất bại:

```python
def send_with_retry(to_email, license_key, max_retries=3):
    for i in range(max_retries):
        result = send_license_email(...)
        if result['success']:
            return result
        time.sleep(5)
    return result
```

---

## 📝 Checklist Triển Khai

- [x] Tạo 2 tài khoản Gmail
- [x] Bật 2-Step Verification
- [x] Tạo App Password
- [x] Cấu hình `email_config.py`
- [x] Test gửi email
- [x] Tích hợp vào license server
- [ ] **Deploy lên production**
- [ ] Monitor email usage
- [ ] Backup App Passwords

---

## 🆘 Support

**Nếu gặp vấn đề:**

1. Chạy test: `python test_email_config.py`
2. Check logs trong terminal
3. Kiểm tra `email_usage.json`
4. Verify App Password trên Gmail

**Contact:**
- Email: hoangtuan.th484@gmail.com
- GitHub: [Your Repo]

---

## 📚 Tài Liệu Tham Khảo

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [App Passwords](https://support.google.com/accounts/answer/185833)
- [2-Step Verification](https://support.google.com/accounts/answer/185839)

---

**✅ Hệ thống email đã sẵn sàng!**

Tổng: **1000 emails/ngày** | Auto-switch | Tracking | Beautiful HTML emails

