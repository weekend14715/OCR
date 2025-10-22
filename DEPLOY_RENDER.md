# 🚀 Deploy License Server lên Render.com

Hướng dẫn chi tiết để deploy OCR License Server từ GitHub lên Render.com

---

## 📋 MỤC LỤC

1. [Chuẩn bị](#1-chuẩn-bị)
2. [Push code lên GitHub](#2-push-code-lên-github)
3. [Tạo Web Service trên Render](#3-tạo-web-service-trên-render)
4. [Cấu hình Environment Variables](#4-cấu-hình-environment-variables)
5. [Deploy & Kiểm tra](#5-deploy--kiểm-tra)
6. [Sử dụng Custom Domain](#6-sử-dụng-custom-domain-optional)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. CHUẨN BỊ

### ✅ Checklist trước khi deploy:

- [ ] Có tài khoản GitHub (đã có ✅)
- [ ] Có tài khoản Render.com (Free tier cũng OK)
- [ ] Repository GitHub đã tạo (weekend14715/OCR ✅)
- [ ] Code đã push lên GitHub
- [ ] Đã có 2 Gmail accounts với App Passwords

### 📦 Files cần thiết (đã tạo):

```
✅ license_server/render.yaml       - Cấu hình Render
✅ license_server/start.sh          - Start script
✅ license_server/requirements.txt  - Dependencies (có gunicorn)
✅ license_server/app_config.py     - Config loader
✅ .gitignore                       - Bảo vệ sensitive files
```

---

## 2. PUSH CODE LÊN GITHUB

### Bước 1: Kiểm tra files

```bash
# Xem trạng thái
git status

# Nên thấy các files mới:
# - license_server/render.yaml
# - license_server/start.sh
# - license_server/app_config.py
# - .gitignore
```

### Bước 2: Commit & Push

```bash
# Add tất cả files mới
git add .

# Commit
git commit -m "Add Render.com deployment config"

# Push lên GitHub
git push origin main
```

⚠️ **QUAN TRỌNG:** Đảm bảo `.gitignore` đã ignore:
- `license_server/email_config.py` (chứa App Password!)
- `license_server/*.db` (database local)

### Bước 3: Verify trên GitHub

1. Vào https://github.com/weekend14715/OCR
2. Check thấy các files mới
3. **Đảm bảo KHÔNG thấy** `email_config.py` (đã bị ignore)

---

## 3. TẠO WEB SERVICE TRÊN RENDER

### Bước 1: Đăng nhập Render.com

1. Vào https://render.com
2. Sign up hoặc Login
3. Nếu lần đầu, có thể dùng GitHub để login

### Bước 2: Connect GitHub

1. Trên Render Dashboard, click **"New +"**
2. Chọn **"Web Service"**
3. Click **"Connect account"** để connect GitHub
4. Authorize Render to access your GitHub

### Bước 3: Chọn Repository

1. Tìm repository **"weekend14715/OCR"**
2. Click **"Connect"**

### Bước 4: Configure Service

#### Basic Settings:

```yaml
Name: ocr-license-server
Region: Oregon (US-West)  # Hoặc Singapore nếu có
Branch: main
Root Directory: license_server  # ⚠️ QUAN TRỌNG!
```

#### Build Settings:

```yaml
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: bash start.sh
```

#### Instance Type:

```
Free (512MB RAM, 0.1 CPU) - OK cho development
Starter ($7/month) - Tốt hơn cho production
```

#### Auto-Deploy:

```
☑️ Auto-Deploy: Yes
   → Tự động deploy khi push lên GitHub
```

---

## 4. CẤU HÌNH ENVIRONMENT VARIABLES

### Bước 1: Vào Environment Tab

Sau khi tạo service, vào tab **"Environment"**

### Bước 2: Add Environment Variables

Click **"Add Environment Variable"** và thêm:

#### 🔐 Admin API Key:

```
Key: ADMIN_API_KEY
Value: <generate-strong-password>  # Dùng password generator
```

Example: `ocr_admin_2024_x9k2m5p8q3`

#### 📧 Email Configuration:

**Account 1:**
```
Key: EMAIL_ACCOUNT_1
Value: ocrtool.license@gmail.com

Key: EMAIL_PASSWORD_1
Value: gjxhqhqrflvjzurg  # Bỏ dấu cách!

Key: EMAIL_LIMIT_1
Value: 500
```

**Account 2:**
```
Key: EMAIL_ACCOUNT_2
Value: ocrtool.system@gmail.com

Key: EMAIL_PASSWORD_2
Value: xjoqoaedkwzjfvxj  # Bỏ dấu cách!

Key: EMAIL_LIMIT_2
Value: 500
```

**Email Settings:**
```
Key: EMAIL_FROM_NAME
Value: OCR Tool License

Key: EMAIL_SUPPORT
Value: hoangtuan.th484@gmail.com
```

#### 💳 Payment Gateway (Optional - add sau nếu cần):

**VNPay:**
```
Key: VNPAY_TMN_CODE
Value: <your-vnpay-code>

Key: VNPAY_HASH_SECRET
Value: <your-vnpay-secret>
```

**MoMo:**
```
Key: MOMO_PARTNER_CODE
Value: <your-momo-code>

Key: MOMO_ACCESS_KEY
Value: <your-momo-access-key>

Key: MOMO_SECRET_KEY
Value: <your-momo-secret>
```

**ZaloPay:**
```
Key: ZALOPAY_APP_ID
Value: <your-zalopay-id>

Key: ZALOPAY_KEY1
Value: <your-zalopay-key1>

Key: ZALOPAY_KEY2
Value: <your-zalopay-key2>
```

### Bước 3: Save

Click **"Save Changes"** → Render sẽ tự động redeploy

---

## 5. DEPLOY & KIỂM TRA

### Bước 1: Deploy

Sau khi save environment variables:
- Render sẽ tự động build và deploy
- Xem logs trong tab **"Logs"**
- Chờ khoảng 2-5 phút

### Bước 2: Check Status

```
Logs sẽ hiện:
✅ ==> Building...
✅ ==> Installing dependencies...
✅ ==> Starting service...
✅ 🚀 Starting OCR License Server...
✅ 📦 Initializing database...
✅ 🌐 Starting Gunicorn server...
✅ Your service is live 🎉
```

### Bước 3: Get URL

URL của bạn sẽ có dạng:
```
https://ocr-license-server.onrender.com
```

### Bước 4: Test API

#### Test 1: Health Check

```bash
curl https://ocr-license-server.onrender.com/api/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "License Server is running",
  "timestamp": "2024-10-22T10:43:00Z"
}
```

#### Test 2: Get Plans

```bash
curl https://ocr-license-server.onrender.com/api/plans
```

Expected response:
```json
{
  "plans": [
    {
      "id": "lifetime",
      "name": "Lifetime License",
      "price": 299000,
      ...
    }
  ]
}
```

#### Test 3: Access Web Interface

Mở browser:
```
https://ocr-license-server.onrender.com/
```

Sẽ thấy trang mua license!

---

## 6. SỬ DỤNG CUSTOM DOMAIN (Optional)

### Bước 1: Mua Domain

Mua domain từ:
- Namecheap
- GoDaddy
- Google Domains
- ...

Example: `ocrtool.com`

### Bước 2: Add Custom Domain trên Render

1. Vào tab **"Settings"**
2. Scroll đến **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Nhập domain: `api.ocrtool.com`

### Bước 3: Configure DNS

Render sẽ cho bạn CNAME record:

```
Type: CNAME
Name: api (hoặc @)
Value: ocr-license-server.onrender.com
TTL: 3600
```

Add vào DNS provider của bạn (Namecheap/GoDaddy...)

### Bước 4: Verify

- Chờ 5-30 phút DNS propagate
- Render sẽ tự động provision SSL certificate
- Test: `https://api.ocrtool.com/api/health`

---

## 7. TROUBLESHOOTING

### ❌ Lỗi: Build Failed

**Nguyên nhân:** Dependencies không install được

**Giải pháp:**
```bash
# Check requirements.txt
cat license_server/requirements.txt

# Phải có:
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
gunicorn==21.2.0
```

### ❌ Lỗi: Start Command Failed

**Nguyên nhân:** `start.sh` không có quyền execute hoặc sai path

**Giải pháp:**

1. Check Root Directory = `license_server`
2. Start Command = `bash start.sh`
3. Verify `start.sh` có trong `license_server/`

### ❌ Lỗi: Database Error

**Nguyên nhân:** Không có persistent disk

**Giải pháp:**

1. Vào tab **"Environment"**
2. Scroll đến **"Disk"**
3. Click **"Add Disk"**:
   ```
   Name: license-db
   Mount Path: /opt/render/project/src
   Size: 1 GB
   ```

### ❌ Lỗi: Email không gửi được

**Nguyên nhân:** Environment variables chưa set hoặc sai

**Giải pháp:**

1. Check environment variables:
   - `EMAIL_ACCOUNT_1`
   - `EMAIL_PASSWORD_1`
   - Đảm bảo App Password **KHÔNG CÓ DẤU CÁCH**

2. Test trong logs:
   ```bash
   # Xem logs
   # Tìm dòng: "✅ Email configuration loaded"
   ```

### ❌ Lỗi: 403 Forbidden

**Nguyên nhân:** Admin API key sai

**Giải pháp:**

Check environment variable `ADMIN_API_KEY` và dùng đúng key khi call API

### ❌ Lỗi: Service Keeps Restarting

**Nguyên nhân:** 
- Out of memory (Free tier: 512MB)
- Crash trong code

**Giải pháp:**

1. Check logs để xem error
2. Upgrade lên Starter plan nếu cần
3. Optimize code

---

## 8. UPDATE CODE SAU KHI DEPLOY

### Khi có thay đổi code:

```bash
# 1. Edit code local
# 2. Test local
python license_server/app.py

# 3. Commit & push
git add .
git commit -m "Update features"
git push origin main

# 4. Render sẽ TỰ ĐỘNG deploy! 🎉
```

### Xem deploy progress:

1. Vào Render dashboard
2. Click vào service
3. Tab **"Events"** → thấy "Deploy started"
4. Tab **"Logs"** → xem live logs

---

## 9. MONITORING & MAINTENANCE

### Check Logs:

```
Render Dashboard → Service → Logs tab
```

### Check Metrics:

```
Render Dashboard → Service → Metrics tab
```

Xem:
- CPU usage
- Memory usage
- Request rate
- Response time

### Database Backup:

Free tier: Render không auto backup

**Manual backup:**
```bash
# Download database qua API
curl https://ocr-license-server.onrender.com/admin/backup \
  -H "X-API-Key: your-admin-key" \
  -o backup.db
```

**Hoặc viết script backup định kỳ**

---

## 10. COSTS

### Free Tier:

```
✅ 750 hours/month (đủ cho 1 service 24/7)
✅ 512 MB RAM
✅ 0.1 CPU
✅ 100 GB bandwidth/month
✅ Auto-sleep sau 15 phút không dùng
⚠️  Cold start ~30s khi wake up
```

### Starter Plan ($7/month):

```
✅ Always-on (không sleep)
✅ 512 MB RAM
✅ 0.5 CPU
✅ 100 GB bandwidth
✅ No cold starts
```

---

## 11. SECURITY CHECKLIST

```
✅ .gitignore đã ignore email_config.py
✅ Environment variables dùng cho secrets
✅ ADMIN_API_KEY đủ mạnh
✅ Database không public
✅ HTTPS enabled (tự động bởi Render)
✅ CORS configured đúng
```

---

## 🎯 QUICK START COMMANDS

```bash
# 1. Push lên GitHub
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Tạo service trên Render.com
# → Follow steps trên

# 3. Set environment variables
# → Follow section 4

# 4. Test
curl https://your-service.onrender.com/api/health

# 5. Done! 🎉
```

---

## 📚 TÀI LIỆU THAM KHẢO

- [Render Docs](https://render.com/docs)
- [Flask Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Gunicorn Docs](https://docs.gunicorn.org/)

---

## 🆘 CẦN HỖ TRỢ?

**Email:** hoangtuan.th484@gmail.com

**GitHub Issues:** https://github.com/weekend14715/OCR/issues

---

## ✅ CHECKLIST HOÀN THÀNH

```
[ ] Push code lên GitHub
[ ] Tạo Render.com account
[ ] Connect GitHub với Render
[ ] Tạo Web Service
[ ] Set environment variables
[ ] Deploy thành công
[ ] Test API endpoints
[ ] Test web interface
[ ] Test email sending
[ ] (Optional) Setup custom domain
```

---

**🎉 Chúc deploy thành công!**

