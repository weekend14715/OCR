# 🔑 Admin API Key - Hướng Dẫn Cấu Hình

## ✅ ADMIN API KEY CỦA BẠN:

```
OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE
```

**⚠️ LƯU Ý: Giữ key này bí mật! Đừng share cho ai!**

---

## 📋 ADMIN API KEY LÀ GÌ?

**Admin API Key** = Mật khẩu để:
- ✅ Bảo vệ trang Admin (`/admin`)
- ✅ Tạo license mới (Lifetime/Trial)
- ✅ Xem danh sách tất cả licenses
- ✅ Ngăn người lạ truy cập

**Không có key này → Không thể dùng trang admin!**

---

## 🚀 CÁCH CẤU HÌNH:

### Option 1: Cấu hình trong Render (KHUYÊN DÙNG)

#### Bước 1: Vào Render Dashboard
1. Đăng nhập https://dashboard.render.com
2. Chọn service: **ocr-uufr**
3. Click tab **"Environment"** (bên trái)

#### Bước 2: Thêm Environment Variable
Click nút **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `ADMIN_API_KEY` | `OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE` |

#### Bước 3: Save Changes
- Click **"Save Changes"** (nút xanh)
- Render sẽ tự động **redeploy** (~2-3 phút)
- Đợi deploy xong (xem tab "Logs")

---

### Option 2: Hardcode trong Code (Không khuyên dùng)

File: `license_server/app.py` (dòng 41):

```python
# Cũ (không bảo mật):
ADMIN_API_KEY = 'your-secure-admin-api-key-here-change-this'

# Mới (đổi thành):
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE')
```

**Nhưng tốt nhất là dùng Option 1 (Environment Variable)!**

---

## 🎯 CÁCH SỬ DỤNG ADMIN API KEY:

### Khi vào trang Admin:

1. Truy cập: https://ocr-uufr.onrender.com/admin

2. Điền vào ô **"Admin API Key"**:
   ```
   OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE
   ```

3. Chọn các thông tin khác:
   - **Loại Gói:** Lifetime (Trọn đời) hoặc 30/90/180 ngày
   - **Số Lượng:** 1
   - **Email Khách Hàng:** email của người nhận

4. Click **"🎁 Tạo License"**

5. → License mới được tạo và hiện trong **"Danh Sách Licenses"**

---

## 📊 CẤU TRÚC CODE:

### File: `license_server/app.py`

```python
# Dòng 41: Định nghĩa ADMIN_API_KEY
ADMIN_API_KEY = 'your-secure-admin-api-key-here-change-this'

# Dòng 134: Kiểm tra API key khi tạo license
@app.route('/admin/create_license', methods=['POST'])
def admin_create_license():
    api_key = request.form.get('api_key')
    
    if api_key != ADMIN_API_KEY:
        return jsonify({'success': False, 'error': 'Invalid API Key'})
    
    # ... tạo license
```

**Luồng hoạt động:**
1. User điền API key vào form
2. Backend check: `api_key == ADMIN_API_KEY`
3. ✅ Đúng → Tạo license
4. ❌ Sai → Trả lỗi "Invalid API Key"

---

## 🔒 BẢO MẬT:

### ✅ NÊN:
- Lưu API key trong **environment variables** (Render)
- Dùng key ngẫu nhiên dài (như key phía trên)
- Giữ bí mật, không share
- Đổi key định kỳ (3-6 tháng)

### ❌ KHÔNG NÊN:
- Hardcode trong code rồi push lên GitHub
- Dùng key đơn giản: `admin123`, `password`
- Share key qua email/chat không mã hóa
- Để key mặc định: `your-secure-admin-api-key-here-change-this`

---

## 🧪 CÁCH TEST:

### Test 1: Kiểm tra API key có hoạt động không

```bash
curl -X POST https://ocr-uufr.onrender.com/admin/create_license \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE" \
  -d "license_type=trial" \
  -d "days=30" \
  -d "quantity=1" \
  -d "customer_email=test@example.com"
```

**Kết quả mong đợi:**
```json
{
  "success": true,
  "licenses": ["XXX-XXX-XXX"]
}
```

### Test 2: Vào trang admin
1. Truy cập: https://ocr-uufr.onrender.com/admin
2. Paste API key vào ô "Admin API Key"
3. Điền thông tin license
4. Click "Tạo License"
5. → Danh sách license hiện ngay

---

## 🐛 TROUBLESHOOTING:

### Lỗi: "Vui lòng nhập Admin API Key để xem danh sách"

**Nguyên nhân:** Chưa điền API key hoặc điền sai

**Giải pháp:**
1. Paste đúng key: `OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE`
2. Không có khoảng trắng thừa
3. Copy/paste toàn bộ (không thiếu ký tự)

### Lỗi: "Invalid API Key"

**Nguyên nhân:** API key trong form ≠ API key trong server

**Giải pháp:**
1. Kiểm tra Render Environment Variables
2. Xem logs: `print(f"🔑 Admin API Key: {ADMIN_API_KEY}")`
3. Đảm bảo đã redeploy sau khi thêm env var

### Trang admin không load

**Nguyên nhân:** Render service đang sleep

**Giải pháp:**
1. Truy cập https://ocr-uufr.onrender.com/health trước
2. Đợi 10-15 giây
3. Vào lại https://ocr-uufr.onrender.com/admin

---

## 📝 CHECKLIST CẤU HÌNH:

- [ ] **Bước 1:** Vào Render Dashboard
- [ ] **Bước 2:** Chọn service "ocr-uufr"
- [ ] **Bước 3:** Tab "Environment"
- [ ] **Bước 4:** Add Environment Variable:
  - Key: `ADMIN_API_KEY`
  - Value: `OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE`
- [ ] **Bước 5:** Click "Save Changes"
- [ ] **Bước 6:** Đợi redeploy xong (~2-3 phút)
- [ ] **Bước 7:** Test vào https://ocr-uufr.onrender.com/admin
- [ ] **Bước 8:** Paste API key vào form
- [ ] **Bước 9:** Tạo license thử
- [ ] **Bước 10:** Xem danh sách licenses

---

## 🎁 ADMIN API KEY - LƯU LẠI:

```
OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE
```

**Hãy lưu key này vào:**
- 📱 Password manager (1Password, Bitwarden, LastPass)
- 📝 File text bảo mật trên máy local
- 🔐 Encrypted note (OneNote, Notion với password)

**KHÔNG lưu vào:**
- ❌ Email
- ❌ Chat không mã hóa
- ❌ GitHub public repository
- ❌ Google Docs công khai

---

## 🚀 QUICK START:

1. **Copy API Key:**
   ```
   OCR_ADMIN_MUJpeW9fPbSNuX22esEVOp1Klm0JlOjvMO_lS-OdfUE
   ```

2. **Vào Render:**
   - https://dashboard.render.com
   - Service: **ocr-uufr**
   - Tab: **Environment**
   - Add: `ADMIN_API_KEY` = (paste key trên)
   - Save Changes

3. **Test:**
   - Vào https://ocr-uufr.onrender.com/admin
   - Paste API key
   - Tạo license thử
   - Thành công! ✅

---

**Bây giờ hãy thêm API Key vào Render Environment Variables!** 🎯

