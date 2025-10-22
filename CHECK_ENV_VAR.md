# ✅ KIỂM TRA BIẾN EMAIL_ACCOUNTS TRÊN RENDER

## VẤN ĐỀ CÓ THỂ:

Biến `EMAIL_ACCOUNTS` trên Render có thể:
- ❌ Bị lỗi format JSON
- ❌ Có ký tự đặc biệt không hợp lệ
- ❌ Thiếu dấu ngoặc

---

## CÁCH KIỂM TRA:

### BƯỚC 1: Vào Render Environment Variables

1. **Render Dashboard** → Service `ocr-uufr`
2. Tab **"Environment"**
3. Tìm biến `EMAIL_ACCOUNTS`

### BƯỚC 2: Xác Nhận Format Chính Xác

Giá trị phải giống y hệt thế này (KHÔNG có khoảng trắng thừa):

```json
[{"email":"ocrtool.license@gmail.com","password":"YOUR_APP_PASSWORD_1","daily_limit":500},{"email":"hoangtuan.th484@gmail.com","password":"YOUR_APP_PASSWORD_2","daily_limit":500}]
```

**LƯU Ý:**
- ✅ Dùng dấu ngoặc kép `"` (không phải `'`)
- ✅ KHÔNG có khoảng trắng thừa
- ✅ KHÔNG xuống dòng
- ✅ Password phải là **App Password** (16 ký tự dạng: `xxxx xxxx xxxx xxxx`)

---

### BƯỚC 3: Nếu Sai Format - Sửa Lại

**Copy đoạn này và thay YOUR_APP_PASSWORD:**

```
[{"email":"ocrtool.license@gmail.com","password":"YOUR_APP_PASSWORD_1","daily_limit":500},{"email":"hoangtuan.th484@gmail.com","password":"YOUR_APP_PASSWORD_2","daily_limit":500}]
```

Thay:
- `YOUR_APP_PASSWORD_1` → App Password của `ocrtool.license@gmail.com`
- `YOUR_APP_PASSWORD_2` → App Password của `hoangtuan.th484@gmail.com`

**VÍ DỤ ĐÚNG:**
```
[{"email":"ocrtool.license@gmail.com","password":"abcd efgh ijkl mnop","daily_limit":500},{"email":"hoangtuan.th484@gmail.com","password":"wxyz 1234 5678 9000","daily_limit":500}]
```

---

### BƯỚC 4: Sau Khi Sửa

1. Click **"Save Changes"** trên Render
2. Render sẽ tự động **redeploy**
3. Đợi 2-3 phút
4. Vào **Logs** → Tìm dòng `[OK] Email config loaded`

---

## CÁCH NHANH: Tạo Lại Biến

Nếu muốn chắc chắn:

1. **XÓA** biến `EMAIL_ACCOUNTS` cũ
2. **TẠO MỚI** biến `EMAIL_ACCOUNTS` với giá trị:

```
[{"email":"ocrtool.license@gmail.com","password":"PASTE_APP_PASSWORD_1_HERE","daily_limit":500},{"email":"hoangtuan.th484@gmail.com","password":"PASTE_APP_PASSWORD_2_HERE","daily_limit":500}]
```

3. Save → Đợi redeploy → Check Logs

