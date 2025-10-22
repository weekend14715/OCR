# 🎯 HƯỚNG DẪN HOÀN THIỆN SETUP EMAIL SMTP

## ✅ ĐÃ HOÀN THÀNH

- [x] Code đã fix và push lên GitHub
- [x] Render sẽ auto-deploy (chờ 2-3 phút)
- [x] Upgrade Starter plan ($7/month)

---

## 🚀 CÁC BƯỚC TIẾP THEO

### **BƯỚC 1: TẠO GOOGLE APP PASSWORD** ⚡

1. **Bật 2-Step Verification:**
   - Mở: https://myaccount.google.com/security
   - Tìm mục **"2-Step Verification"**
   - Click **"Get Started"** và làm theo hướng dẫn

2. **Tạo App Password:**
   - Mở: https://myaccount.google.com/apppasswords
   - Nếu không thấy, search "App passwords" trong Google Account
   - Chọn:
     - App: **Mail**
     - Device: **Other (Custom name)**
   - Nhập tên: `OCR License Server`
   - Click **"Generate"**
   - Copy mã **16 ký tự** (ví dụ: `abcdwxyzabcdwxyz`)

⚠️ **LƯU Ý:** Mã này chỉ hiện 1 lần, nhớ copy ngay!

---

### **BƯỚC 2: CẬP NHẬT RENDER ENVIRONMENT VARIABLES** ⚡

1. **Vào Render Dashboard:**
   - Mở: https://dashboard.render.com
   - Chọn service: **ocr-uufr**
   - Click tab **"Environment"**

2. **Thêm biến `EMAIL_ACCOUNTS`:**
   - Click **"Add Environment Variable"**
   - Key: `EMAIL_ACCOUNTS`
   - Value: (copy đoạn JSON bên dưới và **THAY APP_PASSWORD**)

   ```json
   [{"email":"ocrtool.license@gmail.com","app_password":"PASTE_APP_PASSWORD_HERE","daily_limit":500,"display_name":"OCR Tool License"}]
   ```

   **VÍ DỤ:**
   ```json
   [{"email":"ocrtool.license@gmail.com","app_password":"abcdwxyzabcdwxyz","daily_limit":500,"display_name":"OCR Tool License"}]
   ```

3. **Lưu và Deploy:**
   - Click **"Save Changes"**
   - Render sẽ tự động redeploy (2-3 phút)

---

### **BƯỚC 3: KIỂM TRA DEPLOY THÀNH CÔNG** ⚡

1. **Xem Logs:**
   - Vào: https://dashboard.render.com/web/YOUR_SERVICE/logs
   - Chờ deploy xong
   - Tìm dòng:
     ```
     ✅ Email config loaded from environment variable (1 accounts)
     🚀 Vietnamese OCR Tool - License Server
     ```

2. **Nếu thấy lỗi:**
   - Check lại `EMAIL_ACCOUNTS` có đúng format không
   - Phải dùng **double quotes** `"` (KHÔNG phải single quotes `'`)
   - App password phải đúng 16 ký tự

---

### **BƯỚC 4: TEST EMAIL** ⚡

Chạy script PowerShell test:

```powershell
powershell -ExecutionPolicy Bypass -File test_email_production.ps1
```

Script sẽ tự động:
1. ✅ Kiểm tra email config
2. ✅ Gửi email test
3. ✅ (Optional) Test tạo license + gửi email từ admin panel

**Kết quả mong đợi:**
```
[1/3] Checking Email Configuration...
  Status:   OK - Email config will work!
  Accounts: 1
    - Email: ocrtool.license@gmail.com
      Password: OK (16 chars)

[2/3] Sending Test Email...
  SUCCESS - Email sent!
    To:      hoangtuan.th484@gmail.com
    Via:     ocrtool.license@gmail.com

  CHECK YOUR INBOX!
```

---

### **BƯỚC 5: KIỂM TRA EMAIL TRONG INBOX** ⚡

1. Mở Gmail: **hoangtuan.th484@gmail.com**
2. Tìm email với subject: **"🎉 License Key OCR Tool - LIFETIME"**
3. Nếu không thấy → **Check Spam folder**
4. Email sẽ có:
   - ✅ Header gradient đẹp
   - ✅ License key trong box
   - ✅ Thông tin plan
   - ✅ Hướng dẫn kích hoạt

---

## 🔧 NẾU GẶP LỖI

### ❌ "Email config not available"
**Giải pháp:**
- Chưa thêm `EMAIL_ACCOUNTS` vào Render
- Hoặc format JSON sai
- Check lại Render Environment Variables

### ❌ "Username and Password not accepted"
**Giải pháp:**
1. Kiểm tra 2-Step Verification đã bật chưa
2. Tạo App Password mới
3. Paste đúng app_password (16 ký tụ, không có khoảng trắng)

### ❌ "JSON Parse Error"
**Giải pháp:**
- Phải dùng **double quotes** `"`
- Không được có ký tự xuống dòng trong JSON
- Copy chính xác format từ hướng dẫn

### ❌ Email không tới inbox
**Giải pháp:**
1. Check Spam folder
2. Check Render logs có dòng `✅ Email sent to...`
3. Thử gửi lại bằng script test

---

## 📋 CHECKLIST HOÀN CHỈNH

### Chuẩn bị:
- [x] Upgrade Render lên Starter ($7/month)
- [x] Code đã push lên GitHub
- [x] Render đang auto-deploy

### Setup Email:
- [ ] Bật 2-Step Verification trên Gmail
- [ ] Tạo App Password (16 ký tự)
- [ ] Thêm `EMAIL_ACCOUNTS` vào Render Environment
- [ ] Render redeploy thành công

### Testing:
- [ ] Chạy `test_email_production.ps1`
- [ ] Test 1: Email config → OK
- [ ] Test 2: Gửi email test → SUCCESS
- [ ] Kiểm tra inbox → Email nhận được
- [ ] (Optional) Test admin generate license

### Production Ready:
- [ ] Email tự động gửi khi tạo license từ Admin Panel
- [ ] Email tự động gửi khi thanh toán PayOS thành công
- [ ] Hệ thống hoạt động ổn định

---

## 🎯 SAU KHI SETUP XONG

### Sử dụng Admin Panel:

**URL Admin:** https://ocr-uufr.onrender.com/admin

**Tạo license + Tự động gửi email:**
1. Nhập Admin API Key
2. Điền email khách hàng
3. Chọn plan type (lifetime/yearly/monthly)
4. Click "Generate"
5. → Email tự động gửi cho khách hàng! 🎉

### API Endpoints:

**Generate License (Admin):**
```bash
curl -X POST https://ocr-uufr.onrender.com/api/admin/generate \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY" \
  -d '{
    "plan_type": "lifetime",
    "quantity": 1,
    "email": "customer@example.com"
  }'
```

**Test Email:**
```bash
curl -X POST https://ocr-uufr.onrender.com/api/debug/test-email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"test@example.com"}'
```

**Check Config:**
```bash
curl https://ocr-uufr.onrender.com/api/debug/email-config
```

---

## 📊 MONITORING

### Xem Logs:
https://dashboard.render.com/web/YOUR_SERVICE/logs

Tìm:
- `✅ Email sent to ...` → Thành công
- `❌ Failed to send email` → Lỗi
- `[OK] Email config loaded` → Config OK

### Email Usage:
Mỗi account Gmail free có limit **500 emails/ngày**.

Nếu cần nhiều hơn:
- Thêm account thứ 2 vào `EMAIL_ACCOUNTS`
- Hệ thống tự động rotate

---

## 🎉 HOÀN TẤT!

Sau khi làm xong 5 bước trên:
✅ Email tự động gửi khi tạo license
✅ Email tự động gửi khi thanh toán thành công
✅ Hệ thống production-ready!

---

**File tham khảo:**
- `RENDER_EMAIL_SETUP.md` - Chi tiết kỹ thuật
- `test_email_production.ps1` - Script test
- `license_server/email_sender.py` - Email sender code
- `license_server/app.py` - API endpoints

**Cập nhật:** 2024-10-22  
**Status:** ⏳ Waiting for Environment Variables Setup

