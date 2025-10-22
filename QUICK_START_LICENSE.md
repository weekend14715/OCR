# 🚀 Quick Start - License System

## ⚡ Bắt đầu nhanh trong 5 phút

### Bước 1: Cài đặt dependencies

```bash
cd license_server
pip install -r requirements.txt
```

### Bước 2: Đổi Admin API Key

Mở `license_server/app.py`, tìm dòng:

```python
ADMIN_API_KEY = 'your-secure-admin-api-key-here-change-this'
```

Đổi thành (ví dụ):

```python
ADMIN_API_KEY = 'my-super-secret-key-2025'
```

### Bước 3: Chạy License Server

```bash
python app.py
```

Server chạy tại: `http://127.0.0.1:5000`

### Bước 4: Mở Admin Panel

Trình duyệt, truy cập:

```
http://127.0.0.1:5000/admin
```

### Bước 5: Tạo License Key

1. Nhập **Admin API Key** vào ô "Admin API Key"
2. Chọn loại gói: **Lifetime**
3. Số lượng: **1**
4. Email: `test@example.com`
5. Click **"🎁 Tạo License"**
6. **Copy license key** (dạng: `XXXX-XXXX-XXXX-XXXX`)

### Bước 6: Test License Client

Mở terminal mới:

```bash
python license_client.py
```

Nhập license key vừa tạo khi được yêu cầu.

### Bước 7: Chạy OCR App với License

```bash
python ocr_tool_licensed.py
```

Nhập license key khi dialog hiện ra.

---

## 🎯 Demo nhanh

### Tạo license bằng API:

```bash
curl -X POST http://127.0.0.1:5000/api/admin/generate \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: my-super-secret-key-2025" \
  -d '{"plan_type":"lifetime","quantity":1,"email":"test@example.com"}'
```

### Test validation:

```bash
curl -X POST http://127.0.0.1:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"license_key":"XXXX-XXXX-XXXX-XXXX","machine_id":"test-machine"}'
```

---

## 🧪 Chạy test tự động

```bash
# Đảm bảo server đang chạy
python test_license_system.py
```

Sẽ tự động test:
- ✅ Tạo 3 licenses (lifetime, yearly, monthly)
- ✅ Kích hoạt license
- ✅ Validate với cùng máy
- ✅ Chặn máy khác
- ✅ Vô hiệu hóa license
- ✅ Xem thống kê

---

## 📱 Xem Landing Page

Truy cập:

```
http://127.0.0.1:5000/
```

Sẽ thấy trang bán license với 3 gói giá.

---

## ❓ Troubleshooting

### Lỗi: "Cannot connect to server"

→ Chắc chắn server đang chạy: `python app.py`

### Lỗi: "Unauthorized"

→ Kiểm tra Admin API Key đúng chưa

### Lỗi: "License already activated on another machine"

→ Đúng! Mỗi license chỉ dùng được 1 máy. Dùng "Deactivate" để chuyển máy.

---

## 📞 Cần trợ giúp?

Đọc file: `LICENSE_SYSTEM_README.md` để biết chi tiết.

