# 🔐 Vietnamese OCR Tool - License System

Hệ thống quản lý license hoàn chỉnh cho Vietnamese OCR Tool với backend API, frontend web, và tích hợp vào ứng dụng.

---

## 📁 Cấu trúc thư mục

```
OCR/
├── license_server/          # Backend license server
│   ├── app.py              # Flask API server
│   ├── templates/          
│   │   ├── index.html      # Landing page bán license
│   │   └── admin.html      # Admin panel quản lý
│   ├── requirements.txt    # Python dependencies
│   └── licenses.db         # SQLite database (auto-created)
│
├── license_client.py       # Module license client
├── ocr_tool_licensed.py    # OCR app có tích hợp license
└── ocr_tool.py            # OCR app gốc (không có license)
```

---

## 🚀 Cài đặt & Chạy License Server

### Bước 1: Cài đặt dependencies

```bash
cd license_server
pip install -r requirements.txt
```

### Bước 2: Chạy server

```bash
python app.py
```

Server sẽ chạy tại: `http://127.0.0.1:5000`

### Bước 3: Đổi Admin API Key (QUAN TRỌNG!)

Mở `license_server/app.py` và đổi dòng:

```python
ADMIN_API_KEY = 'your-secure-admin-api-key-here-change-this'
```

Thành một key bảo mật của bạn (ví dụ: `my-super-secret-admin-key-2025`)

---

## 🌐 Sử dụng Frontend Web

### Landing Page (Bán License)
- **URL**: `http://127.0.0.1:5000/`
- Hiển thị 3 gói: Monthly, Yearly, Lifetime
- Khách hàng xem giá và liên hệ mua

### Admin Panel (Quản lý License)
- **URL**: `http://127.0.0.1:5000/admin.html` (cần tạo route hoặc mở trực tiếp file)
- Tạo license keys
- Xem danh sách licenses
- Vô hiệu hóa licenses
- Thống kê

#### Cách sử dụng Admin Panel:

1. Mở `http://127.0.0.1:5000/static/admin.html` (hoặc mở file HTML trực tiếp)
2. Nhập **Admin API Key** vào ô input
3. Click "Làm mới danh sách" để tải licenses
4. Tạo license mới bằng form "Tạo License Mới"

---

## 🔑 API Endpoints

### PUBLIC ENDPOINTS

#### 1. Validate License (Xác thực license)
```http
POST /api/validate
Content-Type: application/json

{
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "machine_id": "unique-machine-id"
}
```

**Response Success:**
```json
{
  "valid": true,
  "plan": "lifetime",
  "activated": "2025-01-01T10:00:00",
  "expires": null,
  "message": "License is valid"
}
```

**Response Error:**
```json
{
  "valid": false,
  "error": "Invalid license key"
}
```

### ADMIN ENDPOINTS (Yêu cầu header `X-Admin-Key`)

#### 2. Generate License Keys
```http
POST /api/admin/generate
Content-Type: application/json
X-Admin-Key: your-admin-key

{
  "plan_type": "lifetime",
  "quantity": 5,
  "email": "customer@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "licenses": [
    "A1B2-C3D4-E5F6-7890",
    "1234-5678-90AB-CDEF"
  ],
  "plan": "lifetime",
  "quantity": 2
}
```

#### 3. List All Licenses
```http
GET /api/admin/licenses
X-Admin-Key: your-admin-key
```

#### 4. Deactivate License
```http
POST /api/admin/deactivate
Content-Type: application/json
X-Admin-Key: your-admin-key

{
  "license_key": "XXXX-XXXX-XXXX-XXXX"
}
```

#### 5. Get Statistics
```http
GET /api/admin/stats
X-Admin-Key: your-admin-key
```

**Response:**
```json
{
  "total_licenses": 100,
  "activated": 75,
  "active": 70,
  "by_plan": {
    "lifetime": 30,
    "yearly": 40,
    "monthly": 30
  }
}
```

---

## 💻 Sử dụng trong App OCR

### Test License Client (Standalone)

```bash
python license_client.py
```

Sẽ hiển thị:
- Machine ID của máy bạn
- Trạng thái license hiện tại
- Yêu cầu nhập license key nếu chưa có

### Chạy OCR App với License

```bash
python ocr_tool_licensed.py
```

**Tính năng:**
- Kiểm tra license khi khởi động
- Yêu cầu nhập license key nếu chưa có
- Hiển thị dialog GUI để kích hoạt
- Menu "License Info" trong system tray
- Menu "Deactivate License" để xóa license khỏi máy

---

## 🎯 Quy trình bán License

### Với Khách hàng:

1. **Khách truy cập website** (`http://yourserver.com/`)
2. **Chọn gói** (Monthly/Yearly/Lifetime)
3. **Thanh toán** qua:
   - Chuyển khoản ngân hàng
   - Momo/ZaloPay
   - PayPal (nếu có)
4. **Nhận email** chứa license key

### Admin workflow:

1. **Nhận thông báo** thanh toán thành công
2. **Vào Admin Panel** (`http://127.0.0.1:5000/admin.html`)
3. **Tạo license key**:
   - Chọn plan type (lifetime/yearly/monthly)
   - Nhập email khách hàng
   - Click "Tạo License"
4. **Copy license key** và gửi cho khách
5. **Khách kích hoạt** trong app OCR

---

## 🔒 Bảo mật

### Machine Binding
- Mỗi license chỉ có thể kích hoạt trên **1 máy**
- Sử dụng hardware fingerprint:
  - Hostname
  - MAC address
  - Processor info
- Hash SHA256 để bảo mật

### API Security
- Admin endpoints yêu cầu **API Key**
- License keys được validate trên server
- Machine ID được hash trước khi lưu

### License Storage
- License key lưu tại: `%LOCALAPPDATA%\VietnameseOCRTool\license.dat`
- Không lưu plain text, có thể mã hóa thêm

---

## 📊 Database Schema

### Table: `licenses`
```sql
CREATE TABLE licenses (
    id INTEGER PRIMARY KEY,
    license_key TEXT UNIQUE NOT NULL,
    email TEXT,
    machine_id TEXT,                 -- Hashed machine ID
    activation_date TEXT,
    expiry_date TEXT,                -- NULL for lifetime
    plan_type TEXT NOT NULL,         -- lifetime/yearly/monthly
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    last_validated TEXT
);
```

### Table: `validation_logs`
```sql
CREATE TABLE validation_logs (
    id INTEGER PRIMARY KEY,
    license_key TEXT NOT NULL,
    machine_id TEXT,
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL,        -- 0 or 1
    ip_address TEXT
);
```

---

## 🌍 Deploy lên Production

### Option 1: VPS/Cloud Server

1. **Setup server** (Ubuntu/CentOS)
2. **Install Python & dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   cd /var/www/license_server
   pip3 install -r requirements.txt
   ```

3. **Chạy với Gunicorn**:
   ```bash
   pip3 install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Setup Nginx reverse proxy**:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Setup SSL** với Let's Encrypt:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

### Option 2: Heroku

```bash
# Tạo Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-license-server
git push heroku main
```

### Option 3: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 🎨 Tùy chỉnh Frontend

### Đổi giá và thông tin

Mở `license_server/templates/index.html` và sửa:

```html
<!-- Giá gói -->
<div class="plan-price">99,000₫</div>

<!-- Email liên hệ -->
<p>Email: <a href="mailto:support@ocrvietnamese.com">support@ocrvietnamese.com</a></p>
```

### Đổi màu sắc

Tìm CSS gradient trong `<style>`:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Thêm payment gateway

Tích hợp với:
- **Momo**: [Momo API Docs](https://developers.momo.vn/)
- **ZaloPay**: [ZaloPay Docs](https://docs.zalopay.vn/)
- **PayPal**: [PayPal Checkout](https://developer.paypal.com/)

---

## 🧪 Testing

### Test API với cURL

```bash
# Test validate (license chưa tồn tại)
curl -X POST http://127.0.0.1:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"license_key":"TEST-1234-5678-90AB","machine_id":"test-machine"}'

# Generate license (cần admin key)
curl -X POST http://127.0.0.1:5000/api/admin/generate \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: your-secure-admin-api-key-here-change-this" \
  -d '{"plan_type":"lifetime","quantity":1,"email":"test@example.com"}'
```

### Test với Python

```python
import requests

# Generate license
response = requests.post(
    'http://127.0.0.1:5000/api/admin/generate',
    headers={'X-Admin-Key': 'your-admin-key'},
    json={'plan_type': 'lifetime', 'quantity': 1}
)
print(response.json())

# Validate license
license_key = response.json()['licenses'][0]
response = requests.post(
    'http://127.0.0.1:5000/api/validate',
    json={'license_key': license_key, 'machine_id': 'test-machine'}
)
print(response.json())
```

---

## ❓ FAQ

### Q: License có thể chuyển sang máy khác không?
**A**: Có, sử dụng menu "Deactivate License" trên máy cũ, sau đó kích hoạt trên máy mới.

### Q: Làm sao reset license nếu khách mất máy?
**A**: Admin vào panel, tìm license key, click "Vô hiệu hóa", sau đó tạo license mới cho khách.

### Q: Database lưu ở đâu?
**A**: File `licenses.db` trong folder `license_server/`. Backup file này định kỳ!

### Q: Có thể tạo license offline không?
**A**: Không, app cần internet để validate license lần đầu. Sau đó có thể dùng offline.

### Q: License có hết hạn không?
**A**: Tùy gói:
- **Lifetime**: Không hết hạn
- **Yearly**: 365 ngày
- **Monthly**: 30 ngày

---

## 📞 Support

- **Email**: support@ocrvietnamese.com
- **Phone**: 0123 456 789
- **GitHub**: [Your Repo]

---

## 📝 License

© 2025 Vietnamese OCR Tool. All rights reserved.

Made with ❤️ in Vietnam 🇻🇳

