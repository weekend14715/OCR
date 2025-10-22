# 🏦 HƯỚNG DẪN SETUP VIETQR

## ✅ ĐÃ HOÀN THÀNH

Hệ thống VietQR đã được tích hợp thành công! 🎉

### Tính năng mới:
1. ✅ **Tự động tạo mã QR** thanh toán khi khách hàng nhập email
2. ✅ **Hiển thị QR code** trên trang thanh toán
3. ✅ **Nội dung CK tự động** được điền sẵn trong QR (email khách hàng)
4. ✅ **Hỗ trợ quét bằng app ngân hàng** - Thanh toán nhanh chóng!

---

## 🔧 CẬP NHẬT THÔNG TIN NGÂN HÀNG

### Bước 1: Mở file `license_server/payment_gateway.py`

Tìm đến dòng 450-460, phần `get_bank_info()`:

```python
@staticmethod
def get_bank_info():
    """
    Lấy thông tin ngân hàng để hiển thị
    Thay đổi thông tin này theo tài khoản thật của bạn
    """
    return {
        'bank_code': 'MB',  # MB Bank
        'bank_name': 'MB Bank (Ngân hàng Quân Đội)',
        'account_number': '0123456789',  # THAY ĐỔI
        'account_name': 'NGUYEN VAN A',  # THAY ĐỔI
    }
```

### Bước 2: Thay đổi thông tin

**Ví dụ với MB Bank:**
```python
return {
    'bank_code': 'MB',
    'bank_name': 'MB Bank (Ngân hàng Quân Đội)',
    'account_number': '0987654321',  # Số TK của bạn
    'account_name': 'HOANG TUAN',     # Tên của bạn (VIẾT HOA, không dấu)
}
```

**Ví dụ với VCB (Vietcombank):**
```python
return {
    'bank_code': 'VCB',
    'bank_name': 'Vietcombank',
    'account_number': '1234567890',
    'account_name': 'HOANG TUAN',
}
```

**Ví dụ với TCB (Techcombank):**
```python
return {
    'bank_code': 'TCB',
    'bank_name': 'Techcombank',
    'account_number': '9876543210',
    'account_name': 'HOANG TUAN',
}
```

### Danh sách mã ngân hàng phổ biến:

| Ngân hàng | Mã code |
|-----------|---------|
| Vietcombank | `VCB` |
| Techcombank | `TCB` |
| MB Bank | `MB` |
| VietinBank | `CTG` |
| BIDV | `BIDV` |
| ACB | `ACB` |
| TPBank | `TPB` |
| Sacombank | `STB` |
| VPBank | `VPB` |
| Agribank | `AGR` |

**⚠️ LƯU Ý:**
- `account_name` phải viết **HOA KHÔNG DẤU** (ví dụ: `NGUYEN VAN A`)
- `account_number` là số tài khoản thật của bạn
- `bank_code` phải đúng mã ngân hàng (xem bảng trên)

---

## 🧪 TEST LOCAL

### 1. Cài đặt dependencies:

```bash
cd license_server
pip install -r requirements.txt
```

### 2. Chạy server:

```bash
python app.py
```

### 3. Mở browser:

```
http://localhost:5000
```

### 4. Test luồng thanh toán:

1. Click **"Mua Ngay"**
2. Nhập email
3. Click **"Tạo Đơn Hàng"**
4. Xem mã QR xuất hiện ✅
5. Quét bằng app ngân hàng (hoặc screenshot để test)

---

## 🚀 DEPLOY LÊN RENDER

### 1. Push code lên Git:

```bash
git add .
git commit -m "feat: Add VietQR payment integration"
git push
```

### 2. Render sẽ tự động deploy

Render sẽ:
- ✅ Cài đặt `qrcode` và `Pillow` từ `requirements.txt`
- ✅ Deploy code mới
- ✅ Server sẽ chạy với VietQR

### 3. Test trên Production:

Vào: `https://ocr-uufr.onrender.com`

---

## 🎯 LUỒNG HOẠT ĐỘNG

```
1. Khách hàng vào website
   ↓
2. Click "Mua Ngay" → Nhập email
   ↓
3. Click "Tạo Đơn Hàng"
   ↓
4. Backend tạo VietQR URL với:
   - Số TK của bạn
   - Số tiền: 100,000đ
   - Nội dung: Email khách hàng
   ↓
5. QR code hiển thị trên trang
   ↓
6. Khách hàng quét QR bằng app ngân hàng
   ↓
7. App tự động điền:
   - Số TK nhận
   - Số tiền
   - Nội dung CK (email)
   ↓
8. Khách hàng chỉ cần nhấn "Xác nhận"
   ↓
9. Casso webhook nhận thông báo
   ↓
10. Tự động tạo license key + gửi email
```

---

## 📱 APP NGÂN HÀNG HỖ TRỢ VietQR

✅ Hầu hết các app ngân hàng VN đều hỗ trợ:
- MB Bank
- Vietcombank
- Techcombank
- VietinBank
- BIDV
- ACB
- TPBank
- VPBank
- Agribank
- Sacombank
- ...và hầu hết các ngân hàng khác

---

## 🎨 DEMO

### Trước đây:
```
❌ Khách hàng phải:
1. Copy số TK
2. Copy tên TK
3. Nhập số tiền
4. Gõ email vào nội dung
5. Xác nhận

→ Dễ sai sót!
```

### Bây giờ:
```
✅ Khách hàng chỉ cần:
1. Quét QR
2. Xác nhận

→ Siêu nhanh! Không sai sót!
```

---

## 🔥 LỢI ÍCH

1. **Tăng conversion rate**: Khách dễ dàng thanh toán hơn
2. **Giảm sai sót**: Không lo gõ sai nội dung CK
3. **Trải nghiệm tốt**: UI đẹp, hiện đại
4. **Tự động 100%**: Quét → Xác nhận → Nhận license

---

## 🛠️ CẦN HỖ TRỢ?

Nếu có vấn đề gì, hãy:
1. Check Render Logs
2. Test local trước
3. Verify thông tin bank code đúng

**Chúc bạn thành công!** 🎉

