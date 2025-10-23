# 🧪 Hướng Dẫn Test PayOS Webhook

## 📋 Mục Lục
1. [Tổng Quan](#tổng-quan)
2. [Chuẩn Bị](#chuẩn-bị)
3. [Test Local](#test-local)
4. [Test Production](#test-production)
5. [Test Thực Tế với PayOS](#test-thực-tế-với-payos)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Tổng Quan

### Webhook URL
- **Production:** `https://ocr-uufr.onrender.com/payos/webhook`
- **Local:** `http://127.0.0.1:5000/payos/webhook`

### Các Endpoints Liên Quan
```
GET  /payos/webhook       → Verification test
POST /payos/webhook       → Nhận webhook từ PayOS
GET  /payos/health        → Health check
GET  /payos/test          → Test endpoint
POST /payos/simulate      → Simulate webhook (testing only)
```

---

## 🛠️ Chuẩn Bị

### 1. Cài Đặt Dependencies
```bash
pip install requests
```

### 2. Kiểm Tra Server Đang Chạy
```bash
# Local
curl http://127.0.0.1:5000/payos/health

# Production
curl https://ocr-uufr.onrender.com/payos/health
```

### 3. Tạo Order Test
```bash
curl -X POST https://ocr-uufr.onrender.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "plan_type": "lifetime",
    "amount": 100000
  }'
```

**Response:**
```json
{
  "success": true,
  "order_id": "1729685123456",
  "checkout_url": "https://...",
  "qr_code": "https://..."
}
```

**⚠️ Lưu lại `order_id` để test!**

---

## 🏠 Test Local

### Bước 1: Start Server
```bash
cd license_server
python app.py
```

### Bước 2: Chạy Test Script
```bash
# Sửa ENVIRONMENT = "local" trong test_payos_webhook.py
python test_payos_webhook.py
```

### Bước 3: Test Từng Endpoint

#### Test 1: GET Verification
```bash
curl http://127.0.0.1:5000/payos/webhook
```

**Expected Response:**
```json
{
  "code": "00",
  "desc": "success",
  "success": true,
  "data": {
    "status": "webhook_active",
    "service": "payos",
    "version": "2.0",
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

#### Test 2: POST Empty Body
```bash
curl -X POST http://127.0.0.1:5000/payos/webhook \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Test 3: POST Successful Payment
```bash
curl -X POST http://127.0.0.1:5000/payos/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "code": "00",
    "desc": "success",
    "success": true,
    "data": {
      "orderCode": 1729685123456,
      "amount": 100000,
      "description": "Test payment",
      "reference": "TEST20240101120000",
      "transactionDateTime": "2024-01-01 12:00:00"
    }
  }'
```

**Expected Response (nếu order tồn tại):**
```json
{
  "code": "00",
  "desc": "success",
  "success": true,
  "data": {
    "order_id": "1729685123456",
    "license_key": "ABCD-1234-EFGH-5678",
    "email": "test@example.com"
  }
}
```

---

## 🌐 Test Production

### Bước 1: Chạy Test Script
```bash
# ENVIRONMENT = "production" (default)
python test_payos_webhook.py
```

### Bước 2: Test với Order ID Thật
```bash
# Tạo order trước
ORDER_ID=$(curl -X POST https://ocr-uufr.onrender.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","plan_type":"lifetime","amount":100000}' \
  | jq -r '.order_id')

echo "Order ID: $ORDER_ID"

# Test webhook với order_id này
python test_payos_webhook.py $ORDER_ID
```

### Bước 3: Kiểm Tra Logs trên Render
1. Vào [Render Dashboard](https://dashboard.render.com/)
2. Chọn service `ocr-uufr`
3. Click tab **Logs**
4. Tìm dòng log:
   ```
   [WEBHOOK] Method: POST
   [WEBHOOK] 💰 Payment details:
   [WEBHOOK] ✅ SUCCESS!
   ```

---

## 💳 Test Thực Tế với PayOS

### Bước 1: Cấu Hình Webhook trên PayOS Dashboard

1. Đăng nhập [PayOS Dashboard](https://my.payos.vn/)
2. Vào **Cài đặt** → **Webhook**
3. Nhập URL:
   ```
   https://ocr-uufr.onrender.com/payos/webhook
   ```
4. Click **Kiểm tra** → Phải thấy ✅ Success

### Bước 2: Tạo Payment Link Thật

```bash
curl -X POST https://ocr-uufr.onrender.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-real-email@gmail.com",
    "plan_type": "lifetime",
    "amount": 100000
  }'
```

**Response:**
```json
{
  "success": true,
  "order_id": "1729685123456",
  "checkout_url": "https://pay.payos.vn/web/...",
  "qr_code": "https://img.vietqr.io/..."
}
```

### Bước 3: Thanh Toán Test

**Option 1: QR Code**
- Mở app banking
- Quét QR code từ `qr_code` URL
- Chuyển khoản (test với số tiền nhỏ)

**Option 2: Checkout URL**
- Mở `checkout_url` trên browser
- Chọn phương thức thanh toán
- Hoàn tất thanh toán

### Bước 4: Kiểm Tra Webhook Được Gọi

**Trong Render Logs, bạn sẽ thấy:**
```
================================================================================
[WEBHOOK] Method: POST
[WEBHOOK] From: 103.x.x.x (PayOS IP)
[WEBHOOK] 📦 Parsed data: {'code': '00', 'desc': 'success', ...}
[WEBHOOK] 💰 Payment details:
           Order Code: 1729685123456
           Amount: 100,000 VND
           Reference: TF20240101120000
[WEBHOOK] 📋 Order found:
           Order ID: 1729685123456
           Email: your-real-email@gmail.com
           Plan: lifetime
           Status: pending
[WEBHOOK] 🔑 Generating license for order 1729685123456...
✅ Auto-generated license: ABCD-1234-EFGH-5678
   Order ID: 1729685123456
   Email: your-real-email@gmail.com
✅ Email sent to your-real-email@gmail.com via account_1
[WEBHOOK] ✅ SUCCESS!
           License: ABCD-1234-EFGH-5678
           Email: your-real-email@gmail.com
           Plan: lifetime
================================================================================
```

### Bước 5: Kiểm Tra Email

Kiểm tra inbox của `your-real-email@gmail.com`:
- **Subject:** "🎉 License Key của bạn - Vietnamese OCR Tool"
- **Body:** Chứa license key `ABCD-1234-EFGH-5678`

---

## 🔍 Troubleshooting

### ❌ Lỗi: "Order not found"

**Nguyên nhân:** Order ID không tồn tại trong database

**Giải pháp:**
```bash
# Tạo order trước
curl -X POST https://ocr-uufr.onrender.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","plan_type":"lifetime","amount":100000}'
```

---

### ❌ Lỗi: "PayOS not initialized"

**Nguyên nhân:** Thiếu environment variables

**Giải pháp:**
1. Vào Render Dashboard → Environment
2. Thêm:
   ```
   PAYOS_CLIENT_ID=4bbbd884-88f2-410c-9dc8-6782980ef64f
   PAYOS_API_KEY=dd9f4ba8-cc6b-46e8-9afb-930972bf7531
   PAYOS_CHECKSUM_KEY=a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
   ```
3. Redeploy service

---

### ❌ Lỗi: "Failed to generate license"

**Nguyên nhân:** Lỗi trong function `auto_generate_license()`

**Giải pháp:**
```bash
# Kiểm tra logs chi tiết
curl https://ocr-uufr.onrender.com/payos/health

# Kiểm tra database
sqlite3 licenses.db "SELECT * FROM orders WHERE order_id='1729685123456';"
```

---

### ❌ Webhook không được gọi từ PayOS

**Nguyên nhân:** 
- Webhook URL chưa được cấu hình
- URL không accessible từ internet
- PayOS chưa verify URL

**Giải pháp:**

1. **Kiểm tra URL accessible:**
   ```bash
   curl https://ocr-uufr.onrender.com/payos/webhook
   ```
   → Phải trả về status 200

2. **Verify trên PayOS Dashboard:**
   - Vào PayOS → Webhook Settings
   - Click "Kiểm tra URL"
   - Phải thấy ✅ Success

3. **Kiểm tra PayOS IP whitelist:**
   - PayOS gọi webhook từ IP cố định
   - Đảm bảo server không block IP của PayOS

---

### ⚠️ Webhook được gọi nhưng không tạo license

**Nguyên nhân:** Order đã được xử lý trước đó

**Giải pháp:**
```bash
# Kiểm tra order status
curl https://ocr-uufr.onrender.com/api/order/status/1729685123456

# Nếu payment_status = "completed", order đã được xử lý
# Tạo order mới để test
```

---

## 📊 Test Checklist

### ✅ Pre-deployment Checklist
- [ ] Environment variables đã set trên Render
- [ ] PayOS credentials hợp lệ
- [ ] Database đã được init
- [ ] Email sender hoạt động

### ✅ Local Testing Checklist
- [ ] Server start thành công
- [ ] GET /payos/webhook trả về 200
- [ ] POST empty body trả về 200
- [ ] POST với order_id thật tạo được license
- [ ] Health check endpoint hoạt động

### ✅ Production Testing Checklist
- [ ] Webhook URL accessible từ internet
- [ ] PayOS verify webhook URL thành công
- [ ] Test payment thật tạo được license
- [ ] Email được gửi đến customer
- [ ] Logs hiển thị đầy đủ thông tin

### ✅ Integration Testing Checklist
- [ ] Tạo order → Nhận QR code
- [ ] Thanh toán → Webhook được gọi
- [ ] License được tạo tự động
- [ ] Email được gửi tự động
- [ ] Order status = "completed"

---

## 🎯 Quick Test Commands

### Test Webhook Verification
```bash
curl https://ocr-uufr.onrender.com/payos/webhook
```

### Test Health Check
```bash
curl https://ocr-uufr.onrender.com/payos/health
```

### Create Test Order
```bash
curl -X POST https://ocr-uufr.onrender.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","plan_type":"lifetime","amount":100000}'
```

### Simulate Webhook
```bash
curl -X POST https://ocr-uufr.onrender.com/payos/simulate \
  -H "Content-Type: application/json" \
  -d '{"orderCode":1729685123456,"amount":100000}'
```

### Run Full Test Suite
```bash
python test_payos_webhook.py
```

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs trên Render Dashboard
2. Chạy `python test_payos_webhook.py` để debug
3. Kiểm tra PayOS Dashboard → Webhook logs
4. Xem file `payos_handler.py` để hiểu logic xử lý

---

**✅ Hoàn tất! Webhook PayOS đã sẵn sàng!**

