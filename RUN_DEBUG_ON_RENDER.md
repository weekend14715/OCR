# 🔍 CHẠY TOOL DEBUG TRÊN RENDER

Em vừa tạo tool debug để kiểm tra biến `EMAIL_ACCOUNTS` trên Render.

---

## BƯỚC 1: Push Code Lên

```bash
git add license_server/test_env.py
git commit -m "Add debug tool for EMAIL_ACCOUNTS"
git push origin main
```

---

## BƯỚC 2: Chạy Trên Render

### Cách A: Dùng Shell Tab (Nếu có)

1. Vào **Render Dashboard** → Service `ocr-uufr`
2. Tab **"Shell"** (nếu có)
3. Chạy:
   ```bash
   cd license_server
   python test_env.py
   ```

### Cách B: Tạo Endpoint Test (Dễ hơn)

Em sẽ tạo endpoint `/test-email-config` để anh truy cập trực tiếp qua browser!

---

## HOẶC - Đơn Giản Nhất:

**Kiểm tra Logs sau khi deploy:**

1. Đợi Render deploy xong
2. Vào **Logs** tab
3. Tìm 1 trong 3 dòng:
   - ✅ `[OK] Email config loaded from environment variable (2 accounts)`
   - ⚠️ `[WARNING] Could not parse EMAIL_ACCOUNTS env var: ...`
   - ⚠️ `[WARNING] No email config found`

**Nếu thấy dòng WARNING → Chụp màn hình gửi em!**

---

## GỢI Ý TỐT NHẤT:

Anh chụp màn hình cho em xem:
1. **Render → Tab "Logs"** (scroll lên phần đầu sau khi deploy)
2. **Render → Tab "Environment"** → Biến `EMAIL_ACCOUNTS` (che mật khẩu)

Em sẽ giúp anh debug chính xác! 😊

