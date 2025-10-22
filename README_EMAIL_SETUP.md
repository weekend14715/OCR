# 📧 OCR LICENSE SERVER - EMAIL SYSTEM

> Hệ thống gửi email tự động cho License Server - Sẵn sàng production!

---

## 🎯 CHỨC NĂNG

✅ **Tự động gửi email khi:**
- Admin tạo license từ Admin Panel
- Khách hàng thanh toán thành công qua PayOS
- Test email thủ công qua API

✅ **Email Template:**
- HTML đẹp với gradient header
- License key trong box nổi bật
- Hướng dẫn kích hoạt chi tiết

✅ **Load Balancing:**
- Hỗ trợ nhiều email accounts
- Auto rotate khi đạt daily limit (500/ngày)
- Track usage tự động

---

## 🚀 SETUP NHANH (5 PHÚT)

### **Bước 1: Tạo Google App Password**

1. Bật 2FA: https://myaccount.google.com/security
2. Tạo App Password: https://myaccount.google.com/apppasswords
   - Chọn **Mail** > **Other** > Nhập `OCR License Server`
   - Copy mã **16 ký tự**

### **Bước 2: Cập nhật Render Environment**

1. Vào: https://dashboard.render.com
2. Chọn service **ocr-uufr** > Tab **Environment**
3. Add variable `EMAIL_ACCOUNTS`:

```json
[{"email":"ocrtool.license@gmail.com","app_password":"YOUR_16_CHAR_PASSWORD","daily_limit":500,"display_name":"OCR Tool License"}]
```

4. Save → Chờ deploy (2 phút)

### **Bước 3: Test**

```powershell
powershell -ExecutionPolicy Bypass -File test_email_production.ps1
```

**Hoặc:**

```bash
curl -X POST https://ocr-uufr.onrender.com/api/debug/test-email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"your@email.com"}'
```

→ ✅ Check inbox!

---

## 📚 TÀI LIỆU

| File | Mô tả |
|------|-------|
| **QUICK_START.md** | ⚡ Hướng dẫn nhanh 5 phút |
| **SETUP_COMPLETE_GUIDE.md** | 📖 Hướng dẫn chi tiết từng bước |
| **RENDER_EMAIL_SETUP.md** | 🔧 Tài liệu kỹ thuật đầy đủ |
| **EMAIL_SYSTEM_SUMMARY.md** | 📊 Tổng quan hệ thống |

---

## 🔌 API ENDPOINTS

### **Public (No Auth):**

**Check Config:**
```bash
GET https://ocr-uufr.onrender.com/api/debug/email-config
```

**Send Test Email:**
```bash
POST https://ocr-uufr.onrender.com/api/debug/test-email
Body: {"to_email": "test@example.com"}
```

### **Admin (Require X-Admin-Key):**

**Generate License + Send Email:**
```bash
POST https://ocr-uufr.onrender.com/api/admin/generate
Headers: X-Admin-Key: YOUR_API_KEY
Body: {
  "plan_type": "lifetime",
  "quantity": 1,
  "email": "customer@example.com"
}
```

---

## 🛠️ TECH STACK

- **Backend:** Python Flask
- **Email:** SMTP (Gmail)
- **Deployment:** Render (Starter Plan)
- **Database:** SQLite
- **Authentication:** API Key

**SMTP Config:**
- Server: `smtp.gmail.com:587`
- TLS: Enabled
- Timeout: 30s
- Daily Limit: 500 emails/account

---

## 🎨 EMAIL PREVIEW

```
┌─────────────────────────────────────┐
│   🎉 Chúc mừng!                     │
│   Bạn đã nhận được License Key      │
├─────────────────────────────────────┤
│                                     │
│   Xin chào [Customer Name],         │
│                                     │
│   License Key của bạn:              │
│   ┌───────────────────────────────┐ │
│   │   XXXX-XXXX-XXXX-XXXX         │ │
│   └───────────────────────────────┘ │
│                                     │
│   📋 Thông tin gói:                 │
│   • Loại gói: LIFETIME              │
│   • Thời hạn: Trọn đời              │
│                                     │
│   📝 Hướng dẫn kích hoạt:           │
│   1. Mở phần mềm OCR Tool           │
│   2. Vào phần License               │
│   3. Dán License Key                │
│   4. Click Kích hoạt!               │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔐 SECURITY

✅ **Best Practices:**
- App Password thay vì mật khẩu thường
- Environment variables encrypted trên Render
- Không commit credentials vào Git
- Daily rate limiting
- Error handling với timeout

---

## 📊 STATUS

**Code:** ✅ Deployed to GitHub  
**Render:** ✅ Starter Plan Active  
**SMTP:** ⏳ Waiting for Environment Variables  

**Next:** Setup `EMAIL_ACCOUNTS` → Production Ready!

---

## 🧪 TESTING

### **Manual Test:**
```powershell
.\test_email_production.ps1
```

### **Expected Output:**
```
[1/3] Checking Email Configuration...
  ✅ Status: OK - Email config will work!

[2/3] Sending Test Email...
  ✅ SUCCESS - Email sent!

[3/3] Test License Generation + Email
  ✅ LICENSE CREATED!
  ✅ Email: SENT!
```

---

## ⚡ QUICK COMMANDS

**Test Config:**
```bash
curl https://ocr-uufr.onrender.com/api/debug/email-config
```

**Send Test Email:**
```bash
curl -X POST https://ocr-uufr.onrender.com/api/debug/test-email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"hoangtuan.th484@gmail.com"}'
```

**Generate License (Admin):**
```bash
curl -X POST https://ocr-uufr.onrender.com/api/admin/generate \
  -H "X-Admin-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"plan_type":"lifetime","quantity":1,"email":"customer@email.com"}'
```

---

## 🔗 LINKS

- **Admin Panel:** https://ocr-uufr.onrender.com/admin
- **Health Check:** https://ocr-uufr.onrender.com/health
- **Render Dashboard:** https://dashboard.render.com
- **Google App Passwords:** https://myaccount.google.com/apppasswords

---

## 💡 TIPS

1. **Sau khi setup, test ngay** với email của chính mình
2. **Check Spam folder** nếu không thấy email
3. **Monitor Render logs** để track email sending
4. **Backup:** Thêm ít nhất 2 email accounts để tránh downtime

---

## 📞 SUPPORT

**Nếu gặp vấn đề:**
1. Check `SETUP_COMPLETE_GUIDE.md` cho troubleshooting
2. Xem Render logs: https://dashboard.render.com/web/YOUR_SERVICE/logs
3. Test các debug endpoints

---

## 📝 CHANGELOG

**2024-10-22:**
- ✅ Fix SMTP với timeout 30s
- ✅ Add `auto_generate_license()` cho PayOS webhook
- ✅ Improve error handling
- ✅ Add comprehensive documentation
- ✅ Create test script
- 🎉 **Production Ready** (sau khi setup env vars)

---

**Made with ❤️ by Hoàng Tuấn**

