# ✅ Deployment Checklist - Deploy to Render.com

Checklist đầy đủ để deploy OCR License Server lên Render.com

---

## 📦 PRE-DEPLOYMENT

### Files cần có:

- [ ] `license_server/render.yaml` - Cấu hình Render
- [ ] `license_server/start.sh` - Start script
- [ ] `license_server/requirements.txt` - Dependencies (có gunicorn)
- [ ] `license_server/app.py` - Main application
- [ ] `license_server/app_config.py` - Config loader
- [ ] `license_server/email_sender.py` - Email module
- [ ] `license_server/payment_gateway.py` - Payment integration
- [ ] `license_server/templates/*.html` - Web templates
- [ ] `.gitignore` - Security

### Accounts cần có:

- [ ] GitHub account
- [ ] Render.com account (free tier OK)
- [ ] 2 Gmail accounts với App Passwords
- [ ] (Optional) Payment gateway accounts

---

## 🔐 SECURITY CHECK

### Before pushing to GitHub:

- [ ] `.gitignore` đã có `license_server/email_config.py`
- [ ] `.gitignore` đã có `*.db`
- [ ] `.gitignore` đã có `email_usage.json`
- [ ] Không có sensitive data trong code
- [ ] ADMIN_API_KEY sẽ được set qua env vars

### Test local .gitignore:

```bash
git status
# Không thấy:
# - license_server/email_config.py
# - license_server/licenses.db
```

---

## 📤 PUSH TO GITHUB

### Step 1: Add files

- [ ] `git add .`
- [ ] Review changes: `git status`
- [ ] Verify no sensitive files included

### Step 2: Commit

- [ ] `git commit -m "Add Render deployment config"`
- [ ] Check commit: `git log -1`

### Step 3: Push

- [ ] `git push origin main`
- [ ] Verify on GitHub: https://github.com/weekend14715/OCR
- [ ] Check files exist on GitHub
- [ ] Verify sensitive files NOT on GitHub

---

## 🚀 CREATE RENDER SERVICE

### Step 1: Login to Render

- [ ] Go to https://render.com
- [ ] Login or Sign up
- [ ] Verify email if needed

### Step 2: Connect GitHub

- [ ] Dashboard → "New +"
- [ ] Select "Web Service"
- [ ] Click "Connect account"
- [ ] Authorize Render to access GitHub
- [ ] Search for "weekend14715/OCR"
- [ ] Click "Connect"

### Step 3: Configure Service

**Basic Settings:**

- [ ] Name: `ocr-license-server`
- [ ] Region: `Oregon (US West)` or `Singapore`
- [ ] Branch: `main`
- [ ] Root Directory: `license_server` ⚠️ IMPORTANT!

**Build Settings:**

- [ ] Runtime: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `bash start.sh`

**Instance:**

- [ ] Instance Type: `Free` (or `Starter` for better performance)
- [ ] Auto-Deploy: ✅ Enabled

### Step 4: Create Service

- [ ] Click "Create Web Service"
- [ ] Wait for initial deployment (may fail, it's OK)

---

## ⚙️ ENVIRONMENT VARIABLES

### Go to Environment Tab

- [ ] Click service → "Environment" tab
- [ ] Ready to add variables

### Required Variables (MUST HAVE):

#### Admin:

- [ ] `ADMIN_API_KEY` = `<generate-strong-password>`
- [ ] `FLASK_ENV` = `production`

#### Email Account 1:

- [ ] `EMAIL_ACCOUNT_1` = `ocrtool.license@gmail.com`
- [ ] `EMAIL_PASSWORD_1` = `gjxhqhqrflvjzurg` (NO SPACES!)
- [ ] `EMAIL_LIMIT_1` = `500`

#### Email Account 2:

- [ ] `EMAIL_ACCOUNT_2` = `ocrtool.system@gmail.com`
- [ ] `EMAIL_PASSWORD_2` = `xjoqoaedkwzjfvxj` (NO SPACES!)
- [ ] `EMAIL_LIMIT_2` = `500`

#### Email Settings:

- [ ] `EMAIL_FROM_NAME` = `OCR Tool License`
- [ ] `EMAIL_SUPPORT` = `hoangtuan.th484@gmail.com`

### Optional Variables (Add later if needed):

#### VNPay:

- [ ] `VNPAY_TMN_CODE`
- [ ] `VNPAY_HASH_SECRET`

#### MoMo:

- [ ] `MOMO_PARTNER_CODE`
- [ ] `MOMO_ACCESS_KEY`
- [ ] `MOMO_SECRET_KEY`

#### ZaloPay:

- [ ] `ZALOPAY_APP_ID`
- [ ] `ZALOPAY_KEY1`
- [ ] `ZALOPAY_KEY2`

### Save:

- [ ] Click "Save Changes"
- [ ] Service will auto-redeploy

---

## 💾 PERSISTENT STORAGE

### Add Disk for Database:

- [ ] Go to "Disks" tab
- [ ] Click "Add Disk"
- [ ] Name: `license-db`
- [ ] Mount Path: `/opt/render/project/src`
- [ ] Size: `1 GB`
- [ ] Click "Save"
- [ ] Service will restart

---

## ✅ VERIFY DEPLOYMENT

### Check Logs:

- [ ] Go to "Logs" tab
- [ ] Wait for deployment to complete (2-5 minutes)
- [ ] Look for success messages:
  - [ ] `==> Building...`
  - [ ] `==> Installing dependencies...`
  - [ ] `🚀 Starting OCR License Server...`
  - [ ] `📦 Initializing database...`
  - [ ] `🌐 Starting Gunicorn server...`
  - [ ] `Your service is live 🎉`

### Get Service URL:

- [ ] Copy URL at top of page (e.g., `https://ocr-license-server.onrender.com`)

### Test Endpoints:

#### 1. Health Check:

```bash
curl https://ocr-license-server.onrender.com/api/health
```

- [ ] Returns: `{"status": "ok", "message": "License Server is running"}`

#### 2. Get Plans:

```bash
curl https://ocr-license-server.onrender.com/api/plans
```

- [ ] Returns: List of plans with pricing

#### 3. Web Interface:

- [ ] Open in browser: `https://ocr-license-server.onrender.com/`
- [ ] See license purchase page
- [ ] Check UI displays correctly

#### 4. Admin Dashboard:

- [ ] Open: `https://ocr-license-server.onrender.com/admin`
- [ ] Enter Admin API Key
- [ ] Access admin panel

---

## 📧 TEST EMAIL FUNCTIONALITY

### Option 1: Via API (if you add test endpoint):

```bash
curl -X POST \
  https://ocr-license-server.onrender.com/test/email \
  -H "X-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "your-email@gmail.com", "license_key": "TEST-KEY"}'
```

- [ ] Email sent successfully
- [ ] Check inbox (or spam)
- [ ] Verify email format

### Option 2: Real Purchase Flow:

- [ ] Go to homepage
- [ ] Select a plan
- [ ] Complete payment (use test mode)
- [ ] Check email received
- [ ] Verify license key in email

---

## 🔍 POST-DEPLOYMENT CHECKS

### Functionality:

- [ ] Homepage loads correctly
- [ ] Plans display with correct pricing
- [ ] Payment gateway integration working
- [ ] License generation working
- [ ] Email sending working
- [ ] License validation API working
- [ ] Admin dashboard accessible

### Performance:

- [ ] Page load time acceptable
- [ ] API response time < 2s
- [ ] No memory leaks (check metrics)

### Security:

- [ ] HTTPS enabled (automatic on Render)
- [ ] Admin API key required for protected endpoints
- [ ] CORS configured correctly
- [ ] No sensitive data exposed in responses

---

## 📊 MONITORING SETUP

### Render Dashboard:

- [ ] Check "Metrics" tab
- [ ] Monitor CPU usage
- [ ] Monitor Memory usage
- [ ] Monitor Request rate

### Set Up Alerts (Optional):

- [ ] Email alerts for service down
- [ ] Slack/Discord webhook for errors

---

## 🔄 AUTO-DEPLOYMENT VERIFICATION

### Test auto-deploy:

- [ ] Make a small change to code (e.g., update README)
- [ ] Commit: `git commit -m "Test auto-deploy"`
- [ ] Push: `git push origin main`
- [ ] Go to Render Dashboard → "Events" tab
- [ ] See "Deploy started" event
- [ ] Wait for deployment to complete
- [ ] Verify change is live

---

## 📱 CUSTOM DOMAIN (Optional)

If you have a custom domain:

- [ ] Purchase domain (Namecheap, GoDaddy, etc.)
- [ ] Go to service → "Settings" → "Custom Domain"
- [ ] Click "Add Custom Domain"
- [ ] Enter domain: `api.yourdomain.com`
- [ ] Get CNAME record from Render
- [ ] Add CNAME to DNS provider
- [ ] Wait for DNS propagation (5-30 minutes)
- [ ] SSL certificate auto-provisioned
- [ ] Test: `https://api.yourdomain.com/api/health`

---

## 💰 BILLING CHECK

### If using Free Tier:

- [ ] Verify within 750 hours/month limit
- [ ] Understand auto-sleep after 15 min inactivity
- [ ] Know cold start time (~30s)

### If upgrading to Starter:

- [ ] Review pricing ($7/month)
- [ ] Add payment method
- [ ] Upgrade instance type
- [ ] Verify always-on (no sleep)

---

## 📝 DOCUMENTATION

### Update docs with deployment info:

- [ ] Document production URL
- [ ] Update API endpoints documentation
- [ ] Document admin API key location
- [ ] Document environment variables
- [ ] Create operations runbook

### Share with team:

- [ ] Share production URL
- [ ] Share admin credentials securely
- [ ] Document deployment process
- [ ] Create incident response plan

---

## 🐛 TROUBLESHOOTING CHECKLIST

### If deployment fails:

- [ ] Check build logs for errors
- [ ] Verify all dependencies in requirements.txt
- [ ] Check Python version compatibility
- [ ] Verify file paths are correct

### If service won't start:

- [ ] Check start command: `bash start.sh`
- [ ] Verify start.sh has correct permissions
- [ ] Check application logs for errors
- [ ] Verify all env vars are set

### If email not working:

- [ ] Verify EMAIL_* env vars are set
- [ ] Check App Passwords have no spaces
- [ ] Check logs for email configuration messages
- [ ] Test Gmail accounts manually

### If database issues:

- [ ] Verify Persistent Disk is attached
- [ ] Check disk mount path: `/opt/render/project/src`
- [ ] Verify database initialization in logs
- [ ] Check file permissions

---

## 🎯 FINAL VERIFICATION

### Complete System Test:

1. **Purchase Flow:**
   - [ ] User visits homepage
   - [ ] User selects plan
   - [ ] User pays (test mode)
   - [ ] Payment successful
   - [ ] License generated
   - [ ] Email sent automatically
   - [ ] User receives license key

2. **Activation Flow:**
   - [ ] User opens OCR Tool
   - [ ] User enters license key
   - [ ] License validated via API
   - [ ] Tool activated successfully

3. **Admin Flow:**
   - [ ] Admin logs in
   - [ ] Admin sees all licenses
   - [ ] Admin can search/filter
   - [ ] Admin can revoke licenses
   - [ ] Stats displayed correctly

---

## 📋 POST-DEPLOYMENT TASKS

### Week 1:

- [ ] Monitor logs daily
- [ ] Check email delivery rate
- [ ] Monitor error rates
- [ ] Review performance metrics
- [ ] Gather user feedback

### Week 2-4:

- [ ] Optimize based on metrics
- [ ] Fix any reported bugs
- [ ] Improve documentation
- [ ] Consider adding features

### Ongoing:

- [ ] Regular security updates
- [ ] Monitor costs
- [ ] Backup database regularly
- [ ] Keep dependencies updated

---

## ✅ DEPLOYMENT COMPLETE!

### Success Criteria:

- [ ] Service is live and accessible
- [ ] All endpoints working
- [ ] Emails sending successfully
- [ ] Payments processing correctly
- [ ] No critical errors in logs
- [ ] Performance acceptable
- [ ] Security measures in place

### Production URL:

```
https://ocr-license-server.onrender.com/
```

### Next Steps:

- [ ] Share URL with customers
- [ ] Monitor usage
- [ ] Collect feedback
- [ ] Iterate and improve

---

**🎉 Congratulations! Your License Server is live!**

---

## 📞 Support

- **Email:** hoangtuan.th484@gmail.com
- **GitHub:** https://github.com/weekend14715/OCR
- **Documentation:** DEPLOY_RENDER.md

---

**Last Updated:** 2024-10-22

