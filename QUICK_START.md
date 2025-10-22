# ⚡ QUICK START - 5 PHÚT SETUP EMAIL

## 📋 TÓM TẮT NHANH

Anh đã upgrade Starter plan → Giờ chỉ cần 3 bước:

---

## 1️⃣ TẠO APP PASSWORD (2 phút)

1. Bật 2FA: https://myaccount.google.com/security
2. Tạo App Password: https://myaccount.google.com/apppasswords
   - App: **Mail**
   - Device: **Other** → Nhập `OCR License Server`
   - Copy mã **16 ký tự**: `abcdwxyzabcdwxyz`

---

## 2️⃣ CẬP NHẬT RENDER (2 phút)

1. Vào: https://dashboard.render.com
2. Chọn service **ocr-uufr** → Tab **Environment**
3. Add variable:
   - Key: `EMAIL_ACCOUNTS`
   - Value:
   ```json
   [{"email":"ocrtool.license@gmail.com","app_password":"PASTE_MÃ_16_KÝ_TỰ_Ở_ĐÂY","daily_limit":500,"display_name":"OCR Tool License"}]
   ```
4. Click **Save Changes** → Chờ deploy (2 phút)

---

## 3️⃣ TEST (1 phút)

Chạy script:
```powershell
powershell -ExecutionPolicy Bypass -File test_email_production.ps1
```

Hoặc test bằng curl:
```bash
curl -X POST https://ocr-uufr.onrender.com/api/debug/test-email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"hoangtuan.th484@gmail.com"}'
```

→ Check inbox → Nhận email! 🎉

---

## ✅ XONG!

Giờ mỗi lần tạo license từ Admin Panel, email tự động gửi cho khách hàng!

**Chi tiết đầy đủ:** Xem file `SETUP_COMPLETE_GUIDE.md`

