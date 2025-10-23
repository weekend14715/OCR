# Hướng dẫn Test PayOS

## Bước 1: Cấu hình PayOS Credentials

### 1.1. Lấy credentials từ PayOS Dashboard
1. Truy cập: https://my.payos.vn/
2. Đăng nhập/Đăng ký tài khoản
3. Vào **Settings** → **API Keys**
4. Copy 3 thông tin:
   - `Client ID`
   - `API Key`
   - `Checksum Key`

### 1.2. Cấu hình trong server

**Trên local (file `.env`):**
```bash
# Tạo file license_server/.env
PAYOS_CLIENT_ID=your_client_id_here
PAYOS_API_KEY=your_api_key_here
PAYOS_CHECKSUM_KEY=your_checksum_key_here
```

**Trên Render.com:**
1. Vào Dashboard → Your Service → **Environment**
2. Thêm 3 biến môi trường:
   - `PAYOS_CLIENT_ID` = ...
   - `PAYOS_API_KEY` = ...
   - `PAYOS_CHECKSUM_KEY` = ...
3. Click **Save Changes**

## Bước 2: Cấu hình Webhook URL

### 2.1. Lấy Webhook URL
- **Local**: `http://localhost:5000/api/webhook/payos` (dùng ngrok nếu test từ PayOS)
- **Production**: `https://ocr-uufr.onrender.com/api/webhook/payos`

### 2.2. Cấu hình trong PayOS Dashboard
1. Vào https://my.payos.vn/
2. **Settings** → **Webhook**
3. Nhập webhook URL (production URL)
4. Click **Test** → Có thể báo lỗi 404, **bỏ qua và click SAVE**
5. Webhook đã sẵn sàng!

## Bước 3: Test Webhook (Kiểm tra server)

Chạy script test webhook:

```powershell
.\test_payos_webhook.ps1
```

**Kết quả mong đợi:**
- ✓ Test 1 PASSED - Webhook is ready
- ✓ Test 2 PASSED - Correctly rejected non-existent order
- ✓ Test 3 PASSED - Correctly rejected failed payment

## Bước 4: Test Tạo Payment Link

### 4.1. Khởi động server (nếu chưa chạy)

```bash
cd license_server
python app.py
```

Server chạy tại: http://localhost:5000

### 4.2. Chạy script test payment

```powershell
.\test_payos_payment.ps1
```

Script sẽ:
1. Tạo payment link cho license 1 tháng (50,000 VND)
2. Tạo payment link cho license 6 tháng (150,000 VND)
3. Hiển thị checkout URL và QR code

**Kết quả mong đợi:**
```
✓ Thành công!
  Payment Link: https://pay.payos.vn/web/...
  QR Code: https://img.vietqr.io/image/...
  Order Code: 1729712345678
```

### 4.3. Test thanh toán thật

1. **Copy payment link** từ kết quả trên
2. **Mở trong browser**
3. **Quét QR code** bằng app ngân hàng
4. Hoặc chọn ngân hàng để thanh toán

**Sau khi thanh toán thành công:**
- Webhook tự động nhận thông báo
- License được tạo trong database
- Email chứa license key được gửi tới người mua

## Bước 5: Test với Postman/Thunder Client (Tùy chọn)

### Test tạo payment link
```http
POST http://localhost:5000/api/payment/payos/create
Content-Type: application/json

{
    "email": "test@example.com",
    "license_type": "1_month"
}
```

**Response mẫu:**
```json
{
    "checkoutUrl": "https://pay.payos.vn/web/...",
    "qrCode": "https://img.vietqr.io/image/...",
    "orderCode": 1729712345678
}
```

### Test webhook (giả lập PayOS)
```http
POST http://localhost:5000/api/webhook/payos
Content-Type: application/json

{
    "code": "00",
    "desc": "success",
    "success": true,
    "data": {
        "orderCode": 1729712345678,
        "amount": 50000,
        "description": "License 1 month for test@example.com",
        "accountNumber": "12345678",
        "reference": "FT123456",
        "transactionDateTime": "2024-10-23 10:30:00"
    },
    "signature": "test-signature"
}
```

## Bước 6: Kiểm tra kết quả

### 6.1. Check database
```python
python
>>> from license_server.models import db, License
>>> from license_server.app import app
>>> with app.app_context():
...     licenses = License.query.all()
...     for lic in licenses:
...         print(f"Email: {lic.email}, Key: {lic.license_key}, Expires: {lic.expires_at}")
```

### 6.2. Check email
- Kiểm tra hộp thư của email test
- Email tiêu đề: "Your OCR License Key"
- Nội dung chứa license key và hướng dẫn kích hoạt

### 6.3. Check logs
```bash
# Local
python app.py  # Xem console logs

# Render
# Vào Dashboard → Logs
```

## Troubleshooting

### Lỗi: "PAYOS_CLIENT_ID missing"
- ✓ Kiểm tra file `.env` có đúng tên biến không
- ✓ Restart server sau khi thêm biến môi trường

### Lỗi: "Invalid signature"
- ✓ Kiểm tra `PAYOS_CHECKSUM_KEY` đúng chưa
- ✓ PayOS webhook signature verification đã bật chưa?

### Lỗi: "Order not found"
- ✓ OrderCode có đúng định dạng timestamp không?
- ✓ Kiểm tra database có order này không?

### Payment link không hoạt động
- ✓ Tài khoản PayOS đã được kích hoạt chưa?
- ✓ Thông tin ngân hàng đã được cấu hình chưa?
- ✓ Số tiền có hợp lệ không? (tối thiểu 3,000 VND)

### Webhook không nhận được
- ✓ Webhook URL đã đúng trong PayOS dashboard?
- ✓ Server có public accessible không? (dùng ngrok nếu local)
- ✓ Kiểm tra logs của server

## Test với số tiền nhỏ

Để test an toàn, tạo order với số tiền nhỏ:

```python
# Sửa trong license_server/payos_handler.py
LICENSE_PRICES = {
    '1_month': 3000,    # 3,000 VND (test)
    '6_months': 5000,   # 5,000 VND (test)
    '1_year': 10000     # 10,000 VND (test)
}
```

## Tóm tắt

```bash
# 1. Cấu hình credentials
# → Vào PayOS dashboard lấy keys
# → Thêm vào .env hoặc Render environment

# 2. Cấu hình webhook
# → Vào PayOS Settings → Webhook
# → Nhập URL và SAVE

# 3. Test webhook
.\test_payos_webhook.ps1

# 4. Test payment
.\test_payos_payment.ps1

# 5. Thanh toán thật
# → Mở payment link
# → Quét QR hoặc chọn ngân hàng
# → Kiểm tra email nhận license key
```

---

**Lưu ý:**
- PayOS cần tài khoản đã xác thực để nhận tiền thật
- Test webhook có thể báo 404, bỏ qua và SAVE
- Luôn test với số tiền nhỏ trước (3,000 VND)
- Kiểm tra email spam folder nếu không nhận được email

