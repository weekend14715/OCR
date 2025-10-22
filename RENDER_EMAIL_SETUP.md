# 📧 HƯỚNG DẪN CẤU HÌNH EMAIL SMTP TRÊN RENDER

## ✅ ĐÃ UPGRADE STARTER PLAN → SMTP SẴN SÀNG!

Sau khi upgrade lên Starter plan ($7/month), Render đã mở port SMTP. Giờ chỉ cần cấu hình Environment Variables.

---

## 🔧 BƯỚC 1: CẬP NHẬT ENVIRONMENT VARIABLES

### Truy cập Render Dashboard:
1. Vào: https://dashboard.render.com
2. Chọn service: **ocr-uufr**
3. Click tab **Environment**

### Thêm/Cập nhật biến `EMAIL_ACCOUNTS`:

```json
[{"email":"ocrtool.license@gmail.com","app_password":"YOUR_APP_PASSWORD_HERE","daily_limit":500,"display_name":"OCR Tool License"}]
```

**⚠️ QUAN TRỌNG:**
- Thay `YOUR_APP_PASSWORD_HERE` bằng **App Password** từ Google (16 ký tự)
- **KHÔNG DÙNG** mật khẩu Gmail thường!
- Phải dùng **double quotes** `"` (không phải single quotes `'`)

---

## 🔐 BƯỚC 2: TẠO GOOGLE APP PASSWORD

### Cách lấy App Password từ Gmail:

1. **Bật 2-Step Verification:**
   - Vào: https://myaccount.google.com/security
   - Tìm "2-Step Verification" → Bật nó

2. **Tạo App Password:**
   - Vào: https://myaccount.google.com/apppasswords
   - Chọn app: "Mail"
   - Chọn device: "Other (Custom name)" → Nhập "OCR License Server"
   - Click "Generate"
   - Copy mã **16 ký tự** (không có dấu cách)

3. **Paste vào Environment Variable:**
   ```json
   [{"email":"ocrtool.license@gmail.com","app_password":"abcdwxyzabcdwxyz","daily_limit":500,"display_name":"OCR Tool License"}]
   ```

---

## 🚀 BƯỚC 3: DEPLOY VÀ TEST

### 3.1. Deploy trên Render:

1. Sau khi thêm `EMAIL_ACCOUNTS`, Render sẽ tự động redeploy
2. Chờ deploy thành công (2-3 phút)
3. Check logs: https://dashboard.render.com/web/YOUR_SERVICE/logs

### 3.2. Test Email ngay trên production:

**Test 1: Kiểm tra config**
```bash
curl https://ocr-uufr.onrender.com/api/debug/email-config
```

Kết quả mong đợi:
```json
{
  "status": "OK - Email config will work!",
  "accounts_count": 1,
  "accounts": [
    {
      "email": "ocrtool.license@gmail.com",
      "has_password": true,
      "password_length": 16,
      "daily_limit": 500
    }
  ]
}
```

**Test 2: Gửi email thật**
```bash
curl -X POST https://ocr-uufr.onrender.com/api/debug/test-email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"hoangtuan.th484@gmail.com"}'
```

Kết quả mong đợi:
```json
{
  "success": true,
  "message": "Email sent successfully to hoangtuan.th484@gmail.com",
  "account_used": "ocrtool.license@gmail.com"
}
```

**Test 3: Tạo license + Gửi email từ Admin Panel**
```bash
curl -X POST https://ocr-uufr.onrender.com/api/admin/generate \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY" \
  -d '{
    "plan_type": "lifetime",
    "quantity": 1,
    "email": "hoangtuan.th484@gmail.com"
  }'
```

---

## 📝 CẤU TRÚC EMAIL_ACCOUNTS CHI TIẾT

### Single Account (Đơn giản):
```json
[{"email":"ocrtool.license@gmail.com","app_password":"abcdwxyzabcdwxyz","daily_limit":500,"display_name":"OCR Tool License"}]
```

### Multiple Accounts (Load Balancing):
```json
[
  {"email":"ocrtool.license@gmail.com","app_password":"password1","daily_limit":500,"display_name":"OCR Tool License"},
  {"email":"ocrtool.license2@gmail.com","app_password":"password2","daily_limit":500,"display_name":"OCR Tool Support"}
]
```

**Lợi ích Multi-Account:**
- ✅ Gmail free có limit 500 email/ngày/account
- ✅ Hệ thống tự động rotate giữa các account
- ✅ Nếu 1 account đạt limit, dùng account khác

---

## 🔍 TROUBLESHOOTING

### ❌ Lỗi: "Network is unreachable"
**Nguyên nhân:** Chưa upgrade Starter plan  
**Giải pháp:** Đã upgrade rồi → OK!

### ❌ Lỗi: "Username and Password not accepted"
**Nguyên nhân:** Sai App Password hoặc chưa bật 2FA  
**Giải pháp:**
1. Kiểm tra App Password đã đúng chưa
2. Đảm bảo 2-Step Verification đã bật
3. Tạo App Password mới

### ❌ Lỗi: "JSON Parse Error"
**Nguyên nhân:** Sai format JSON (dùng single quotes)  
**Giải pháp:** Phải dùng **double quotes** `"`

### ✅ Email không gửi nhưng không báo lỗi
**Kiểm tra:**
1. Check Render logs: https://dashboard.render.com/web/YOUR_SERVICE/logs
2. Tìm dòng: `✅ Email sent to ...` hoặc `❌ Failed to send email`
3. Nếu thấy "Email config not available" → Chưa set `EMAIL_ACCOUNTS`

---

## 📊 MONITORING EMAIL USAGE

Hệ thống tự động track số email đã gửi mỗi ngày:

- File: `email_usage.json` (trên Render disk)
- Reset tự động mỗi ngày
- Daily limit: 500 emails/account

**Xem usage stats:**
```bash
curl https://ocr-uufr.onrender.com/api/admin/stats \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY"
```

---

## 🎯 CHECKLIST SETUP HOÀN CHỈNH

- [ ] Upgrade Render lên Starter plan ($7/month) ✅
- [ ] Bật 2-Step Verification trên Gmail
- [ ] Tạo App Password từ Google
- [ ] Thêm `EMAIL_ACCOUNTS` vào Render Environment Variables
- [ ] Deploy thành công
- [ ] Test `/api/debug/email-config` → Status OK
- [ ] Test `/api/debug/test-email` → Email gửi thành công
- [ ] Kiểm tra email trong inbox
- [ ] Test tạo license từ Admin Panel

---

## 📧 TEMPLATE EMAIL

Khách hàng sẽ nhận được email đẹp với:
- ✅ Subject: "🎉 License Key OCR Tool - LIFETIME"
- ✅ HTML format với gradient header
- ✅ License key trong box nổi bật
- ✅ Thông tin gói: Plan type, thời hạn, mã đơn
- ✅ Hướng dẫn kích hoạt
- ✅ Reply-To: support email

---

## 🚨 BẢO MẬT

**QUAN TRỌNG:**
- ⚠️ **KHÔNG COMMIT** App Password vào Git
- ⚠️ **KHÔNG CHIA SẺ** Environment Variables
- ✅ Dùng Render Environment Variables (encrypted)
- ✅ Rotate App Password định kỳ (3-6 tháng)

---

## 💡 TIPS

1. **Test ngay sau khi setup:**
   - Gửi email test cho chính email anh
   - Kiểm tra Spam folder nếu không thấy

2. **Production Ready:**
   - Hệ thống đã sẵn sàng gửi email tự động
   - Khi khách hàng thanh toán → Tự động gửi license
   - Admin tạo license → Tự động gửi email

3. **Scale Up:**
   - Nếu cần > 500 emails/ngày → Thêm account thứ 2
   - Hệ thống tự động load balance

---

## 📞 SUPPORT

Nếu gặp vấn đề:
1. Check Render logs
2. Test debug endpoints
3. Verify App Password

**Email test endpoint (public):**
- Config check: `GET /api/debug/email-config`
- Send test: `POST /api/debug/test-email`

---

**Cập nhật:** 2024-10-22  
**Status:** ✅ Ready for Production (sau khi set EMAIL_ACCOUNTS)

