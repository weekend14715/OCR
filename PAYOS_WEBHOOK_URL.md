# 🔗 PayOS Webhook URL - Hướng Dẫn Cấu Hình

## ✅ URL WEBHOOK CHÍNH XÁC:

```
https://ocr-uufr.onrender.com/api/webhook/payos
```

---

## 📋 CÁCH CẤU HÌNH TRONG PAYOS DASHBOARD:

### Bước 1: Vào PayOS Settings
1. Đăng nhập https://my.payos.vn
2. Chọn merchant **"OCR Vietnamese"**
3. Click vào **"Chỉnh sửa thông tin"** (icon ⚙️)

### Bước 2: Tìm phần "Thiết lập nâng cao"
- Kéo xuống dưới
- Tìm mục **"Webhook Url"**

### Bước 3: Điền URL Webhook
Nhập chính xác (copy/paste):
```
https://ocr-uufr.onrender.com/api/webhook/payos
```

### Bước 4: Lưu
- Click nút **"Lưu"** (màu xanh)
- PayOS sẽ test webhook ngay lập tức
- Nếu thành công → Không hiện lỗi
- Nếu lỗi → Hiện popup cảnh báo

---

## 🔍 CÁCH KIỂM TRA URL ĐÚNG CHƯA:

### Test bằng curl:
```bash
curl -X POST https://ocr-uufr.onrender.com/api/webhook/payos \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**Kết quả mong đợi:**
```json
{"status": "received"}
```

Hoặc xem trong Render logs:
```
📩 Received PayOS webhook: {'test': True}
```

---

## 🏗️ CẤU TRÚC URL:

```
https://ocr-uufr.onrender.com  ← Domain Render của bạn
       /api/webhook/payos       ← Endpoint trong code
```

### Domain được định nghĩa ở đâu?
- Tên service Render: **ocr-uufr**
- → Domain tự động: **ocr-uufr.onrender.com**

### Endpoint được định nghĩa ở đâu?
File: `license_server/app.py`
```python
@app.route('/api/webhook/payos', methods=['POST'])
def payos_webhook():
    # ... xử lý webhook
```

---

## ⚠️ LƯU Ý QUAN TRỌNG:

### ✅ ĐÚNG:
- `https://ocr-uufr.onrender.com/api/webhook/payos` ✅
- Protocol: **https** (có SSL)
- Không có dấu `/` cuối cùng

### ❌ SAI:
- `http://ocr-uufr.onrender.com/api/webhook/payos` ❌ (không SSL)
- `https://ocr-uufr.onrender.com/api/webhook/payos/` ❌ (có `/` cuối)
- `https://ocr-uufr.onrender.com/webhook/payos` ❌ (thiếu `/api`)

---

## 🧪 CÁCH TEST SAU KHI CẤU HÌNH:

### Cách 1: Test Webhook trong PayOS Dashboard
1. Vào PayOS Dashboard
2. Sau khi lưu webhook URL
3. PayOS tự động gửi test request
4. Xem có lỗi không

### Cách 2: Tạo đơn hàng thử
1. Vào app OCR
2. Chọn gói license (30 ngày)
3. Click "Thanh toán"
4. PayOS tạo QR code
5. **Quét & thanh toán**
6. → Webhook tự động được gọi
7. Xem logs trong Render

### Cách 3: Xem Render Logs
1. Vào https://dashboard.render.com
2. Chọn service **ocr-uufr**
3. Click tab **"Logs"**
4. Tìm dòng:
   ```
   📩 Received PayOS webhook: {...}
   ```

---

## 🐛 TROUBLESHOOTING:

### Lỗi 404 - Not Found
**Nguyên nhân:** URL sai hoặc endpoint chưa deploy
**Giải pháp:**
- Kiểm tra lại URL (copy/paste từ đây)
- Đợi Render deploy xong (check tab "Logs")

### Lỗi 401 - Unauthorized
**Nguyên nhân:** Signature verification lỗi (đã fix!)
**Giải pháp:** Đã tắt signature verification tạm thời

### Lỗi 500 - Internal Server Error
**Nguyên nhân:** Lỗi code trong webhook handler
**Giải pháp:** Xem logs trong Render để debug

### Không nhận được webhook
**Nguyên nhân:** Render service đang sleep
**Giải pháp:**
- Render Free tier sleep sau 15 phút không dùng
- Truy cập https://ocr-uufr.onrender.com/health để đánh thức
- Hoặc upgrade lên Render Paid ($7/tháng)

---

## 📊 XEM LOGS WEBHOOK:

### Trong Render:
1. https://dashboard.render.com
2. Service: **ocr-uufr**
3. Tab: **Logs**
4. Filter: Tìm "webhook"

### Log mẫu khi thành công:
```
📩 Received PayOS webhook: {
  'code': '00',
  'desc': 'success', 
  'data': {
    'orderCode': 123456,
    'amount': 30000,
    'description': 'Mua license 30 ngay',
    'status': 'PAID'
  }
}
✅ Payment verified, activating license...
🎉 License activated: XXX-XXX-XXX
```

---

## 🚀 QUICK START:

Copy URL này vào PayOS:
```
https://ocr-uufr.onrender.com/api/webhook/payos
```

1. Vào https://my.payos.vn
2. Chọn **"OCR Vietnamese"**
3. **"Chỉnh sửa thông tin"**
4. Phần **"Webhook Url"** → Paste URL trên
5. Click **"Lưu"**
6. Xong! ✅

---

**Bây giờ hãy thử cấu hình webhook trong PayOS Dashboard!** 🎯

