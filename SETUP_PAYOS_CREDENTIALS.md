# 🔐 Cách Tích Hợp Thông Tin PayOS

## Thông Tin PayOS Của Bạn

```
Client ID:     4bbbd884-88f2-410c-9dc8-6782980ef64f
API Key:       dd9f4ba8-cc6b-46e8-9afb-930972bf7531
Checksum Key:  a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
```

---

## 📋 Bước 1: Thêm Environment Variables trên Render

### Cách thêm:

1. **Truy cập Render Dashboard**:
   - Vào https://dashboard.render.com/
   - Chọn service: `license-server-hjat`

2. **Vào phần Environment**:
   - Click tab **"Environment"** ở menu bên trái
   - Scroll xuống phần **"Environment Variables"**

3. **Thêm 3 biến sau**:

| Key | Value |
|-----|-------|
| `PAYOS_CLIENT_ID` | `4bbbd884-88f2-410c-9dc8-6782980ef64f` |
| `PAYOS_API_KEY` | `dd9f4ba8-cc6b-46e8-9afb-930972bf7531` |
| `PAYOS_CHECKSUM_KEY` | `a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d` |

4. **Click "Save Changes"**
   - Render sẽ tự động **redeploy** service
   - Đợi khoảng **2-3 phút** để hoàn tất

---

## 📋 Bước 2: Commit Code và Push lên GitHub

Sau khi thêm Environment Variables, bạn cần push code đã fix lỗi Unicode:

```bash
cd F:\OCR\OCR\license_server
git add payos_handler.py app.py
git commit -m "fix: Remove Unicode characters causing server startup errors"
git push origin main
```

Render sẽ tự động deploy code mới.

---

## ✅ Bước 3: Kiểm Tra PayOS Đã Hoạt Động

### 3.1. Kiểm tra logs trên Render

Sau khi deploy xong, vào **Logs** tab và tìm dòng:

```
PayOS activated successfully!
Available methods: ['cancelPaymentLink', 'confirmWebhook', 'createPaymentLink', 'getPaymentLinkInformation']
PayOS Blueprint registered at /payos/*
```

Nếu thấy dòng này → **PayOS đã hoạt động!** ✅

### 3.2. Test API tạo PayOS Payment

```powershell
# Test tạo payment link PayOS
Invoke-WebRequest -Uri "https://license-server-hjat.onrender.com/api/payments/create-payos" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"plan":"basic","customer_email":"test@example.com"}' | 
  Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Kết quả mong đợi**:
```json
{
  "success": true,
  "order_id": "PAYOS-123456...",
  "payment_url": "https://pay.payos.vn/...",
  "qr_code_url": "https://qr.payos.vn/...",
  "amount": 99000,
  "plan": "basic"
}
```

---

## 🧪 Bước 4: Test Webhook từ PayOS

### 4.1. Webhook URL để cấu hình trong PayOS Dashboard

```
https://license-server-hjat.onrender.com/payos/webhook
```

### 4.2. Cách test webhook thủ công

Sau khi thanh toán test, PayOS sẽ gửi webhook đến server của bạn. Server sẽ:

1. ✅ Xác thực chữ ký webhook
2. ✅ Tạo license key tự động
3. ✅ Gửi email license cho khách hàng (nếu EMAIL_ENABLED=True)
4. ✅ Cập nhật trạng thái đơn hàng

### 4.3. Kiểm tra license sau thanh toán

```powershell
# Kiểm tra license vừa tạo
Invoke-WebRequest -Uri "https://license-server-hjat.onrender.com/api/verify-license" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"license_key":"BASIC-XXXX-YYYY-ZZZZ","hwid":"test-hwid"}' | 
  Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 📱 Bước 5: Tích Hợp Vào UI (Nếu cần)

### Frontend code để hiển thị PayOS QR

```javascript
async function createPayOSPayment(plan, email) {
  const response = await fetch('https://license-server-hjat.onrender.com/api/payments/create-payos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan, customer_email: email })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Hiển thị QR code
    document.getElementById('qr-image').src = data.qr_code_url;
    
    // Hoặc chuyển hướng đến trang thanh toán
    window.location.href = data.payment_url;
  }
}
```

---

## 🔍 Troubleshooting

### Nếu PayOS không hoạt động

1. **Kiểm tra Environment Variables trên Render**:
   - Đảm bảo 3 biến `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY` đã được thêm chính xác
   - Không có khoảng trắng thừa ở đầu/cuối giá trị

2. **Kiểm tra Logs trên Render**:
   - Nếu thấy: `Warning: PayOS credentials not configured`
     → Environment Variables chưa được thêm hoặc sai tên

   - Nếu thấy: `Error initializing PayOS: ...`
     → Thông tin credentials có thể không đúng, hãy kiểm tra lại trên PayOS Dashboard

3. **Kiểm tra thư viện payos đã được cài**:
   - File `requirements.txt` phải có dòng: `payos==1.0.0`
   - Render tự động cài khi deploy

4. **Test thủ công**:
   ```powershell
   # Test health endpoint
   Invoke-WebRequest -Uri "https://license-server-hjat.onrender.com/health" -UseBasicParsing
   ```

---

## 📊 Monitoring

Sau khi PayOS hoạt động, bạn có thể:

1. **Xem lịch sử giao dịch**: https://license-server-hjat.onrender.com/admin
2. **Xem logs real-time**: https://dashboard.render.com → Logs tab
3. **Kiểm tra webhook logs**: PayOS Dashboard → Webhooks

---

## 🚀 Tóm Tắt

| Bước | Mô tả | Trạng thái |
|------|-------|------------|
| 1 | Fix lỗi Unicode trong code | ✅ Hoàn thành |
| 2 | Thêm Environment Variables trên Render | ⏳ **BẠN CẦN LÀM** |
| 3 | Push code lên GitHub | ⏳ **BẠN CẦN LÀM** |
| 4 | Đợi Render deploy | ⏳ Tự động |
| 5 | Test API PayOS | ⏳ Sau khi deploy |
| 6 | Cấu hình webhook URL trong PayOS | ⏳ Tùy chọn |

---

## 🎯 Next Steps

Sau khi hoàn thành các bước trên:

1. **Test thanh toán thật**: Tạo đơn hàng test với số tiền nhỏ (VD: 1,000 VND)
2. **Xem email**: Kiểm tra xem license có được gửi tự động không
3. **Verify license**: Test xác thực license vừa mua

---

**Có vấn đề gì hãy hỏi tôi nhé!** 🚀

