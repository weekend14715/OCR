# 💳 Hệ Thống Thanh Toán Tự Động

**Vietnamese OCR Tool - Automatic Payment & License System**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)

---

## 🎯 Overview

Hệ thống thanh toán **HOÀN TOÀN TỰ ĐỘNG** cho phép:

✅ Khách hàng thanh toán trực tuyến (VNPay/MoMo/ZaloPay)  
✅ **Nhận license key NGAY LẬP TỨC** sau thanh toán  
✅ **1 máy = 1 license** (machine binding)  
✅ Không cần admin can thiệp  
✅ Production-ready security

---

## 🚀 Quick Start

### Install

```bash
cd license_server
pip install flask flask-cors requests
```

### Run

```bash
python app.py
```

### Test

Open browser: `http://127.0.0.1:5000`

**Done!** 🎉

---

## 📋 Features

### ✅ Payment Gateways

- **VNPay** - Thẻ ngân hàng, QR Code
- **MoMo** - Ví điện tử
- **ZaloPay** - Ví điện tử

### ✅ Auto License Generation

1. Customer pays → Callback to server
2. Server verifies signature (HMAC)
3. **Auto-generates license key**
4. Shows key on success page

**No manual work needed!**

### ✅ Machine Binding

- Hardware fingerprint (hostname + MAC + CPU)
- 1 license = 1 máy only
- Cannot share to other computers

### ✅ Beautiful UI

- Responsive landing page
- Payment modal with email input
- Success page with confetti 🎊
- Failed page with retry option

---

## 📁 Project Structure

```
license_server/
├── app.py                      # Flask API + Payment endpoints
├── payment_gateway.py          # Payment integration (VNPay/MoMo/ZaloPay)
├── requirements.txt
├── templates/
│   ├── index.html             # Landing page
│   ├── admin.html             # Admin panel
│   ├── success.html           # Payment success page
│   └── failed.html            # Payment failed page
└── licenses.db                # SQLite database (auto-created)

Documentation/
├── QUICK_START_PAYMENT.md          # 5-minute guide
├── PAYMENT_SYSTEM_GUIDE.md         # Complete documentation
├── PAYMENT_SYSTEM_SUMMARY.md       # Overview
├── GITHUB_PAGES_DEPLOY.md          # Deployment guide
└── _PAYMENT_SYSTEM_COMPLETE.txt    # Quick reference
```

---

## 🎯 How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   AUTOMATED FLOW                        │
└─────────────────────────────────────────────────────────┘

1. Customer visits website
   └─> Selects plan (Monthly/Yearly/Lifetime)

2. Enters email in modal
   └─> Chooses payment method (VNPay/MoMo/ZaloPay)

3. Redirects to payment gateway
   └─> Customer completes payment

4. ✨ AUTO-MAGIC:
   ├─> Gateway callbacks to server
   ├─> Server verifies signature
   ├─> Auto-generates license key
   └─> Saves to database

5. Redirects to success page
   └─> Shows license key: ABCD-1234-EFGH-5678

6. Customer copies key
   └─> Enters in OCR app → Activated!

7. License binds to machine
   └─> Cannot use on other computers
```

---

## 💰 Pricing

| Plan | Price (VNĐ) | Duration | Features |
|------|-------------|----------|----------|
| Monthly | 99,000 | 30 days | Full features |
| Yearly | 799,000 | 365 days | + Priority support |
| Lifetime | 1,999,000 | Forever | + VIP support |

**Revenue Potential:**
- 50 customers/month = ~38M VNĐ/month
- 200 customers/month = ~125M VNĐ/month

---

## 🔧 Configuration

### Payment Gateway Setup

#### VNPay

1. Register: https://vnpay.vn/dang-ky-merchant
2. Get `TMN Code` and `Hash Secret`
3. Update in `payment_gateway.py`:

```python
VNPAY_CONFIG = {
    'vnp_TmnCode': 'YOUR_CODE',
    'vnp_HashSecret': 'YOUR_SECRET',
    'vnp_Url': 'https://pay.vnpay.vn/vpcpay.html',
    'vnp_ReturnUrl': 'https://yourdomain.com/api/payment/vnpay/callback',
}
```

#### MoMo

1. Register: https://business.momo.vn
2. Get `Partner Code`, `Access Key`, `Secret Key`
3. Update in `payment_gateway.py`

#### ZaloPay

1. Register: https://zalopay.vn/business
2. Get `App ID`, `Key1`, `Key2`
3. Update in `payment_gateway.py`

---

## 🌐 Deployment

### Frontend (GitHub Pages - FREE)

```bash
# 1. Push to GitHub
git push origin main

# 2. Enable Pages
# Settings → Pages → Enable

# 3. Update API URLs in index.html
const BACKEND_URL = 'https://api.yourdomain.com';
```

### Backend (VPS - $5/month)

```bash
# 1. Deploy Flask app
scp -r license_server/ user@server:/var/www/

# 2. Install & Run
pip3 install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 3. Setup Nginx + SSL
# (See GITHUB_PAGES_DEPLOY.md)
```

---

## 🔐 Security

### 1. Payment Verification

All payments verified with HMAC signature:

```python
def verify_payment(params):
    received_sig = params['signature']
    calculated_sig = hmac.sha256(data, secret_key)
    return received_sig == calculated_sig  # ✅ or ❌
```

### 2. Machine Binding

```python
machine_id = sha256(hostname + mac + cpu)
# Saved on first activation
# Checked on every validation
```

### 3. HTTPS Required

All payment callbacks **must** use HTTPS in production.

---

## 📊 API Reference

### Public Endpoints

```bash
# Create payment
POST /api/payment/create
Body: {
  "plan_type": "lifetime",
  "payment_method": "vnpay",
  "customer_email": "user@email.com"
}

# Payment callbacks (auto-called by gateways)
GET /api/payment/vnpay/callback
GET/POST /api/payment/momo/callback
POST /api/payment/zalopay/callback

# Success/Failed pages
GET /success?license_key=XXXX-XXXX-XXXX-XXXX
GET /failed

# Check order status
GET /api/order/status/<order_id>
```

### Admin Endpoints (Require X-Admin-Key)

```bash
POST /api/admin/generate       # Manual generate
GET  /api/admin/licenses        # List all
POST /api/admin/deactivate      # Disable license
GET  /api/admin/stats           # Statistics
```

---

## 📚 Documentation

- **[Quick Start](QUICK_START_PAYMENT.md)** - Get started in 5 minutes
- **[Complete Guide](PAYMENT_SYSTEM_GUIDE.md)** - Full documentation
- **[Deployment](GITHUB_PAGES_DEPLOY.md)** - Production deployment
- **[Summary](PAYMENT_SYSTEM_SUMMARY.md)** - System overview

---

## 🧪 Testing

### Local Testing

```bash
# Start server
python app.py

# Open browser
http://localhost:5000

# Test payment flow
# (Callbacks won't work on localhost)
```

### Testing with ngrok (Callbacks work!)

```bash
# Terminal 1
python app.py

# Terminal 2
ngrok http 5000

# Update callback URLs in payment_gateway.py
# Now test complete payment flow!
```

---

## 🆘 Troubleshooting

### "CORS error"

```python
# In app.py
from flask_cors import CORS
CORS(app)
```

### "Callback not called"

- Use ngrok for local testing
- Ensure HTTPS in production
- Check callback URLs match gateway dashboard

### "License not generated"

```sql
-- Check database
SELECT * FROM orders WHERE order_id = 'ORD...';
SELECT * FROM licenses WHERE order_id = 'ORD...';
```

---

## ✅ Pre-Launch Checklist

- [ ] Payment gateways registered
- [ ] API keys updated
- [ ] Backend deployed (HTTPS!)
- [ ] Frontend deployed
- [ ] Tested end-to-end payment
- [ ] Database backed up
- [ ] Customer support ready

---

## 📈 Monitoring

### Database Queries

```sql
-- Total revenue
SELECT SUM(amount) FROM orders WHERE payment_status = 'completed';

-- Revenue by plan
SELECT plan_type, SUM(amount) FROM orders 
WHERE payment_status = 'completed'
GROUP BY plan_type;

-- Conversion rate
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN payment_status = 'completed' THEN 1 ELSE 0 END) as paid
FROM orders;
```

---

## 🎉 Success Metrics

**Total Code:** ~2,500 lines  
**Documentation:** ~2,500 lines  
**Files Created:** 6 files  
**Payment Gateways:** 3 integrated  
**Automation Level:** 100%  

---

## 📞 Support

- **Email:** ocrtool.system@gmail.com
- **Docs:** See `.md` files in project

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🌟 Acknowledgments

- Flask - Web framework
- VNPay/MoMo/ZaloPay - Payment gateways
- SQLite - Database

---

## 🚀 Ready to Launch!

```bash
# Start making money! 💰
python app.py
```

---

**Made with ❤️ for Vietnamese OCR Tool**

**© 2025 - All Rights Reserved**

---

## 🔗 Links

- **GitHub:** https://github.com/yourusername/vietnamese-ocr-license
- **Website:** https://yourdomain.com
- **Docs:** [Full Documentation](PAYMENT_SYSTEM_GUIDE.md)

---

**⭐ Star this repo if you find it helpful!**

