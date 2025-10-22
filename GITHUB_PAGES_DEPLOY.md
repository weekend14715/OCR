# 🚀 Deploy Frontend lên GitHub Pages

## 📋 Tổng Quan

GitHub Pages cho phép host **frontend miễn phí**. Backend API sẽ deploy riêng trên VPS/Cloud.

```
Architecture:
┌─────────────────────────┐
│   GitHub Pages          │ → Frontend (HTML/CSS/JS)
│   (Free Hosting)        │ → Landing page, payment UI
└──────────┬──────────────┘
           │ AJAX calls
           ↓
┌─────────────────────────┐
│   VPS / Cloud Server    │ → Backend API (Flask)
│   (Paid Hosting)        │ → Database, license logic
└──────────┬──────────────┘
           │ Callbacks
           ↓
┌─────────────────────────┐
│   Payment Gateways      │ → VNPay, MoMo, ZaloPay
└─────────────────────────┘
```

---

## 🎯 Bước 1: Tạo GitHub Repository

### Option A: Tạo Repo Mới

```bash
# 1. Init git (nếu chưa có)
cd F:\OCR\OCR
git init

# 2. Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
*.db
*.log
venv/
.env
dist/
build/
.DS_Store
EOF

# 3. Add files
git add .
git commit -m "Initial commit: License System + Payment"

# 4. Create repo on GitHub
# Go to: https://github.com/new
# Name: vietnamese-ocr-license
# Public/Private: Your choice

# 5. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/vietnamese-ocr-license.git
git branch -M main
git push -u origin main
```

### Option B: Sử Dụng Repo Hiện Có

```bash
# Nếu đã có repo, chỉ cần push
git add license_server/
git commit -m "Add payment system"
git push
```

---

## 🎯 Bước 2: Enable GitHub Pages

### Via GitHub Website

1. Go to your repo: `https://github.com/YOUR_USERNAME/vietnamese-ocr-license`
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**:
   - Branch: `main`
   - Folder: `/` (root) hoặc `/docs` nếu bạn move files vào đó
5. Click **Save**
6. Wait 1-2 minutes
7. Page will be live at: `https://YOUR_USERNAME.github.io/vietnamese-ocr-license/`

### Via GitHub CLI (Optional)

```bash
gh repo create vietnamese-ocr-license --public
gh repo edit --enable-pages --pages-branch main --pages-path /
```

---

## 🎯 Bước 3: Tạo Static Frontend

GitHub Pages chỉ host **static files** (HTML/CSS/JS). Flask templates cần convert.

### Create `docs/` folder (Optional structure)

```bash
mkdir docs
```

### Copy index.html

**Option 1: Manual Copy**
```bash
cp license_server/templates/index.html docs/index.html
cp license_server/templates/success.html docs/success.html
cp license_server/templates/failed.html docs/failed.html
```

**Option 2: Deploy từ root**
- Giữ nguyên structure
- GitHub Pages sẽ serve từ root directory

---

## 🎯 Bước 4: Update API Endpoints

Trong `index.html`, update API call để trỏ đến backend server:

### Before (Local)
```javascript
const response = await fetch('/api/payment/create', {
    // ...
});
```

### After (Production)
```javascript
const BACKEND_URL = 'https://your-backend-server.com';  // ← Change this!

const response = await fetch(`${BACKEND_URL}/api/payment/create`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        plan_type: selectedPlan,
        payment_method: paymentMethod,
        customer_email: email
    })
});
```

### Complete Update

Search và replace tất cả `/api/` calls:

```javascript
// At the top of <script> tag
const BACKEND_URL = 'https://api.yourdomain.com';  // Backend API URL

// Update fetch call
async function processPayment(paymentMethod) {
    const email = document.getElementById('customerEmail').value;
    
    if (!email || !email.includes('@')) {
        alert('Email không hợp lệ!');
        return;
    }
    
    // Disable buttons
    const buttons = document.querySelectorAll('.payment-methods button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.6';
    });
    
    try {
        // Updated URL with BACKEND_URL
        const response = await fetch(`${BACKEND_URL}/api/payment/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plan_type: selectedPlan,
                payment_method: paymentMethod,
                customer_email: email
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.payment_url) {
            window.location.href = data.payment_url;
        } else {
            alert('Lỗi: ' + (data.error || 'Không thể tạo thanh toán'));
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
            });
        }
    } catch (error) {
        alert('Lỗi kết nối: ' + error.message);
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.style.opacity = '1';
        });
    }
}
```

---

## 🎯 Bước 5: Enable CORS on Backend

Backend phải cho phép requests từ GitHub Pages domain.

### Update `app.py`

```python
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from GitHub Pages
CORS(app, origins=[
    'http://localhost:5000',  # Local testing
    'https://YOUR_USERNAME.github.io',  # GitHub Pages
    'https://yourdomain.com',  # Custom domain (if any)
])
```

Or allow all origins (less secure):
```python
CORS(app)  # Allow all origins
```

---

## 🎯 Bước 6: Deploy Backend API

Backend MUST be deployed separately. GitHub Pages chỉ host static files!

### Recommended Options

#### Option 1: DigitalOcean Droplet ($5/month)

```bash
# 1. Create droplet (Ubuntu)
# 2. SSH to server
ssh root@your-server-ip

# 3. Install Python & dependencies
apt update
apt install python3-pip nginx certbot python3-certbot-nginx
pip3 install flask flask-cors gunicorn

# 4. Upload code
scp -r license_server/ root@your-server-ip:/var/www/

# 5. Run with Gunicorn
cd /var/www/license_server
gunicorn -w 4 -b 127.0.0.1:5000 app:app

# 6. Setup Nginx (see below)
```

#### Option 2: PythonAnywhere (Easier, ~$5/month)

1. Create account: https://www.pythonanywhere.com/
2. Upload code via web interface
3. Create Web App → Flask
4. Set WSGI file:
   ```python
   import sys
   sys.path.insert(0, '/home/yourusername/license_server')
   from app import app as application
   ```
5. Reload app
6. API at: `https://yourusername.pythonanywhere.com`

#### Option 3: Heroku (Free tier limited)

```bash
# 1. Create Procfile
echo "web: gunicorn app:app" > Procfile

# 2. Create requirements.txt
pip freeze > requirements.txt

# 3. Deploy
heroku login
heroku create your-app-name
git push heroku main

# API at: https://your-app-name.herokuapp.com
```

#### Option 4: Railway.app (Modern, $5/month)

1. Connect GitHub repo
2. Railway auto-detects Flask
3. Deploy with one click
4. API at: `https://your-app.railway.app`

---

## 🎯 Bước 7: Setup Custom Domain (Optional)

### For GitHub Pages (Frontend)

1. Buy domain (e.g., `ocrvietnamese.com`)
2. In domain registrar, add DNS records:
   ```
   Type: A
   Name: @
   Value: 185.199.108.153
   
   Type: A
   Name: @
   Value: 185.199.109.153
   
   Type: A
   Name: @
   Value: 185.199.110.153
   
   Type: A
   Name: @
   Value: 185.199.111.153
   
   Type: CNAME
   Name: www
   Value: YOUR_USERNAME.github.io
   ```
3. In GitHub repo Settings → Pages:
   - Custom domain: `ocrvietnamese.com`
   - Enforce HTTPS: ✓
4. Wait for DNS propagation (24-48h)

### For Backend API

Point subdomain to backend server:
```
Type: A
Name: api
Value: YOUR_SERVER_IP
```

Then access via: `https://api.ocrvietnamese.com`

---

## 🎯 Bước 8: Setup Nginx (Backend Server)

### Nginx Config

```nginx
# /etc/nginx/sites-available/license-api

server {
    listen 80;
    server_name api.yourdomain.com;  # Or use IP
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/license-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Setup SSL (HTTPS Required!)

```bash
sudo certbot --nginx -d api.yourdomain.com
```

Certbot sẽ tự động update Nginx config và enable HTTPS.

---

## 🎯 Bước 9: Test Complete Flow

### 1. Test Frontend

Visit: `https://YOUR_USERNAME.github.io/vietnamese-ocr-license/`

Should see:
- ✅ Landing page loads
- ✅ Pricing cards visible
- ✅ Click "Mua Ngay" shows modal

### 2. Test Backend API

```bash
# Test health check
curl https://api.yourdomain.com/

# Test payment creation
curl -X POST https://api.yourdomain.com/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "lifetime",
    "payment_method": "vnpay",
    "customer_email": "test@example.com"
  }'
```

Should return payment URL.

### 3. Test Complete Purchase Flow

1. Open frontend in browser
2. Click "Mua Ngay" on any plan
3. Enter email
4. Select payment method
5. Should redirect to VNPay/MoMo/ZaloPay
6. Complete test payment
7. Should redirect back to success page with license key
8. Copy key and test in OCR app

---

## 🎯 Bước 10: Monitoring & Maintenance

### Setup Process Manager (Backend)

Use PM2 or systemd to keep app running:

#### With PM2
```bash
npm install -g pm2
pm2 start "gunicorn -w 4 -b 127.0.0.1:5000 app:app" --name license-api
pm2 save
pm2 startup
```

#### With systemd
```ini
# /etc/systemd/system/license-api.service

[Unit]
Description=License API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/license_server
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable license-api
sudo systemctl start license-api
```

### Database Backup

```bash
# Backup daily
0 2 * * * cp /var/www/license_server/licenses.db /backups/licenses_$(date +\%Y\%m\%d).db
```

### Monitor Logs

```bash
# Watch application logs
tail -f /var/log/license-api.log

# Watch Nginx logs
tail -f /var/log/nginx/access.log
```

---

## ✅ Deployment Checklist

### Pre-Deploy

- [ ] Code pushed to GitHub
- [ ] GitHub Pages enabled
- [ ] Backend server provisioned
- [ ] Domain purchased (optional)
- [ ] Payment gateway accounts created
- [ ] API keys obtained

### Deploy

- [ ] Frontend deployed to GitHub Pages
- [ ] Backend deployed to VPS/Cloud
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] CORS enabled on backend
- [ ] API URLs updated in frontend
- [ ] Payment callback URLs updated

### Post-Deploy

- [ ] Test landing page loads
- [ ] Test API health check
- [ ] Test payment creation
- [ ] Test complete purchase flow
- [ ] Test license activation in OCR app
- [ ] Monitor logs for errors
- [ ] Setup database backups
- [ ] Setup monitoring/alerts

---

## 🎉 Live URLs

After deployment:

- **Frontend:** `https://YOUR_USERNAME.github.io/vietnamese-ocr-license/`
- **Backend API:** `https://api.yourdomain.com`
- **Admin Panel:** `https://api.yourdomain.com/admin`
- **Success Page:** `https://YOUR_USERNAME.github.io/vietnamese-ocr-license/success.html`

---

## 🆘 Troubleshooting

### GitHub Pages not loading

- Check repo is public (or GitHub Pro for private repos)
- Wait 5-10 minutes after enabling Pages
- Check Settings → Pages shows green checkmark
- Try force refresh: Ctrl+F5

### CORS errors in browser console

```javascript
Access to fetch at 'https://api.domain.com' from origin 'https://username.github.io' 
has been blocked by CORS policy
```

**Fix:** Enable CORS on backend (see Step 5)

### Backend not responding

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check Nginx
sudo systemctl status nginx

# Check logs
tail -f /var/log/nginx/error.log
```

### Payment callbacks not working

- Ensure callback URLs are HTTPS
- Check URLs match exactly in payment gateway dashboard
- Check server firewall allows incoming connections
- Test with ngrok first

---

## 📚 Resources

- **GitHub Pages Docs:** https://docs.github.com/pages
- **Nginx Setup:** https://nginx.org/en/docs/
- **Let's Encrypt:** https://letsencrypt.org/
- **Flask Deployment:** https://flask.palletsprojects.com/en/2.3.x/deploying/

---

**🎊 Chúc mừng! Hệ thống đã online và sẵn sàng bán license!**

**Made with ❤️ for Vietnamese OCR Tool**

