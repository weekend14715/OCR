# 🚀 HƯỚNG DẪN SETUP PAYOS

## 📋 THÔNG TIN CREDENTIALS

Bạn đã có credentials PayOS:

```
Client ID: 4bbbd884-88f2-410c-9dc8-6782980ef64f
API Key: dd9f4ba8-cc6b-46e8-9afb-930972bf7531
Checksum Key: a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
```

---

## ⚙️ SETUP TRÊN RENDER

### Bước 1: Thêm Environment Variables

Vào **Render Dashboard** → **license-server** → **Environment**

Thêm 3 biến:

```bash
PAYOS_CLIENT_ID=4bbbd884-88f2-410c-9dc8-6782980ef64f
PAYOS_API_KEY=dd9f4ba8-cc6b-46e8-9afb-930972bf7531
PAYOS_CHECKSUM_KEY=a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
```

**Xóa các biến cũ (nếu có):**
- `CASSO_API_KEY`
- `CASSO_BUSINESS_ID`
- `CASSO_CHECKSUM_KEY`

### Bước 2: Save → Tự động Deploy

Render sẽ tự động rebuild với PayOS!

---

## 📡 SETUP WEBHOOK TRÊN PAYOS

### URL Webhook của bạn:

```
https://[your-render-domain]/api/webhook/payos
```

**Cách thêm:**

1. Vào **PayOS Dashboard**: https://my.payos.vn
2. **Settings** → **Webhook**
3. Thêm URL: `https://your-app.onrender.com/api/webhook/payos`
4. **Save**

---

## 🧪 TESTING

### Test 1: Tạo QR Code Thanh Toán

```bash
curl -X POST https://your-app.onrender.com/api/payment/create \
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
  "order_id": "1234567890",
  "checkout_url": "https://pay.payos.vn/...",
  "qr_code": "https://qr.payos.vn/...",
  "amount": 100000,
  "plan_type": "lifetime"
}
```

### Test 2: Quét QR & Thanh Toán

1. Mở `qr_code` URL trên điện thoại
2. Quét bằng app ngân hàng
3. Thanh toán 100,000 VND
4. PayOS sẽ gọi webhook → tự động tạo license!

### Test 3: Kiểm Tra License

```bash
curl https://your-app.onrender.com/api/admin/orders \
  -H "X-Admin-API-Key: your-secure-admin-api-key-here-change-this"
```

---

## 🎯 FLOW THANH TOÁN

```
1. Client → POST /api/payment/create
   ↓
2. Server tạo order trong DB (status: pending)
   ↓
3. Server gọi PayOS API → nhận QR code
   ↓
4. Return QR code cho client
   ↓
5. User quét QR & thanh toán
   ↓
6. PayOS → POST /api/webhook/payos (thanh toán thành công)
   ↓
7. Server tự động tạo license key
   ↓
8. Gửi email license cho customer
   ↓
9. DONE! ✅
```

---

## 📊 ENDPOINTS MỚI

### 1. Tạo Payment

**POST** `/api/payment/create`

```json
{
  "email": "customer@example.com",
  "plan_type": "lifetime",
  "amount": 100000
}
```

### 2. Webhook PayOS

**POST** `/api/webhook/payos`

Endpoint này PayOS sẽ tự động gọi khi thanh toán thành công.

### 3. Test Webhook (Admin Only)

**POST** `/api/payos/test-webhook`

```bash
curl -X POST https://your-app.onrender.com/api/payos/test-webhook \
  -H "X-Admin-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "1234567890",
    "amount": 100000
  }'
```

---

## 🔥 LƯU Ý QUAN TRỌNG

### ⚠️ Order ID Format

PayOS yêu cầu `orderCode` phải là **số nguyên**.

Server tự động tạo: `int(timestamp * 1000)`

Ví dụ: `1729584000000`

### ⚠️ Webhook Signature

Hiện tại webhook **không verify signature** (commented out).

Để bật, uncomment dòng này trong `app.py`:

```python
if signature and not verify_webhook_signature(data.get('data', {}), signature):
    print("⚠️ Invalid signature")
    return jsonify({'error': 'Invalid signature'}), 401
```

### ⚠️ Return URL

Hiện tại return URL là placeholder:

```python
return_url=f"https://your-app.com/payment/success?order_id={order_id}"
```

**Cần thay bằng domain thật của frontend!**

---

## 🎉 KẾT QUẢ

Sau khi deploy:

✅ **PayOS đã được kích hoạt!** (trong logs)
✅ QR code động cho từng đơn hàng
✅ Webhook tự động tạo license
✅ Email thông báo license key
✅ Admin có thể track tất cả orders

**DONE! Hệ thống thanh toán tự động hoàn chỉnh!** 🚀

