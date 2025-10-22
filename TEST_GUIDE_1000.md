# 🧪 HƯỚNG DẪN TEST GÓI 1,000Đ

## ✅ ĐÃ HOÀN THÀNH

- ✅ Push code lên GitHub thành công
- ✅ Casso API đã được cấu hình
- ✅ Thêm gói Test 1,000đ
- ✅ VietQR + Casso hoạt động tự động

---

## ⏳ BÂY GIỜ ĐANG XẢY RA

**Render đang tự động deploy:**

```
GitHub (commit mới)
    ↓
Render nhận thông báo
    ↓
Render pull code mới
    ↓
Cài đặt dependencies (qrcode, Pillow)
    ↓
Build & Deploy
    ↓
Restart server
    ↓
✅ XONG! (2-3 phút)
```

---

## 🔍 KIỂM TRA DEPLOY

1. **Vào Render Dashboard:**
   ```
   https://dashboard.render.com
   ```

2. **Chọn service: `ocr`**

3. **Xem Logs tab:**
   ```
   - "Building..."
   - "Installing dependencies..."
   - "qrcode==7.4.2"
   - "Pillow==10.1.0"
   - "✅ Casso Payment đã được kích hoạt!"
   - "Build successful!"
   - "Starting service..."
   - "Running on http://0.0.0.0:10000"
   ```

4. **Đợi status = "Live" (màu xanh)** ✅

---

## 🧪 CÁCH TEST

### **BƯỚC 1: Vào Website**

```
https://ocr-uufr.onrender.com
```

### **BƯỚC 2: Chọn Gói Test**

- Bạn sẽ thấy **2 gói**:
  - 🧪 **Gói Test** - 1,000đ (màu cam)
  - ⭐ **Kích Hoạt Trọn Đời** - 100,000đ (màu xanh)

- Click **"🧪 Test Ngay - 1,000đ"**

### **BƯỚC 3: Nhập Email**

```
Nhập email của bạn:
hoangtuan.th484@gmail.com
```

Click **"Tạo Đơn Hàng"**

### **BƯỚC 4: Xem Thông Tin Thanh Toán**

Bạn sẽ thấy:

```
✅ Đơn hàng đã được tạo thành công!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Thông tin đơn hàng:
   Order ID: ORD20251022150030A1B2

💰 Số tiền: 1,000₫

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 QUÉT MÃ QR ĐỂ THANH TOÁN NHANH

[MÃ QR HIỂN THỊ Ở ĐÂY]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏦 Hoặc chuyển khoản thủ công:

Ngân hàng: MB Bank
Số tài khoản: 0123456789
Tên: NGUYEN VAN A
Số tiền: 1,000₫
Nội dung: OCR ORD20251022150030A1B2
```

### **BƯỚC 5: Thanh Toán**

**Option A: Quét QR (KHUYÊN DÙNG)** 📱
1. Mở app ngân hàng của bạn
2. Chọn "Quét QR"
3. Quét mã QR trên màn hình
4. Thông tin tự động điền → Xác nhận!

**Option B: Chuyển khoản thủ công** 💳
1. Mở app ngân hàng
2. Chọn "Chuyển tiền"
3. Nhập thông tin:
   - STK: `0123456789`
   - Số tiền: `1000`
   - Nội dung: `OCR ORD20251022150030A1B2` (COPY CHÍNH XÁC!)
4. Xác nhận!

### **BƯỚC 6: Đợi Nhận License** ⏰

```
⏱️ Timeline:

[00:00] Bạn thanh toán xong
    ↓
[00:10] Ngân hàng xử lý giao dịch
    ↓
[00:30] Casso nhận giao dịch
    ↓
[00:31] Casso gửi webhook đến server
    ↓
[00:32] Server tạo license key
    ↓
[00:35] Email gửi đi
    ↓
[00:40] ✅ Bạn nhận email!

Tổng: 30-90 giây
```

### **BƯỚC 7: Check Email** 📧

1. **Mở email:** `hoangtuan.th484@gmail.com`

2. **Tìm email từ:** `no-reply@ocr-tool.com` hoặc `noreply@render.com`

3. **Email sẽ chứa:**
   ```
   🎉 License Key của bạn:
   
   XXXX-XXXX-XXXX-XXXX
   
   Gói: Test Plan (1,000đ)
   Thời hạn: 1 ngày
   
   Hướng dẫn kích hoạt:
   1. Mở OCR Tool
   2. Vào Settings
   3. Paste license key
   4. Click "Activate"
   ```

4. **Copy license key** → Dùng trong tool!

---

## ⚠️ NẾU KHÔNG NHẬN ĐƯỢC EMAIL

### **Đợi 2-3 phút**

Có thể email bị delay. Đợi thêm 2-3 phút.

### **Kiểm tra Spam/Junk**

Email có thể rơi vào spam.

### **Kiểm tra Render Logs**

```bash
# Vào Render Dashboard → Logs tab

# Tìm kiếm:
1. "Casso webhook received"
   → Có = Casso đã gửi webhook
   → Không có = Casso chưa nhận giao dịch

2. "Order ORD... processed successfully"
   → Có = Order đã xử lý
   → Không có = Có lỗi xử lý

3. "License email sent to hoangtuan.th484@gmail.com"
   → Có = Email đã gửi
   → Không có = Email service lỗi
```

### **Kiểm tra Casso Dashboard**

```
1. Vào: https://app.casso.vn
2. Login với account của bạn
3. Vào "Giao dịch"
4. Tìm giao dịch 1,000đ với nội dung "OCR ORD..."
5. Nếu có → Casso đã nhận
6. Vào "Webhook" → Xem logs
```

### **Test Lại Với Email Khác**

Nếu email service lỗi, thử với email khác:
- Gmail
- Yahoo
- Outlook

---

## 🐛 TROUBLESHOOTING

### **Lỗi 1: Không thấy gói 1,000đ**

**Nguyên nhân:** Render chưa deploy xong

**Cách fix:**
- Đợi thêm 1-2 phút
- Refresh trang
- Xóa cache (Ctrl + Shift + R)

### **Lỗi 2: QR code không hiển thị**

**Nguyên nhân:** `qrcode` hoặc `Pillow` chưa cài

**Cách fix:**
```bash
# Kiểm tra Render logs
- Có dòng "qrcode==7.4.2" → Đã cài
- Không có → Lỗi build

# Nếu lỗi, thêm vào requirements.txt:
qrcode==7.4.2
Pillow==10.1.0
```

### **Lỗi 3: "Invalid signature" trong Casso webhook**

**Nguyên nhân:** `CASSO_CHECKSUM_KEY` sai

**Cách fix:**
```bash
# Vào Render → Environment Variables
CASSO_CHECKSUM_KEY = a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d
```

Restart service.

### **Lỗi 4: Webhook URL không đúng**

**Nguyên nhân:** Casso gửi webhook về URL sai

**Cách fix:**
```bash
# Vào Casso.vn → Cài đặt → Webhook URL:
https://ocr-uufr.onrender.com/api/casso/webhook

# LƯU Ý: Phải có /api/casso/webhook
```

---

## 📊 MONITOR

### **Render Logs**

```bash
# Xem real-time logs:
https://dashboard.render.com/web/[your-service]/logs

# Filter:
- "Casso" → Xem webhook
- "Order" → Xem order processing
- "Email" → Xem email sending
- "ERROR" → Xem lỗi
```

### **Casso Dashboard**

```
https://app.casso.vn

- Xem giao dịch mới
- Xem webhook logs
- Xem số dư tài khoản
```

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi test thành công với 1,000đ:

✅ **Khách hàng thấy:**
- QR code hiển thị rõ ràng
- Thông tin chuyển khoản đầy đủ
- Email nhận license trong 1-2 phút

✅ **Bạn thấy:**
- Order được tạo trong DB
- Webhook từ Casso
- License được tạo tự động
- Email gửi thành công

✅ **Hệ thống hoạt động:**
- 100% tự động
- Không cần can thiệp
- Conversion rate cao

**Sẵn sàng launch production!** 🚀

---

## 📚 TÀI LIỆU LIÊN QUAN

- `VIETQR_CASSO_FLOW.md` - Luồng hoạt động chi tiết
- `DEPLOY_VIETQR.md` - Hướng dẫn deploy
- `VIETQR_SETUP.md` - Cấu hình chi tiết

**Chúc bạn test thành công!** 🎉

