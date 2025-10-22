# 📧 Hướng Dẫn Setup Gmail App Password

## ❌ Lỗi Hiện Tại

```
Failed: Email config not available - logged only
```

**Nguyên nhân:** File `email_config.py` chưa có app passwords thật!

---

## ✅ Giải Pháp: Tạo Gmail App Passwords

Bạn cần tạo **App Passwords** cho 2 Gmail accounts:
1. `ocrtool.license@gmail.com` (hoặc Gmail của bạn)
2. `ocrtool.system@gmail.com` (hoặc Gmail thứ 2)

---

## 📋 Bước 1: Tạo/Sử Dụng Gmail Accounts

### **Option A: Tạo mới 2 Gmail accounts**
1. Vào: https://accounts.google.com/signup
2. Tạo 2 Gmail mới:
   - `ocrtool.license@gmail.com`
   - `ocrtool.system@gmail.com`

### **Option B: Dùng Gmail sẵn có**
Bạn có thể dùng Gmail hiện tại của mình:
- Gmail 1: `hoangtuan.th484@gmail.com` ← email bạn đã có
- Gmail 2: Tạo thêm 1 Gmail mới hoặc dùng Gmail phụ

**Khuyến nghị:** Dùng Option B (dùng Gmail sẵn có) nhanh hơn!

---

## 📋 Bước 2: Bật 2-Step Verification

### **Với MỖI Gmail account:**

1. Vào: https://myaccount.google.com/security

2. Tìm mục **"2-Step Verification"**

3. Click **"Get started"** hoặc **"Turn on"**

4. Làm theo hướng dẫn:
   - Nhập số điện thoại
   - Nhận mã OTP
   - Xác nhận

5. **✅ Bật thành công** → Thấy "2-Step Verification is on"

---

## 📋 Bước 3: Tạo App Password

### **Với MỖI Gmail account:**

1. Vào: https://myaccount.google.com/security

2. Scroll xuống, tìm **"App passwords"**

3. Click **"App passwords"**
   - Nếu không thấy → Kiểm tra lại 2-Step Verification đã bật chưa

4. Tạo App Password:
   - **Select app:** Mail
   - **Select device:** Other (Custom name)
   - **Name:** OCR Tool
   - Click **"Generate"**

5. **Copy App Password** (16 ký tự):
   ```
   VD: abcd efgh ijkl mnop
   ```
   
   **Lưu ý:** Bỏ dấu cách! → `abcdefghijklmnop`

6. **Lưu lại** App Password này! (Chỉ hiện 1 lần duy nhất)

---

## 📋 Bước 4: Update `email_config.py`

Mở file `license_server/email_config.py` và update:

### **Trước:**
```python
{
    'email': 'ocrtool.license@gmail.com',
    'password': 'gjxhqhqrflvjzurg',  # ← Fake password (ví dụ)
    'name': 'OCR License System',
    'daily_limit': 500
}
```

### **Sau:**
```python
{
    'email': 'hoangtuan.th484@gmail.com',  # ← Gmail THẬT của bạn
    'password': 'abcdefghijklmnop',  # ← App Password THẬT (16 ký tự, bỏ dấu cách)
    'name': 'OCR License System',
    'daily_limit': 500
}
```

### **Full Example:**
```python
def get_email_accounts():
    return [
        {
            'email': 'hoangtuan.th484@gmail.com',  # Gmail 1 (thật)
            'password': 'abcd efgh ijkl mnop',  # App Password 1 (thật, bỏ dấu cách)
            'name': 'OCR License System',
            'daily_limit': 500
        },
        {
            'email': 'your-second-gmail@gmail.com',  # Gmail 2 (thật)
            'password': 'wxyz 1234 5678 90ab',  # App Password 2 (thật, bỏ dấu cách)
            'name': 'OCR System Backup',
            'daily_limit': 500
        }
    ]
```

---

## 📋 Bước 5: Test Email

### **Option A: Test locally**

```bash
cd license_server
python
```

```python
from email_sender import send_license_email

result = send_license_email(
    to_email='hoangtuan.th484@gmail.com',  # Email của bạn
    license_key='TEST-1234-ABCD-5678',
    customer_name='Hoang Tuan',
    plan_type='lifetime'
)

print(result)
```

Nếu thành công:
```python
{
    'success': True,
    'message': 'Email sent successfully to hoangtuan.th484@gmail.com',
    'account_used': 'hoangtuan.th484@gmail.com'
}
```

### **Option B: Test qua Admin Panel**

1. Vào: http://localhost:5000/admin (local) hoặc https://ocr-uufr.onrender.com/admin (production)

2. Tạo license với email của bạn

3. Check email inbox!

---

## ⚠️ Troubleshooting

### **Lỗi 1: "App passwords" không hiện**

**Nguyên nhân:** 2-Step Verification chưa bật

**Giải pháp:**
1. Vào: https://myaccount.google.com/security
2. Bật 2-Step Verification
3. Đợi vài phút
4. Refresh page
5. "App passwords" sẽ xuất hiện

---

### **Lỗi 2: "Authentication failed" khi gửi email**

**Nguyên nhân:** App Password sai

**Giải pháp:**
1. Xóa App Password cũ trên Google Account
2. Tạo App Password mới
3. Copy đúng (16 ký tự, bỏ dấu cách)
4. Update vào `email_config.py`

---

### **Lỗi 3: "SMTPAuthenticationError: Username and Password not accepted"**

**Nguyên nhân:** 
- App Password sai
- Hoặc chưa bật "Less secure app access"

**Giải pháp:**
1. Check lại App Password (copy đúng, bỏ dấu cách)
2. Tạo lại App Password mới
3. Đảm bảo dùng App Password, không phải password Gmail

---

### **Lỗi 4: Email vào Spam**

**Nguyên nhân:** Gmail từ Gmail khác thường không vào spam, nhưng có thể

**Giải pháp:**
1. Check Spam folder
2. Mark email as "Not Spam"
3. Add sender vào Contacts

---

## 📊 Gmail Limits

| Limit Type | Free Gmail | G Suite |
|------------|------------|---------|
| Emails/day | **500** | **2,000** |
| Recipients/email | 500 | 2,000 |
| Emails/minute | ~20 | ~60 |

**Với 2 Gmail accounts:** 1000 emails/day (đủ dùng!)

---

## 🎯 Quick Setup (Nhanh Nhất)

### **Dùng 1 Gmail duy nhất:**

Nếu bạn chỉ muốn test nhanh, chỉ cần 1 Gmail:

1. **Tạo App Password** cho Gmail của bạn: `hoangtuan.th484@gmail.com`

2. **Update `email_config.py`:**

```python
def get_email_accounts():
    return [
        {
            'email': 'hoangtuan.th484@gmail.com',
            'password': 'YOUR_APP_PASSWORD_HERE',  # 16 ký tự
            'name': 'OCR License System',
            'daily_limit': 500
        }
    ]
```

3. **Done!** (500 emails/day đủ dùng)

---

## ✅ Checklist Setup

- [ ] Có ít nhất 1 Gmail account (hoặc tạo mới)
- [ ] Bật 2-Step Verification cho Gmail
- [ ] Tạo App Password (16 ký tự)
- [ ] Copy App Password (bỏ dấu cách)
- [ ] Update `email_config.py` với email + app password thật
- [ ] Test gửi email
- [ ] Xác nhận email được nhận
- [ ] Push code lên GitHub
- [ ] Test trên production (Render)

---

## 🚀 Sau Khi Setup Xong

### **Commit và Push:**

```bash
git add license_server/email_config.py
git commit -m "feat: Add Gmail app passwords for email sending"
git push origin main
```

**Lưu ý:** File `email_config.py` chứa passwords, nên:
- Có thể thêm vào `.gitignore` (nếu muốn bảo mật)
- Hoặc push lên (vì App Password có thể thu hồi bất kỳ lúc nào)

### **Test trên Render:**

1. Đợi Render deploy xong (~2 phút)
2. Vào admin panel: https://ocr-uufr.onrender.com/admin
3. Tạo license với email của bạn
4. Check inbox!

---

## 🎉 Kết Quả

Sau khi setup xong, khi tạo license:

**Console:**
```
✅ Email sent to customer@example.com via hoangtuan.th484@gmail.com
   License: ABCD-1234-EFGH-5678
```

**Admin UI:**
```
✅ Đã tạo 1 license thành công!
📧 Email đã được gửi đến: customer@example.com
Sent via hoangtuan.th484@gmail.com
```

**Email Received:**
```
Subject: 🎉 License Key OCR Tool - LIFETIME
From: OCR License System <hoangtuan.th484@gmail.com>

[Beautiful HTML email with license key]
```

---

## 📞 Cần Giúp Đỡ?

Nếu gặp vấn đề:
1. Check file `email_config.py` có đúng format không
2. Check App Password copy đúng không (16 ký tự, bỏ dấu cách)
3. Check 2-Step Verification đã bật chưa
4. Test với Python script nhỏ trước
5. Check Render logs nếu deploy lên production

---

**Good luck!** 🚀

