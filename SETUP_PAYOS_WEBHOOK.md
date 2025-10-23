# 🔗 HƯỚNG DẪN LIÊN KẾT WEBHOOK PAYOS VỚI RENDER

## 📋 YÊU CẦU
- ✅ Đã có tài khoản PayOS
- ✅ Đã deploy license server lên Render
- ✅ Server URL: `https://license-server-hjat.onrender.com`

---

## 🎯 BƯỚC 1: LẤY WEBHOOK URL

**Webhook URL của bạn:**
```
https://license-server-hjat.onrender.com/payos/webhook
```

**Test endpoint này trước:**
```bash
curl https://license-server-hjat.onrender.com/payos/health
```

Kết quả mong đợi:
```json
{
  "service": "payos",
  "status": "webhook_ready",
  "version": "1.0"
}
```

---

## 🎯 BƯỚC 2: CẤU HÌNH WEBHOOK TRÊN PAYOS

### Cách 1: Qua Dashboard (Khuyến nghị)

1. **Đăng nhập PayOS:**
   - Vào: https://my.payos.vn/
   - Login bằng tài khoản của bạn

2. **Vào Cài đặt Webhook:**
   ```
   Dashboard → Cài đặt → Webhook
   hoặc
   Dashboard → Settings → Webhook Configuration
   ```

3. **Thêm Webhook URL:**
   - Click **"Thêm Webhook"** hoặc **"Add Webhook"**
   - Nhập URL: `https://license-server-hjat.onrender.com/payos/webhook`
   - Chọn Events:
     * ✅ `payment.success` (Thanh toán thành công)
     * ✅ `payment.failed` (Thanh toán thất bại)
     * ✅ `payment.cancelled` (Thanh toán hủy)

4. **Xác thực Webhook:**
   - PayOS sẽ gửi test request
   - Server của bạn sẽ tự động phản hồi
   - Nếu OK → Webhook được kích hoạt

5. **Lưu cấu hình:**
   - Click **"Lưu"** hoặc **"Save"**

---

### Cách 2: Qua API (Nâng cao)

Nếu PayOS hỗ trợ API để cấu hình webhook:

```python
import requests

payos_api_key = "your-api-key"
webhook_url = "https://license-server-hjat.onrender.com/payos/webhook"

response = requests.post(
    "https://api.payos.vn/v1/webhooks",
    headers={"Authorization": f"Bearer {payos_api_key}"},
    json={
        "url": webhook_url,
        "events": ["payment.success", "payment.failed", "payment.cancelled"]
    }
)

print(response.json())
```

---

## 🎯 BƯỚC 3: KIỂM TRA WEBHOOK ĐANG HOẠT ĐỘNG

### Test 1: Kiểm tra server sẵn sàng
```bash
python test_webhook.py
```

### Test 2: Tạo thanh toán thực
```python
python test_payos_sdk.py
```

Sẽ tạo payment link → Quét QR → PayOS gọi webhook → Server tạo license

---

## 🔍 BƯỚC 4: XEM LOGS WEBHOOK

### Trên Render:
1. Vào: https://dashboard.render.com
2. Chọn service: `license-server-hjat`
3. Click tab **"Logs"**
4. Tìm dòng: `[WEBHOOK] Received PayOS webhook`

### Trên PayOS Dashboard:
1. Vào: https://my.payos.vn/
2. Menu: **"Webhook Logs"** hoặc **"Lịch sử Webhook"**
3. Xem status mỗi request: 200 OK = thành công

---

## ⚠️ XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: Webhook URL không accessible
```
Error: Could not reach webhook URL
```

**Nguyên nhân:** Render service đang sleep (Free plan)

**Giải pháp:**
```bash
# Wake up service trước
curl https://license-server-hjat.onrender.com/payos/health

# Đợi 10s rồi cấu hình lại webhook
```

---

### Lỗi 2: Webhook trả về 500 Internal Error
```
Error: Webhook returned status 500
```

**Nguyên nhân:** Code có bug hoặc thiếu env vars

**Giải pháp:**
```bash
# Xem logs trên Render
# Fix code và redeploy
git add .
git commit -m "Fix webhook handler"
git push
```

---

### Lỗi 3: Signature verification failed
```
Error: Invalid webhook signature
```

**Nguyên nhân:** `PAYOS_WEBHOOK_SECRET` không khớp

**Giải pháp:**
1. Lấy Webhook Secret từ PayOS Dashboard
2. Update env var trên Render:
   ```
   PAYOS_WEBHOOK_SECRET=<your-secret-from-payos>
   ```
3. Restart service

---

## 🧪 BƯỚC 5: TEST TOÀN BỘ FLOW

### Script test tự động:
```python
# test_full_flow.py
import requests
import time

print("🧪 TEST FULL PAYMENT FLOW\n")

# 1. Tạo payment
print("1️⃣ Creating payment...")
response = requests.post(
    "https://license-server-hjat.onrender.com/payos/create-payment",
    json={
        "machine_id": "TEST-MACHINE-001",
        "amount": 200000,
        "months": 1,
        "customer_email": "test@example.com",
        "customer_name": "Nguyen Van A"
    }
)

if response.status_code == 200:
    data = response.json()
    checkout_url = data.get("checkout_url")
    order_id = data.get("order_id")
    
    print(f"✅ Payment created!")
    print(f"   Order ID: {order_id}")
    print(f"   Checkout URL: {checkout_url}")
    print(f"\n2️⃣ Please scan QR code and pay...")
    print(f"   Waiting for webhook...\n")
    
    # 2. Poll license status
    for i in range(30):  # Wait up to 5 minutes
        time.sleep(10)
        check = requests.get(
            f"https://license-server-hjat.onrender.com/license/check",
            params={"machine_id": "TEST-MACHINE-001"}
        )
        
        if check.status_code == 200 and check.json().get("valid"):
            print("✅ License created successfully!")
            print(f"   License data: {check.json()}")
            break
        
        print(f"   [{i+1}/30] Still waiting...")
    else:
        print("❌ Timeout - License not created")
else:
    print(f"❌ Failed to create payment: {response.text}")
```

Chạy test:
```bash
python test_full_flow.py
```

---

## 📊 MONITORING WEBHOOK

### Tạo script check webhook health:
```python
# check_webhook_health.py
import requests
from datetime import datetime

def check_webhook():
    url = "https://license-server-hjat.onrender.com/payos/health"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ [{datetime.now()}] Webhook healthy")
            return True
        else:
            print(f"⚠️ [{datetime.now()}] Webhook returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ [{datetime.now()}] Webhook error: {e}")
        return False

if __name__ == "__main__":
    check_webhook()
```

Chạy định kỳ (mỗi 5 phút):
```bash
# Linux/Mac: crontab
*/5 * * * * python /path/to/check_webhook_health.py

# Windows: Task Scheduler
# Tạo task chạy check_webhook_health.py mỗi 5 phút
```

---

## 🔒 BẢO MẬT WEBHOOK

### Hiện tại server đã có:
1. ✅ **Signature verification** - Xác thực request từ PayOS
2. ✅ **Webhook secret** - Mã hóa dữ liệu
3. ✅ **HTTPS only** - Render tự động cung cấp SSL

### Thêm bảo mật (Optional):
```python
# Thêm IP whitelist trong payos_handler.py
PAYOS_IPS = [
    "103.75.180.0/24",  # PayOS IP range (example)
]

@app.route('/payos/webhook', methods=['POST'])
def webhook():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Check IP whitelist
    if not any(ip_in_range(client_ip, ip_range) for ip_range in PAYOS_IPS):
        return jsonify({"error": "Forbidden"}), 403
    
    # ... rest of webhook handler
```

---

## 📱 NOTIFICATION KHI WEBHOOK HOẠT ĐỘNG

### Thêm Discord/Telegram notification:
```python
# Thêm vào payos_handler.py
import requests

def notify_admin(message):
    # Discord webhook
    discord_url = os.getenv("DISCORD_WEBHOOK_URL")
    if discord_url:
        requests.post(discord_url, json={"content": message})
    
    # Telegram bot
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_token and telegram_chat_id:
        requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={"chat_id": telegram_chat_id, "text": message}
        )

# Gọi khi webhook nhận payment thành công
notify_admin(f"💰 New payment: {amount}đ from {customer_email}")
```

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Server Render đã deploy thành công
- [ ] Endpoint `/payos/health` trả về 200 OK
- [ ] Đã cấu hình webhook URL trên PayOS Dashboard
- [ ] Webhook events đã chọn: payment.success, failed, cancelled
- [ ] Đã test tạo payment và nhận webhook
- [ ] Email tự động gửi sau khi thanh toán
- [ ] Logs webhook hiển thị trên Render
- [ ] Đã setup monitoring (optional)

---

## 🆘 HỖ TRỢ

Nếu gặp vấn đề:

1. **Check logs trên Render:**
   ```
   https://dashboard.render.com → license-server-hjat → Logs
   ```

2. **Test webhook thủ công:**
   ```bash
   curl -X POST https://license-server-hjat.onrender.com/payos/webhook \
     -H "Content-Type: application/json" \
     -d '{"code": "00", "desc": "success", "data": {"orderCode": "TEST123"}}'
   ```

3. **Liên hệ PayOS support:**
   - Email: support@payos.vn
   - Docs: https://payos.vn/docs/

---

## 🎉 KẾT QUẢ MONG ĐỢI

Sau khi cấu hình xong, flow hoạt động như sau:

```
1. Khách hàng → Request license từ app
2. App → Gọi API tạo payment
3. Server → Tạo payment link PayOS
4. Khách hàng → Quét QR và thanh toán
5. PayOS → Gửi webhook đến server
6. Server → Tạo license trong DB
7. Server → Gửi email license cho khách hàng
8. Khách hàng → Nhận email và kích hoạt app
```

**Tự động 100%!** 🚀

