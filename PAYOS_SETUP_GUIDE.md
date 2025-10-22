# 🚀 HƯỚNG DẪN SETUP PAYOS - WEBHOOK & PAYMENT

## 📋 THÔNG TIN PAYOS CỦA ANH

```
✅ Client ID:  4bbbd884-88f2-410c-9dc8-6782980ef64f
✅ API Key:    dd9f4ba8-cc6b-46e8-9afb-930972bf7531
✅ Checksum:   a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
```

---

## 🎯 CÁC BƯỚC SETUP (10 phút)

### **BƯỚC 1: Cập nhật Render Environment Variables** ⚙️

1. **Vào Render Dashboard:**
   ```
   https://dashboard.render.com
   ```

2. **Chọn service:** `ocr-uufr`

3. **Click tab "Environment"**

4. **Thêm 3 biến môi trường PayOS:**

   | Key | Value |
   |-----|-------|
   | `PAYOS_CLIENT_ID` | `4bbbd884-88f2-410c-9dc8-6782980ef64f` |
   | `PAYOS_API_KEY` | `dd9f4ba8-cc6b-46e8-9afb-930972bf7531` |
   | `PAYOS_CHECKSUM_KEY` | `a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d` |

   **Cách thêm:**
   - Click **"Add Environment Variable"**
   - Nhập Key và Value
   - Click **"Add"**
   - Lặp lại cho 3 biến

5. **Save Changes** → Chờ Render auto-deploy (2-3 phút)

---

### **BƯỚC 2: Cấu hình Webhook trên PayOS Dashboard** 🔗

1. **Đăng nhập PayOS Dashboard:**
   ```
   https://my.payos.vn/
   ```

2. **Vào mục Settings → Webhook**

3. **Thêm Webhook URL:**
   ```
   https://ocr-uufr.onrender.com/api/webhook/payos
   ```

4. **Webhook Events:** Chọn các sự kiện:
   - ✅ `Payment Success` (Thanh toán thành công)
   - ✅ `Payment Cancelled` (Hủy thanh toán)
   - ✅ `Payment Failed` (Thanh toán thất bại)

5. **Save Webhook Settings**

---

### **BƯỚC 3: Test PayOS Payment** 🧪

#### **Option 1: Test bằng PowerShell Script**

Em tạo script test cho anh:

```powershell
# test_payos_payment.ps1

$baseUrl = "https://ocr-uufr.onrender.com"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  TEST PAYOS PAYMENT INTEGRATION" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Tạo payment link
Write-Host "[1/3] Creating PayOS Payment Link..." -ForegroundColor Yellow

$createPayload = @{
    plan_type = "lifetime"
    customer_email = "hoangtuan.th484@gmail.com"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/payment/payos/create" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $createPayload

    Write-Host "✅ Payment Link Created!" -ForegroundColor Green
    Write-Host "   Order ID: $($response.order_id)" -ForegroundColor White
    Write-Host "   Amount: $($response.amount) VND" -ForegroundColor White
    Write-Host "   Checkout URL: $($response.checkout_url)" -ForegroundColor Cyan
    Write-Host "   QR Code: $($response.qr_code)" -ForegroundColor Cyan
    Write-Host ""
    
    $orderId = $response.order_id
    
    # Test 2: Kiểm tra order status
    Write-Host "[2/3] Checking Order Status..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    $orderResponse = Invoke-RestMethod -Uri "$baseUrl/api/orders/$orderId" -Method GET
    
    Write-Host "✅ Order Status Retrieved!" -ForegroundColor Green
    Write-Host "   Status: $($orderResponse.payment_status)" -ForegroundColor White
    Write-Host ""
    
    # Test 3: Test webhook manually (simulate PayOS callback)
    Write-Host "[3/3] Testing Webhook Handler..." -ForegroundColor Yellow
    Write-Host "ℹ️  Note: Webhook sẽ tự động được gọi khi thanh toán thực tế" -ForegroundColor Gray
    Write-Host ""
    
    $webhookPayload = @{
        code = "00"
        desc = "success"
        success = $true
        data = @{
            orderCode = [int]$orderId
            amount = 199000
            description = "Thanh toán License OCR Tool - LIFETIME"
            accountNumber = "123456789"
            reference = "FT123456789"
            transactionDateTime = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
            currency = "VND"
            paymentLinkId = "test-payment-link-id"
            code = "00"
            desc = "Thành công"
            counterAccountBankId = ""
            counterAccountBankName = ""
            counterAccountName = "NGUYEN VAN A"
            counterAccountNumber = "987654321"
            virtualAccountName = ""
            virtualAccountNumber = ""
        }
    } | ConvertTo-Json -Depth 5
    
    $webhookResponse = Invoke-RestMethod -Uri "$baseUrl/api/webhook/payos" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $webhookPayload
    
    Write-Host "✅ Webhook Test Complete!" -ForegroundColor Green
    Write-Host "   Message: $($webhookResponse.message)" -ForegroundColor White
    
    if ($webhookResponse.license_key) {
        Write-Host "   License Key: $($webhookResponse.license_key)" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Mở QR Code URL để scan và thanh toán thực tế" -ForegroundColor White
Write-Host "2. PayOS sẽ tự động gọi webhook sau khi thanh toán" -ForegroundColor White
Write-Host "3. License key sẽ được tạo và gửi email tự động" -ForegroundColor White
Write-Host ""
```

**Chạy script:**
```powershell
powershell -ExecutionPolicy Bypass -File test_payos_payment.ps1
```

#### **Option 2: Test bằng cURL**

```bash
# Tạo payment link
curl -X POST https://ocr-uufr.onrender.com/api/payment/payos/create \
  -H "Content-Type: application/json" \
  -d '{"plan_type":"lifetime","customer_email":"hoangtuan.th484@gmail.com"}'
```

---

### **BƯỚC 4: Thanh toán Thực Tế & Verify** 💳

1. **Tạo payment link** (bằng script trên hoặc cURL)

2. **Mở Checkout URL** trong trình duyệt hoặc **Scan QR Code**

3. **Thanh toán test:**
   - Dùng app ngân hàng để scan QR
   - Hoặc dùng PayOS sandbox (nếu có)

4. **Sau khi thanh toán:**
   - ✅ PayOS tự động gọi webhook: `/api/webhook/payos`
   - ✅ Server tạo license key
   - ✅ Email tự động gửi đến khách hàng
   - ✅ Order status update thành `completed`

5. **Verify email nhận được:**
   - Check inbox: `hoangtuan.th484@gmail.com`
   - Subject: "🎉 License Key OCR Tool - LIFETIME"
   - License key trong email

---

## 🔍 ENDPOINTS PAYOS

### **1. Tạo Payment Link**
```http
POST /api/payment/payos/create
Content-Type: application/json

{
  "plan_type": "monthly|yearly|lifetime",
  "customer_email": "customer@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "order_id": "1729123456789",
  "amount": 199000,
  "checkout_url": "https://pay.payos.vn/...",
  "qr_code": "https://qr.payos.vn/...",
  "payment_link_id": "..."
}
```

### **2. Webhook (PayOS tự động gọi)**
```http
POST /api/webhook/payos
Content-Type: application/json

{
  "code": "00",
  "desc": "success",
  "success": true,
  "data": {
    "orderCode": 1729123456789,
    "amount": 199000,
    "description": "...",
    "transactionDateTime": "2024-10-22T10:30:00",
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Thanh toán thành công!",
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "email_sent": true
}
```

### **3. Kiểm tra Order Status**
```http
GET /api/orders/{order_id}
```

**Response:**
```json
{
  "order_id": "1729123456789",
  "plan_type": "lifetime",
  "amount": 199000,
  "payment_status": "completed",
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "customer_email": "customer@example.com",
  "paid_at": "2024-10-22T10:30:00"
}
```

---

## 🎨 FLOW HOÀN CHỈNH

```
┌─────────────────────────────────────────────────────────────────┐
│  1. KHÁCH HÀNG YÊU CẦU MUA LICENSE                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. FRONTEND GỌI: POST /api/payment/payos/create                │
│     - plan_type: "lifetime"                                     │
│     - customer_email: "customer@example.com"                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. SERVER TẠO ORDER TRONG DATABASE                             │
│     - order_id: timestamp (unique)                              │
│     - payment_status: "pending"                                 │
│     - amount: 199,000 VND (lifetime)                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. GỌI PAYOS API ĐỂ TẠO PAYMENT LINK                          │
│     - Nhận checkout_url                                         │
│     - Nhận qr_code URL                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. TRẢ VỀ FRONTEND: QR Code + Checkout URL                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. KHÁCH HÀNG SCAN QR HOẶC MỞ CHECKOUT URL                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  7. THANH TOÁN QUA APP NGÂN HÀNG                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  8. PAYOS TỰ ĐỘNG GỌI WEBHOOK: POST /api/webhook/payos         │
│     - data.orderCode: order_id                                  │
│     - data.amount: 199000                                       │
│     - data.transactionDateTime: timestamp                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  9. SERVER XỬ LÝ WEBHOOK:                                       │
│     ✅ Verify signature (checksum)                              │
│     ✅ Update order status → "completed"                        │
│     ✅ Tạo license key tự động                                  │
│     ✅ Lưu vào database                                         │
│     ✅ Gửi email với license key                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  10. KHÁCH HÀNG NHẬN EMAIL VỚI LICENSE KEY!                     │
│      Subject: "🎉 License Key OCR Tool - LIFETIME"              │
│      Content: License key + Hướng dẫn kích hoạt                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 BẢNG GIÁ

| Plan | Giá (VND) | Thời hạn |
|------|-----------|----------|
| Monthly | 49,000 | 30 ngày |
| Yearly | 99,000 | 365 ngày |
| Lifetime | 199,000 | Vĩnh viễn |

*(Được định nghĩa trong `payment_gateway.py`)*

---

## 🧪 DEBUG & MONITORING

### **1. Check PayOS Config**
```bash
curl https://ocr-uufr.onrender.com/api/debug/payos-config
```

### **2. Check Render Logs**
```
https://dashboard.render.com/web/YOUR_SERVICE/logs
```

Tìm các log:
- `✅ PayOS đã được kích hoạt!`
- `📩 Received PayOS webhook: {...}`
- `✅ Successfully processed PayOS payment: {order_code}`

### **3. Check Order Status**
```bash
curl https://ocr-uufr.onrender.com/api/orders/{order_id}
```

---

## ⚠️ TROUBLESHOOTING

### **Lỗi: "PayOS not configured"**
**Nguyên nhân:** Environment variables chưa được set  
**Giải pháp:** 
1. Vào Render → Environment
2. Thêm 3 biến: `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY`
3. Save → Chờ deploy

### **Lỗi: "PayOS not initialized"**
**Nguyên nhân:** Credentials sai hoặc PayOS service down  
**Giải pháp:**
1. Check logs: `https://dashboard.render.com`
2. Verify credentials trên PayOS dashboard
3. Test lại sau vài phút

### **Webhook không được gọi**
**Nguyên nhân:** Webhook URL chưa đăng ký trên PayOS  
**Giải pháp:**
1. Vào PayOS Dashboard → Settings → Webhook
2. Add URL: `https://ocr-uufr.onrender.com/api/webhook/payos`
3. Enable events: Payment Success, Failed, Cancelled

### **Email không gửi sau thanh toán**
**Nguyên nhân:** Email config chưa setup hoặc Gmail App Password sai  
**Giải pháp:**
1. Đọc `QUICK_START.md` để setup email
2. Verify `EMAIL_ACCOUNTS` env var đã set
3. Test email: `/api/debug/test-email`

---

## 🎯 CHECKLIST SETUP

- [ ] **Bước 1:** Add 3 env vars vào Render (PAYOS_CLIENT_ID, API_KEY, CHECKSUM_KEY)
- [ ] **Bước 2:** Save → Chờ Render deploy (2-3 phút)
- [ ] **Bước 3:** Vào PayOS Dashboard → Add webhook URL
- [ ] **Bước 4:** Enable webhook events (Payment Success, etc.)
- [ ] **Bước 5:** Test tạo payment link (chạy script test)
- [ ] **Bước 6:** Verify QR code hiển thị
- [ ] **Bước 7:** Thanh toán test
- [ ] **Bước 8:** Verify webhook được gọi (check logs)
- [ ] **Bước 9:** Verify license key được tạo
- [ ] **Bước 10:** Verify email được gửi

---

## 📱 PAYOS SANDBOX (Optional)

Nếu PayOS có sandbox/test mode, anh có thể test mà không cần thanh toán thực:

1. Vào PayOS Dashboard → Settings → Sandbox Mode
2. Enable sandbox
3. Dùng test card để thanh toán

---

## 🚀 PRODUCTION READY!

Sau khi hoàn thành checklist, hệ thống sẽ:

✅ Tự động nhận thanh toán từ PayOS  
✅ Tự động tạo license key  
✅ Tự động gửi email cho khách hàng  
✅ Tự động cập nhật database  
✅ Hoàn toàn tự động, không cần can thiệp thủ công!  

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề, check:

1. **Render Logs:** `https://dashboard.render.com/web/YOUR_SERVICE/logs`
2. **PayOS Dashboard:** `https://my.payos.vn/`
3. **Email Config:** Đọc `QUICK_START.md`
4. **Debug Endpoints:** 
   - `/api/debug/payos-config`
   - `/api/debug/email-config`
   - `/api/orders/{order_id}`

---

**Created:** 2024-10-22  
**Status:** ✅ Ready to Setup  
**Next:** Follow Step 1 → Add env vars to Render

---

