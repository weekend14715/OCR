# ✅ CHECKLIST SETUP RENDER - PAYOS + BANK INFO

## 📝 BẠN CẦN CHUẨN BỊ:

1. ✅ PayOS Credentials (đã có)
2. ⚠️ **Thông tin ngân hàng THẬT của bạn**

---

## 🚀 BƯỚC 1: ĐỢI RENDER DEPLOY XONG

1. Vào **Render Dashboard**: https://dashboard.render.com
2. Chọn service **license-server**
3. Tab **Events** → Xem deploy status
4. ⏳ **Đợi status = "Live"** (2-3 phút)

---

## ⚙️ BƯỚC 2: THÊM 7 ENVIRONMENT VARIABLES

Vào **Environment** tab → Thêm từng biến:

### PayOS Credentials (3 biến)

```bash
PAYOS_CLIENT_ID=4bbbd884-88f2-410c-9dc8-6782980ef64f
PAYOS_API_KEY=dd9f4ba8-cc6b-46e8-9afb-930972bf7531
PAYOS_CHECKSUM_KEY=a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
```

### Bank Account Info (4 biến - THAY ĐỔI THÀNH CỦA BẠN!)

```bash
BANK_CODE=MB
BANK_NAME=MB Bank (Ngân hàng Quân Đội)
BANK_ACCOUNT_NUMBER=0123456789
BANK_ACCOUNT_NAME=NGUYEN VAN A
```

**⚠️ QUAN TRỌNG:** 
- Thay `0123456789` → Số tài khoản THẬT của bạn
- Thay `NGUYEN VAN A` → Tên chủ TK THẬT (viết HOA, không dấu)
- Chọn `BANK_CODE` từ danh sách dưới

---

## 🏦 DANH SÁCH MÃ NGÂN HÀNG

| Ngân hàng | BANK_CODE |
|-----------|-----------|
| MB Bank | `MB` |
| Vietcombank | `VCB` |
| Techcombank | `TCB` |
| VietinBank | `CTG` |
| BIDV | `BIDV` |
| Agribank | `AGR` |
| ACB | `ACB` |
| Sacombank | `STB` |
| VPBank | `VPB` |
| TPBank | `TPB` |

---

## ✅ BƯỚC 3: SAVE & KIỂM TRA

1. Click **Save Changes** → Render tự động redeploy
2. ⏳ Đợi deploy xong (2-3 phút)
3. Check logs:
   ```
   ✅ PayOS Payment đã được kích hoạt!
   ```

---

## 🧪 BƯỚC 4: TEST THANH TOÁN

### Test tạo QR code:

```bash
curl -X POST https://your-app.onrender.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "plan_type": "lifetime",
    "amount": 100000
  }'
```

**Kết quả mong đợi:**
```json
{
  "success": true,
  "order_id": "...",
  "checkout_url": "https://pay.payos.vn/...",
  "qr_code": "data:image/png;base64,...",
  "bank_info": {
    "account_number": "0123456789",  // Số TK CỦA BẠN
    "account_name": "NGUYEN VAN A"   // Tên CỦA BẠN
  }
}
```

✅ **Nếu thấy thông tin bank CỦA BẠN → THÀNH CÔNG!**

---

## 📡 BƯỚC 5: SETUP WEBHOOK

1. Vào **PayOS Dashboard**: https://my.payos.vn
2. **Cài đặt** → **Webhook**
3. Thêm URL: 
   ```
   https://your-app.onrender.com/api/webhook/payos
   ```
4. Save

---

## 🎉 HOÀN THÀNH!

Giờ hệ thống sẽ:
- ✅ Tạo QR PayOS động cho mỗi đơn hàng
- ✅ Hiển thị thông tin bank CỦA BẠN
- ✅ Tự động tạo license khi thanh toán thành công
- ✅ Gửi email license key

**DONE! 🚀**

