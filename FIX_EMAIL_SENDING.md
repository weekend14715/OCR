# 📧 Fix: Email Tự Động Gửi Khi Tạo License

## ❌ Vấn Đề

Khi admin tạo license thủ công qua trang admin, license key được tạo thành công nhưng **email KHÔNG được gửi** cho khách hàng.

## ✅ Giải Pháp

### 1. Cập Nhật API `/api/admin/generate`

File: `license_server/app.py`

**Thay đổi:**
- Thêm code gửi email tự động sau khi tạo license
- Hiển thị thông tin email trong response
- Log chi tiết khi gửi email thành công/thất bại

```python
# Sau khi tạo license keys
if EMAIL_ENABLED and email:
    for license_key in created_keys:
        result = send_license_email(
            to_email=email,
            license_key=license_key,
            customer_name=email.split('@')[0],
            order_id='ADMIN-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            plan_type=plan_type
        )
```

### 2. Cập Nhật Email Sender

File: `license_server/email_sender.py`

**Thay đổi:**
- Từ chỉ LOG ra console → GỬI EMAIL THẬT qua Gmail
- Sử dụng 2 Gmail accounts với load balancing
- Tracking daily limit (500 emails/account/day)
- Email template đẹp với HTML/CSS

**Features:**
- ✅ Round-robin account selection
- ✅ Daily limit tracking (1000 emails/day total)
- ✅ Beautiful HTML email template
- ✅ Automatic fallback nếu account 1 đạt limit

### 3. Cập Nhật Admin UI

File: `license_server/templates/admin.html`

**Thay đổi:**
- Hiển thị thông báo "📧 Email đã được gửi đến: xxx" khi thành công
- Hiển thị "⚠️ Email không được gửi" nếu thất bại
- Hiển thị account Gmail được sử dụng

## 📋 Response API Mới

### Trước (không có email info):
```json
{
  "success": true,
  "licenses": ["ABCD-1234-EFGH-5678"],
  "plan": "lifetime",
  "quantity": 1
}
```

### Sau (có email info):
```json
{
  "success": true,
  "licenses": ["ABCD-1234-EFGH-5678"],
  "plan": "lifetime",
  "quantity": 1,
  "email": "customer@example.com",
  "email_sent": true,
  "email_result": "Sent via ocrtool.license@gmail.com"
}
```

## 🎨 Email Template Mới

Email được gửi có:
- 🎉 Header gradient đẹp
- 📦 License key trong box dashed
- 📋 Thông tin gói (plan, expiry)
- 📝 Hướng dẫn kích hoạt từng bước
- 📧 Link support email
- 💅 Responsive design

## 🔑 Gmail Accounts Được Sử Dụng

Hệ thống sử dụng **2 Gmail accounts** để gửi email:

### Account 1 (Primary):
- Email: `ocrtool.license@gmail.com`
- Limit: 500 emails/day
- App Password: `gjxhqhqrflvjzurg`

### Account 2 (Backup):
- Email: `ocrtool.system@gmail.com`
- Limit: 500 emails/day
- App Password: `xjoqoaedkwzjfvxj`

**Tổng:** 1000 emails/day

## 🔧 Setup Gmail App Passwords

### Đã Setup Sẵn ✅

Cả 2 Gmail accounts đã được cấu hình với App Passwords trong file `license_server/email_config.py`.

### Nếu Cần Tạo Mới:

1. Vào Google Account: https://myaccount.google.com/
2. Security → 2-Step Verification (bật nếu chưa bật)
3. App passwords → Create new
4. Copy app password (16 ký tự)
5. Update vào `email_config.py`

## 📊 Email Usage Tracking

File tracking: `email_usage.json`

```json
{
  "ocrtool.license@gmail.com": {
    "date": "2024-10-22",
    "count": 15
  },
  "ocrtool.system@gmail.com": {
    "date": "2024-10-22",
    "count": 3
  }
}
```

## 🧪 Test Email

### Test Locally:

```bash
cd license_server
python email_sender.py
```

### Test qua Admin Panel:

1. Vào: http://localhost:5000/admin
2. Nhập Admin API Key
3. Điền email của bạn
4. Chọn plan: Lifetime
5. Click "Tạo License"
6. Check email inbox!

### Test qua API:

```bash
curl -X POST http://localhost:5000/api/admin/generate \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY" \
  -d '{
    "plan_type": "lifetime",
    "quantity": 1,
    "email": "your-email@example.com"
  }'
```

## ⚠️ Troubleshooting

### Email không được gửi?

**1. Check email_config.py tồn tại:**
```bash
ls license_server/email_config.py
```

**2. Check import:**
```python
python -c "from license_server.email_config import *; print('OK')"
```

**3. Check Gmail App Password:**
- Đảm bảo App Password đúng (16 ký tự, không có dấu cách)
- Đảm bảo 2-Step Verification đã bật

**4. Check SMTP connection:**
```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('ocrtool.license@gmail.com', 'gjxhqhqrflvjzurg')
print("✅ SMTP OK!")
server.quit()
```

**5. Check logs:**
```
✅ Email sent to xxx via ocrtool.license@gmail.com  ← Thành công
❌ Failed to send email: [error]                      ← Lỗi
```

### Email vào Spam?

Gmail thường không đánh dấu email từ Gmail khác là spam. Nhưng nếu có:
- Check email trong Spam folder
- Mark as "Not Spam"
- Add sender vào contacts

### Daily Limit Reached?

Nếu cả 2 accounts đạt 500 emails/day:
- Đợi đến ngày mới (reset tự động)
- Hoặc thêm Gmail accounts mới vào `email_config.py`

## 📝 Files Đã Thay Đổi

1. `license_server/app.py` - Thêm email sending logic
2. `license_server/email_sender.py` - Viết lại hoàn toàn
3. `license_server/templates/admin.html` - Hiển thị email status

## 🚀 Deployment

### Local Testing:

```bash
cd license_server
python app.py
```

### Deploy to Render:

```bash
git add .
git commit -m "feat: Add automatic email sending when creating license"
git push origin main
```

Render sẽ tự động deploy!

## ✨ Kết Quả

### Khi tạo license thành công:

**Console logs:**
```
✅ Email sent to customer@example.com via ocrtool.license@gmail.com
   License: ABCD-1234-EFGH-5678
```

**Admin UI:**
```
✅ Đã tạo 1 license thành công!

License Keys:
ABCD-1234-EFGH-5678

📧 Email đã được gửi đến: customer@example.com
Sent via ocrtool.license@gmail.com
```

**Email nhận được:**
- Subject: 🎉 License Key OCR Tool - LIFETIME
- From: OCR License System <ocrtool.license@gmail.com>
- Body: Beautiful HTML email với license key

## 🎁 Bonus Features

### Load Balancing:
- Account 1 gửi email đầu tiên
- Khi Account 1 đạt 500 emails, tự động chuyển sang Account 2
- Reset counter mỗi ngày

### Email Template:
- Gradient header
- License key trong dashed box
- Hướng dẫn kích hoạt
- Support email link
- Professional footer

### Error Handling:
- Nếu không có email config → chỉ log, không crash
- Nếu SMTP fail → return error message rõ ràng
- Nếu daily limit reached → thông báo rõ

## 📚 Documentation

Xem thêm:
- `EMAIL_SYSTEM_GUIDE.md` - Hướng dẫn chi tiết email system
- `email_config.py` - Cấu hình Gmail accounts
- `email_sender.py` - Source code email sender

## ✅ Checklist

- [x] Cập nhật `app.py` để gửi email khi tạo license
- [x] Viết lại `email_sender.py` để gửi email thật
- [x] Cập nhật `admin.html` để hiển thị email status
- [x] Test locally
- [ ] Test trên Render (sau khi push)
- [ ] Xác nhận email được nhận

## 🎉 Done!

Bây giờ khi bạn tạo license qua admin panel, email sẽ được gửi tự động cho khách hàng! 🚀

