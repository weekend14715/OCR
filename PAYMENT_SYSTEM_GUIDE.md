# 💳 Hệ Thống Thanh Toán Tự Động - Hướng Dẫn Đầy Đủ

## 📋 Tổng Quan

Hệ thống thanh toán tự động cho phép khách hàng:
- ✅ Thanh toán trực tuyến (VNPay/MoMo/ZaloPay)
- ✅ Nhận license key **NGAY LẬP TỨC** sau khi thanh toán
- ✅ **1 máy = 1 license key = 1 lần kích hoạt**
- ✅ Không cần admin can thiệp
- ✅ Hoàn toàn tự động từ đầu đến cuối

---

## 🎯 Quy Trình Hoạt Động

```
Khách chọn gói → Nhập email → Chọn payment → 
Thanh toán → Callback tự động → 
Generate license → Hiển thị key → 
Khách nhập vào app → Kích hoạt
```

### Chi tiết từng bước:

1. **Khách truy cập website** → `http://yourdomain.com/`
2. **Chọn gói** (Monthly/Yearly/Lifetime)
3. **Nhập email** trong modal
4. **Chọn payment method** (VNPay/MoMo/ZaloPay)
5. **Redirect đến cổng thanh toán**
6. **Khách thanh toán** qua app/web banking
7. **Callback tự động** về server
8. **License key tự động generate**
9. **Redirect đến success page** với license key
10. **Khách copy key** và nhập vào OCR app
11. **License binding vào máy** → Chỉ máy này dùng được

---

## 🏗️ Kiến Trúc Hệ Thống

### Database Schema

```sql
-- Bảng orders (tracking payments)
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    order_id TEXT UNIQUE NOT NULL,      -- ORD20250121123456ABCD
    plan_type TEXT NOT NULL,            -- monthly/yearly/lifetime
    amount INTEGER NOT NULL,            -- VNĐ
    customer_email TEXT,
    payment_method TEXT,                -- vnpay/momo/zalopay
    payment_status TEXT DEFAULT 'pending',  -- pending/completed/failed
    transaction_id TEXT,                -- From payment gateway
    license_key TEXT,                   -- Auto-generated after payment
    created_at TEXT NOT NULL,
    paid_at TEXT,
    expires_at TEXT
);

-- Bảng licenses (existing)
CREATE TABLE licenses (
    id INTEGER PRIMARY KEY,
    license_key TEXT UNIQUE NOT NULL,
    email TEXT,
    machine_id TEXT,                    -- Hardware fingerprint
    activation_date TEXT,
    expiry_date TEXT,
    plan_type TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    last_validated TEXT,
    order_id TEXT                       -- Link to order
);
```

### API Endpoints

#### Public Endpoints (No Auth Required)

```
POST /api/payment/create
    Create payment and redirect to gateway
    Body: {
        "plan_type": "lifetime",
        "payment_method": "vnpay",
        "customer_email": "user@example.com"
    }
    Response: {
        "success": true,
        "order_id": "ORD20250121...",
        "payment_url": "https://sandbox.vnpayment.vn/...",
        "amount": 1999000,
        "plan": "lifetime"
    }

GET /api/payment/vnpay/callback
    VNPay callback endpoint (auto-called by VNPay)
    Validates payment → Generates license → Redirects to /success

GET/POST /api/payment/momo/callback
    MoMo callback endpoint

POST /api/payment/zalopay/callback
    ZaloPay callback endpoint

GET /success?license_key=XXXX-XXXX-XXXX-XXXX
    Success page showing license key

GET /failed
    Payment failed page

GET /api/order/status/<order_id>
    Check order status and get license if paid
```

---

## 🔧 Cài Đặt & Cấu Hình

### 1. Đăng Ký Payment Gateways

#### VNPay
1. Đăng ký tại: https://vnpay.vn/dang-ky-merchant
2. Lấy `TMN Code` và `Hash Secret`
3. Cấu hình trong `payment_gateway.py`:
   ```python
   VNPAY_CONFIG = {
       'vnp_TmnCode': 'YOUR_CODE',
       'vnp_HashSecret': 'YOUR_SECRET',
       'vnp_Url': 'https://pay.vnpay.vn/vpcpay.html',  # Production
       'vnp_ReturnUrl': 'https://yourdomain.com/api/payment/vnpay/callback',
   }
   ```

#### MoMo
1. Đăng ký tại: https://business.momo.vn
2. Lấy `Partner Code`, `Access Key`, `Secret Key`
3. Cấu hình trong `payment_gateway.py`:
   ```python
   MOMO_CONFIG = {
       'partnerCode': 'YOUR_CODE',
       'accessKey': 'YOUR_KEY',
       'secretKey': 'YOUR_SECRET',
       'endpoint': 'https://payment.momo.vn/v2/gateway/api/create',
       'returnUrl': 'https://yourdomain.com/api/payment/momo/callback',
       'notifyUrl': 'https://yourdomain.com/api/payment/momo/callback',
   }
   ```

#### ZaloPay
1. Đăng ký tại: https://zalopay.vn/business
2. Lấy `App ID`, `Key1`, `Key2`
3. Cấu hình trong `payment_gateway.py`:
   ```python
   ZALOPAY_CONFIG = {
       'app_id': 'YOUR_APP_ID',
       'key1': 'YOUR_KEY1',
       'key2': 'YOUR_KEY2',
       'endpoint': 'https://openapi.zalopay.vn/v2/create',
       'callback_url': 'https://yourdomain.com/api/payment/zalopay/callback',
   }
   ```

### 2. Update Callback URLs

**QUAN TRỌNG:** Callback URLs phải là HTTPS và public accessible!

Trong production, thay đổi URLs trong `payment_gateway.py`:
```python
# Thay 'yourdomain.com' bằng domain thật của bạn
'vnp_ReturnUrl': 'https://yourdomain.com/api/payment/vnpay/callback',
'returnUrl': 'https://yourdomain.com/api/payment/momo/callback',
'callback_url': 'https://yourdomain.com/api/payment/zalopay/callback',
```

### 3. Cài Dependencies

```bash
cd license_server
pip install -r requirements.txt
```

Nếu thiếu dependencies, thêm vào `requirements.txt`:
```
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
```

---

## 🚀 Chạy Hệ Thống

### Development (Local Testing)

```bash
cd license_server
python app.py
```

Server chạy tại: `http://127.0.0.1:5000`

**Note:** Payment callbacks sẽ KHÔNG hoạt động ở localhost vì payment gateways không thể gọi về. Cần deploy lên server hoặc dùng ngrok.

### Production Deployment

#### Option 1: VPS (Recommended)

```bash
# 1. Clone code lên server
git clone your-repo
cd license_server

# 2. Install dependencies
pip3 install -r requirements.txt
pip3 install gunicorn

# 3. Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 4. Setup Nginx reverse proxy
sudo nano /etc/nginx/sites-available/license-server

# Nginx config:
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 5. Enable site and reload
sudo ln -s /etc/nginx/sites-available/license-server /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 6. Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### Option 2: PythonAnywhere (Easy)

1. Upload code to PythonAnywhere
2. Set up web app with Flask
3. Configure WSGI file to point to `app.py`
4. Update callback URLs to PythonAnywhere domain

#### Option 3: Heroku

```bash
# 1. Create Procfile
echo "web: gunicorn app:app" > Procfile

# 2. Create runtime.txt
echo "python-3.11.0" > runtime.txt

# 3. Deploy
heroku create your-app-name
git push heroku main
```

---

## 🧪 Testing Payment Flow

### Test với Sandbox

Tất cả payment gateways đều có sandbox environment:

#### VNPay Sandbox
- URL: `https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`
- Test cards: https://sandbox.vnpayment.vn/apis/docs/huong-dan-test/

#### MoMo Test
- Endpoint: `https://test-payment.momo.vn/v2/gateway/api/create`
- Test account: Sử dụng app MoMo test

#### ZaloPay Sandbox
- Endpoint: `https://sb-openapi.zalopay.vn/v2/create`
- Docs: https://docs.zalopay.vn/

### Test Flow

```bash
# 1. Start server
python app.py

# 2. Open browser
http://localhost:5000

# 3. Click "Mua Ngay" on Lifetime plan
# 4. Enter email: test@example.com
# 5. Click VNPay/MoMo/ZaloPay
# 6. Complete test payment
# 7. Should redirect to /success with license key
# 8. Copy key and test in OCR app
```

### Test với ngrok (Local Testing)

```bash
# 1. Install ngrok
# Download from: https://ngrok.com/

# 2. Start ngrok
ngrok http 5000

# 3. Update callback URLs in payment_gateway.py với ngrok URL
# Example: https://abc123.ngrok.io/api/payment/vnpay/callback

# 4. Test payment flow
```

---

## 💻 Frontend Integration

### HTML Structure (Already implemented)

Website có 3 components chính:

1. **Pricing Cards** - Hiển thị 3 gói giá
2. **Payment Modal** - Nhập email + chọn payment method
3. **Success/Failed Pages** - Hiển thị kết quả

### JavaScript Payment Flow

```javascript
// When user clicks "Mua Ngay"
function showPurchaseModal(plan, price) {
    // Show modal with email input
}

// When user selects payment method
async function processPayment(paymentMethod) {
    // 1. Get email
    const email = document.getElementById('customerEmail').value;
    
    // 2. Call API
    const response = await fetch('/api/payment/create', {
        method: 'POST',
        body: JSON.stringify({
            plan_type: selectedPlan,
            payment_method: paymentMethod,
            customer_email: email
        })
    });
    
    // 3. Redirect to payment gateway
    window.location.href = data.payment_url;
}
```

---

## 🔐 Bảo Mật

### Machine Binding (1 License = 1 Máy)

Khi khách nhập license key vào OCR app:

1. **Lần đầu kích hoạt:**
   - App gọi `/api/validate` với `license_key` + `machine_id`
   - Server check: `machine_id` chưa có trong DB
   - Server **lưu `machine_id`** vào license record
   - Response: `{"valid": true, "activated": true}`

2. **Lần sau validate (cùng máy):**
   - App gọi `/api/validate` với `license_key` + `machine_id`
   - Server check: `machine_id` **KHỚP** với DB
   - Response: `{"valid": true}`

3. **Nếu dùng trên máy khác:**
   - App gọi `/api/validate` với `license_key` + `machine_id_khac`
   - Server check: `machine_id_khac` **KHÔNG KHỚP** với DB
   - Response: `{"valid": false, "error": "License đã kích hoạt trên máy khác"}`

### Machine ID Generation

```python
def get_machine_id():
    """Generate unique machine fingerprint"""
    hostname = platform.node()
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                    for i in range(0,8*6,8)][::-1])
    cpu_info = platform.processor()
    
    # Combine and hash
    unique_string = f"{hostname}-{mac}-{cpu_info}"
    return hashlib.sha256(unique_string.encode()).hexdigest()
```

### Payment Verification

Mỗi payment gateway trả về signature để verify:

- **VNPay:** HMAC-SHA512
- **MoMo:** HMAC-SHA256
- **ZaloPay:** HMAC-SHA256

Server **PHẢI** verify signature trước khi generate license!

```python
def verify_payment_response(params):
    # 1. Extract signature
    received_signature = params.get('signature')
    
    # 2. Calculate expected signature
    calculated_signature = hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 3. Compare
    if calculated_signature != received_signature:
        return False  # Invalid!
    
    return True
```

---

## 📊 Giám Sát & Logs

### Database Queries

```sql
-- Tổng orders
SELECT COUNT(*) FROM orders;

-- Orders thành công
SELECT COUNT(*) FROM orders WHERE payment_status = 'completed';

-- Doanh thu theo gói
SELECT plan_type, SUM(amount) FROM orders 
WHERE payment_status = 'completed'
GROUP BY plan_type;

-- Orders chưa thanh toán
SELECT * FROM orders WHERE payment_status = 'pending' 
ORDER BY created_at DESC;

-- Licenses đã kích hoạt
SELECT COUNT(*) FROM licenses WHERE machine_id IS NOT NULL;
```

### Logs

Server tự động log các events:

```python
print(f"✅ Auto-generated license: {license_key} for order: {order_id}")
print(f"VNPay callback error: {e}")
print(f"MoMo callback error: {e}")
```

Redirect logs to file:
```bash
python app.py >> logs/app.log 2>&1
```

---

## 🌐 GitHub Pages Deployment (Frontend Only)

Để host frontend trên GitHub Pages miễn phí:

### 1. Tạo Repo GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/vietnamese-ocr-license.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to repo → Settings → Pages
2. Source: Deploy from branch `main`
3. Folder: `/` (root)
4. Save

→ Site sẽ available tại: `https://yourusername.github.io/vietnamese-ocr-license/`

### 3. Update API URLs

Trong `templates/index.html`, update API endpoint:

```javascript
const response = await fetch('https://your-backend-server.com/api/payment/create', {
    // ...
});
```

**Note:** Backend (Flask API) PHẢI deploy riêng trên VPS/Cloud vì GitHub Pages chỉ host static files!

### Architecture với GitHub Pages

```
GitHub Pages (Frontend)
    ↓ AJAX calls
VPS/Cloud (Backend API + Database)
    ↓ Callbacks
Payment Gateways (VNPay/MoMo/ZaloPay)
```

---

## 🎯 Pricing & Revenue

### Giá đã thiết lập

| Gói | Giá (VNĐ) | Thời hạn | Phí gateway (~3%) |
|-----|-----------|----------|-------------------|
| Monthly | 99,000 | 30 ngày | ~3,000 |
| Yearly | 799,000 | 365 ngày | ~24,000 |
| Lifetime | 1,999,000 | Vĩnh viễn | ~60,000 |

### Revenue Estimation

**Scenario 1: Moderate**
- 50 monthly/month: 50 × 99k = 4.95M/tháng
- 20 yearly/month: 20 × 799k = 15.98M/tháng
- 5 lifetime/month: 5 × 1.999M = 9.995M/tháng
- **Total: ~31M VNĐ/tháng**

**Scenario 2: Aggressive**
- 200 monthly: 19.8M
- 100 yearly: 79.9M
- 30 lifetime: 59.97M
- **Total: ~160M VNĐ/tháng**

### Đổi Giá

Trong `payment_gateway.py`:

```python
PRICING = {
    'monthly': {
        'name': 'Monthly Plan',
        'price': 99000,  # <-- Đổi ở đây
        ...
    },
    ...
}
```

Và trong `templates/index.html`:

```html
<div class="plan-price">99,000₫<span>/tháng</span></div>
```

---

## ❓ Troubleshooting

### Lỗi: "Cannot import payment_gateway"

```bash
# Đảm bảo file payment_gateway.py ở cùng thư mục với app.py
ls license_server/
# Should see: app.py payment_gateway.py
```

### Lỗi: "Callback không được gọi"

**Nguyên nhân:** Payment gateway không thể gọi về localhost

**Giải pháp:**
1. Deploy lên server public
2. Hoặc dùng ngrok: `ngrok http 5000`
3. Update callback URLs với public URL

### Lỗi: "Invalid signature"

**Nguyên nhân:** Secret keys không đúng hoặc data format sai

**Giải pháp:**
1. Check secret keys trong payment_gateway.py
2. Check docs của gateway về signature format
3. Log ra `calculated_signature` vs `received_signature` để debug

### License không được generate

```python
# Check logs trong terminal
# Should see: "✅ Auto-generated license: ..."

# Nếu không thấy, check:
# 1. Callback có được gọi không?
# 2. Payment verification có pass không?
# 3. Database có lỗi không?
```

### Test payment flow

```bash
# 1. Check order được tạo
sqlite3 licenses.db
SELECT * FROM orders ORDER BY created_at DESC LIMIT 5;

# 2. Check license được generate
SELECT * FROM licenses WHERE order_id = 'ORD...';

# 3. Check validation logs
SELECT * FROM validation_logs ORDER BY timestamp DESC LIMIT 10;
```

---

## 📚 Resources

### Documentation

- **VNPay:** https://sandbox.vnpayment.vn/apis/docs/
- **MoMo:** https://developers.momo.vn/
- **ZaloPay:** https://docs.zalopay.vn/

### Testing Tools

- **ngrok:** https://ngrok.com/ (Expose localhost to internet)
- **Postman:** https://www.postman.com/ (API testing)
- **SQLite Browser:** https://sqlitebrowser.org/ (View database)

### Support

- Email: ocrtool.system@gmail.com
- GitHub Issues: your-repo/issues

---

## ✅ Checklist Triển Khai

### Pre-Launch

- [ ] Đăng ký payment gateways (VNPay/MoMo/ZaloPay)
- [ ] Lấy API keys và secrets
- [ ] Update `payment_gateway.py` với keys thật
- [ ] Update callback URLs với domain thật
- [ ] Test sandbox environment
- [ ] Đổi giá nếu cần trong `PRICING`

### Deployment

- [ ] Deploy backend lên VPS/Cloud
- [ ] Setup Nginx reverse proxy
- [ ] Setup SSL certificate (HTTPS required!)
- [ ] Deploy frontend lên GitHub Pages (hoặc cùng server)
- [ ] Update frontend API URLs
- [ ] Test toàn bộ flow end-to-end

### Post-Launch

- [ ] Monitor logs và database
- [ ] Setup email notifications cho admin
- [ ] Backup database định kỳ
- [ ] Monitor payment success rate
- [ ] Customer support ready

---

## 🎉 Kết Luận

Hệ thống đã hoàn chỉnh với:

✅ **Auto payment processing** (VNPay/MoMo/ZaloPay)
✅ **Auto license generation** ngay sau thanh toán
✅ **Machine binding** (1 license = 1 máy)
✅ **Beautiful UI** với payment modal
✅ **Success/Failed pages** đầy đủ
✅ **Database tracking** orders & licenses
✅ **Security** với signature verification
✅ **Ready for production** deployment

**Next Steps:**
1. Đăng ký payment gateways
2. Deploy lên production
3. Test với real payments
4. Launch và kiếm tiền! 💰

---

**Made with ❤️ for Vietnamese OCR Tool**
**© 2025 - All Rights Reserved**

