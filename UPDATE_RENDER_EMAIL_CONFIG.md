# 📧 CẬP NHẬT EMAIL CONFIG TRÊN RENDER

## ✅ Bạn đã nhận được email test thành công!

Bây giờ cần update config trên Render để production cũng gửi được email.

---

## 🔧 BƯỚC 1: Vào Render Dashboard

1. Vào: https://dashboard.render.com
2. Click vào service: **ocr-uufr**
3. Click tab **Environment** (bên trái)

---

## 🔧 BƯỚC 2: Thêm Environment Variables

Click **Add Environment Variable** và thêm các biến sau:

### **EMAIL_ACCOUNTS (JSON format):**

**Key:** `EMAIL_ACCOUNTS`

**Value:** (Copy toàn bộ đoạn này - bao gồm cả dấu ngoặc):
```json
[{"email": "ocrtool.license@gmail.com", "app_password": "xvfn cnxz nmxf mxbq", "display_name": "OCR License System"}, {"email": "ocrtool.system@gmail.com", "app_password": "rweo mwrd xnkj xgzy", "display_name": "OCR Tool System"}]
```

---

## 🔧 BƯỚC 3: Save Changes

1. Click **Save Changes** (nút xanh phía trên)
2. Render sẽ tự động **redeploy** (~2 phút)
3. Đợi deploy xong (status: **Live**)

---

## ✅ BƯỚC 4: Test trên Production

### **4.1. Vào Admin Panel:**
```
https://ocr-uufr.onrender.com/admin
```

### **4.2. Tạo License Test:**

1. Điền form:
   - **Email:** hoangtuan.th484@gmail.com
   - **Customer Name:** Hoang Tuan Test
   - **Plan:** lifetime
   - **Payment Method:** bank_transfer

2. Click **Create License**

3. Check inbox của bạn!

---

## 🎯 KẾT QUẢ MONG ĐỢI:

✅ License được tạo thành công
✅ Email được gửi đến: hoangtuan.th484@gmail.com
✅ Bạn nhận được email với license key
✅ Email gửi từ: ocrtool.license@gmail.com hoặc ocrtool.system@gmail.com

---

## 🔍 KIỂM TRA LOGS (Nếu có lỗi):

1. Vào tab **Logs** trên Render
2. Tìm dòng:
   ```
   ✅ Email sent to ... via ...
   ```
3. Hoặc tìm lỗi:
   ```
   ❌ Email failed: ...
   ```

---

## 📝 LƯU Ý:

- **Email Config** được lưu trong Environment Variables (an toàn)
- **Không push** `email_config.py` lên GitHub (đã bị gitignore)
- **2 Gmail accounts** gửi luân phiên (round-robin)
- **Giới hạn:** 1000 emails/day (500 + 500)

---

## 🆘 NẾU CÓ LỖI:

### **Lỗi: "Invalid credentials"**
→ Check lại App Password có đúng không

### **Lỗi: "SMTP server connection failed"**
→ Check internet connection của Render

### **Email không đến inbox:**
→ Check **Spam folder**

### **Render không tìm thấy EMAIL_ACCOUNTS:**
→ Check lại format JSON có đúng không (phải là 1 dòng, không xuống dòng)

---

## ✅ DONE!

Sau khi update xong và test thành công → **Hệ thống sẵn sàng gửi email tự động!** 🎉

**Workflow hoàn chỉnh:**
1. Customer mua license → PayOS webhook
2. Webhook tạo license → Database
3. Hệ thống gửi email → Gmail accounts
4. Customer nhận email → License key
5. Done! ✅

---

**Questions?** Check logs hoặc inbox để debug! 📧

