# 🔍 DEBUG QR CODE ISSUE

## 🎯 Mục đích
Debug để xem chính xác data flow từ PayOS API → Backend → Frontend

## 📊 Debug Points

### 1️⃣ **PayOS API Response** (payos_handler.py)
```
========== PAYOS API RESPONSE DEBUG ==========
Response type: ...
Response dir: [...]
Response __dict__: {...}
Response.data: {...}
==============================================
```

### 2️⃣ **Backend Response** (app.py)
```
========== BACKEND RESPONSE DATA ==========
payos_result keys: [...]
checkout_url: https://...
qr_code: Present / MISSING
qr_code length: ...
qr_code first 50 chars: ...
payment_link_id: ...
Sending to frontend: [...]
==========================================
```

### 3️⃣ **Frontend Response** (index.html - Browser Console)
```
========== FULL RESPONSE DATA ==========
Response Object: {...}
All Keys: [...]
========================================
--- QR CODE DEBUG ---
data.qr_code exists: true/false
data.qr_code value: ...
data.qr_code type: ...
data.qr_code length: ...
--- CHECKOUT URL DEBUG ---
data.checkout_url exists: true/false
data.checkout_url value: ...
---------------------
```

## 🧪 Testing Steps

### Step 1: Đợi Render Deploy
```bash
# Check deployment status
# https://dashboard.render.com/
# Wait ~2-3 minutes for deployment
```

### Step 2: Open Browser with DevTools
1. Open Chrome
2. Press `F12` (DevTools)
3. Go to **Console** tab
4. Navigate to: https://ocr-uufr.onrender.com

### Step 3: Create Order
1. Click "Mua License"
2. Enter email
3. Click "Tạo đơn hàng"
4. **WATCH CONSOLE LOGS**

### Step 4: Check Render Logs (Backend)
1. Go to: https://dashboard.render.com/
2. Find your service
3. Click "Logs" tab
4. Look for:
   - `PAYOS API RESPONSE DEBUG`
   - `BACKEND RESPONSE DATA`

## 📋 What to Look For

### ✅ **Case 1: QR Code Present**
**Frontend Console:**
```
data.qr_code exists: true
data.qr_code type: string
data.qr_code length: > 10
→ Displaying QR code on page
```
**Expected:** QR code shows on page ✅

### ⚠️ **Case 2: QR Code Missing**
**Frontend Console:**
```
data.qr_code exists: false (hoặc true)
data.qr_code value: null / undefined / ""
data.checkout_url exists: true
data.checkout_url value: https://pay.payos.vn/...
→ QR not available, redirecting to PayOS checkout page
```
**Expected:** Redirect to PayOS payment page ✅

### ❌ **Case 3: Both Missing**
**Frontend Console:**
```
data.qr_code exists: false
data.checkout_url exists: false
❌ No QR code and no checkout URL!
```
**Expected:** Error message ❌

## 🎯 Possible Issues

### Issue 1: QR Code is empty string
**Symptom:**
```
data.qr_code exists: true
data.qr_code value: ""
data.qr_code length: 0
```
**Fix:** Update condition in frontend:
```javascript
if (data.qr_code && data.qr_code.length > 10) {
  // This will correctly skip empty strings
}
```

### Issue 2: QR Code is null/undefined
**Symptom:**
```
data.qr_code exists: true
data.qr_code value: null
```
**Fix:** Already handled with `data.qr_code &&`

### Issue 3: PayOS doesn't return QR
**Symptom:**
```
[Backend] qr_code: MISSING
[Backend] checkout_url: https://...
```
**Fix:** Already implemented - fallback to checkout_url ✅

## 📝 Expected Log Output

### Full Success Flow:

**Backend (Render Logs):**
```
[PayOS] 🔥 Creating payment link...
========== PAYOS API RESPONSE DEBUG ==========
Response type: <class 'payos.PayOSResponse'>
Response.data: {'paymentLinkId': '...', 'checkoutUrl': '...', 'qrCode': '...'}
==============================================
[PayOS]    Payment ID: abc123
[PayOS]    Checkout URL: https://pay.payos.vn/...
[PayOS]    QR Code: ✅ Present (length: 1234)
[PayOS] Returning result keys: ['success', 'checkout_url', 'qr_code', 'order_id', 'amount', 'payment_link_id']

========== BACKEND RESPONSE DATA ==========
payos_result keys: ['success', 'checkout_url', 'qr_code', 'order_id', 'amount', 'payment_link_id']
checkout_url: https://pay.payos.vn/...
qr_code: Present
qr_code length: 1234
Sending to frontend: ['success', 'order_id', 'amount', 'checkout_url', 'qr_code', 'payment_link_id']
==========================================
```

**Frontend (Browser Console):**
```
========== FULL RESPONSE DATA ==========
Response Object: {success: true, order_id: '...', amount: 100000, ...}
All Keys: ['success', 'order_id', 'amount', 'checkout_url', 'qr_code', 'payment_link_id']
========================================
✅ PayOS Payment Created
Order ID: 1729684800000
Payment Link ID: abc123
Amount: 100000
--- QR CODE DEBUG ---
data.qr_code exists: true
data.qr_code value: data:image/png;base64,iVBORw0KG...
data.qr_code type: string
data.qr_code length: 1234
data.qr_code first 50 chars: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA...
--- CHECKOUT URL DEBUG ---
data.checkout_url exists: true
data.checkout_url value: https://pay.payos.vn/web/abc123
data.checkout_url type: string
---------------------
→ Displaying QR code on page
```

## 🚀 Next Steps

1. **Test trên Render** (sau khi deploy)
2. **Copy ALL logs** từ:
   - Browser Console (frontend)
   - Render Logs (backend)
3. **Paste logs** để phân tích
4. **Identify** chỗ nào data bị missing
5. **Fix** logic nếu cần

---

## 🎉 **UPDATE: ISSUE FIXED!**

### **Root Cause Found:**
PayOS trả về **QR code text string** (VietQR EMV format), KHÔNG phải base64 image!

```javascript
data.qr_code = "00020101021238590010A00000072701290006970418..."
```
→ Code cũ set `<img src="...">` → Browser cố load text như URL → 404 Error!

### **Solution Applied:**
✅ Added **QRCode.js** library  
✅ Convert QR text → QR image using `new QRCode()`  
✅ Error handling with fallback to PayOS checkout  

**See:** `QR_CODE_FIX_SUMMARY.md` for full technical details

---

**Current Status:**
- ✅ Debug logs added
- ✅ Fallback logic implemented
- ✅ **QR CODE DISPLAY FIXED!**
- 🚀 Deployed to production (commit `279dce2`)
- 🧪 Ready to test!

