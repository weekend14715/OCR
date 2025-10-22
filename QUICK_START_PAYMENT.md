# ⚡ Hệ Thống Thanh Toán - Bắt Đầu Nhanh (5 Phút)

## 🎯 Mục Tiêu

Khách hàng thanh toán trực tuyến → Nhận license key ngay lập tức → Kích hoạt app

---

## 🚀 Bước 1: Cài Dependencies (30 giây)

```bash
cd license_server
pip install flask flask-cors requests
```

✅ Done!

---

## 🚀 Bước 2: Cấu Hình Payment Gateway (2 phút)

### Mở file: `license_server/payment_gateway.py`

### Test với Sandbox (cho development):

Giữ nguyên config mặc định - đã có sandbox URLs:

```python
# VNPay Sandbox - Ready to use!
'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'

# MoMo Test - Ready to use!
'endpoint': 'https://test-payment.momo.vn/v2/gateway/api/create'

# ZaloPay Sandbox - Ready to use!
'endpoint': 'https://sb-openapi.zalopay.vn/v2/create'
```

### Production (sau khi launch):

1. Đăng ký:
   - VNPay: https://vnpay.vn/dang-ky-merchant
   - MoMo: https://business.momo.vn
   - ZaloPay: https://zalopay.vn/business

2. Lấy API keys và update vào `payment_gateway.py`

---

## 🚀 Bước 3: Chạy Server (10 giây)

```bash
cd license_server
python app.py
```

Output:
```
============================================================
🚀 Vietnamese OCR Tool - License Server
============================================================
📡 Server running on: http://127.0.0.1:5000
...
```

✅ Server đang chạy!

---

## 🚀 Bước 4: Test Payment Flow (2 phút)

### 1. Mở trình duyệt

```
http://127.0.0.1:5000/
```

### 2. Click "Mua Ngay" (gói Lifetime)

Modal xuất hiện:

### 3. Nhập email

```
test@example.com
```

### 4. Click "💳 VNPay"

Redirect đến VNPay sandbox...

### 5. Thanh toán test

- Card: `9704 0000 0000 0018`
- Name: `NGUYEN VAN A`
- Date: `07/15`
- OTP: `123456`

### 6. Success!

Redirect về `/success` với license key:

```
✅ ABCD-1234-EFGH-5678
```

### 7. Copy key và test trong OCR app

```bash
python ocr_tool_licensed.py
# Nhập key khi được hỏi
```

✅ Done! App activated!

---

## ❓ Callback Không Hoạt Động?

**Normal!** Payment gateways không thể callback về `localhost`.

### Giải pháp: Dùng ngrok

```bash
# Terminal 1: Flask server
cd license_server
python app.py

# Terminal 2: ngrok
ngrok http 5000
```

Output:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:5000
```

### Update callback URL

Trong `payment_gateway.py`, thay:

```python
'vnp_ReturnUrl': 'https://abc123.ngrok.io/api/payment/vnpay/callback'
```

Giờ callback sẽ hoạt động!

---

## 🎯 Production Deployment

### Frontend (GitHub Pages - FREE)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Payment system"
git remote add origin https://github.com/YOUR_USERNAME/ocr-license.git
git push -u origin main

# 2. Enable Pages
# GitHub → Repo → Settings → Pages → Enable

# 3. Update API URLs trong index.html
const BACKEND_URL = 'https://your-backend.com';
```

### Backend (VPS - $5/month)

```bash
# 1. SSH to server
ssh root@your-server-ip

# 2. Clone code
git clone your-repo
cd license_server

# 3. Install & run
pip3 install -r requirements.txt
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 4. Setup Nginx + SSL (see GITHUB_PAGES_DEPLOY.md)
```

---

## 📊 Check Revenue

```bash
# SQLite query
sqlite3 license_server/licenses.db

# Total revenue
SELECT SUM(amount) FROM orders WHERE payment_status = 'completed';

# By plan
SELECT plan_type, COUNT(*), SUM(amount) 
FROM orders 
WHERE payment_status = 'completed'
GROUP BY plan_type;
```

---

## 📞 Hỗ Trợ

**Đọc chi tiết:**
- `PAYMENT_SYSTEM_GUIDE.md` - Complete guide
- `PAYMENT_SYSTEM_SUMMARY.md` - Overview
- `GITHUB_PAGES_DEPLOY.md` - Deployment

**Email:** support@ocrvietnamese.com

---

## ✅ Checklist

- [ ] Installed dependencies
- [ ] Started server (`python app.py`)
- [ ] Tested payment flow locally
- [ ] Registered payment gateways
- [ ] Updated API keys (production)
- [ ] Deployed backend (VPS/Cloud)
- [ ] Deployed frontend (GitHub Pages)
- [ ] Tested end-to-end with real payment

---

**🎉 Ready to launch! Start selling licenses now! 💰**

---

**Made with ❤️ for Vietnamese OCR Tool**

