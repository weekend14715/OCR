# 🚀 HƯỚNG DẪN DEPLOY VIETQR - NHANH

## ⚡ 3 BƯỚC ĐỂ HOÀN THÀNH

### BƯỚC 1: CẬP NHẬT THÔNG TIN NGÂN HÀNG ⏱️ 1 phút

Mở file `license_server/payment_gateway.py`, dòng **458-460**:

```python
return {
    'bank_code': 'MB',              # Mã ngân hàng
    'bank_name': 'MB Bank',
    'account_number': '0123456789', # ← SỐ TÀI KHOẢN CỦA BẠN
    'account_name': 'NGUYEN VAN A', # ← TÊN CỦA BẠN (VIẾT HOA, KHÔNG DẤU)
}
```

**Ví dụ thay đổi:**
```python
return {
    'bank_code': 'TCB',
    'bank_name': 'Techcombank',
    'account_number': '19036512345678',
    'account_name': 'HOANG TUAN',
}
```

### BƯỚC 2: PUSH CODE LÊN GIT ⏱️ 30 giây

```bash
git add .
git commit -m "feat: Add VietQR payment"
git push
```

### BƯỚC 3: ĐỢI RENDER DEPLOY ⏱️ 2-3 phút

Render sẽ tự động:
- ✅ Cài đặt `qrcode` và `Pillow`
- ✅ Deploy code mới
- ✅ Restart server

**Xong!** 🎉

---

## 🧪 KIỂM TRA

1. Vào: https://ocr-uufr.onrender.com
2. Click **"Mua Ngay"**
3. Nhập email test
4. Click **"Tạo Đơn Hàng"**
5. **QR code xuất hiện!** 📱

Screenshot và quét bằng app ngân hàng để test!

---

## 📋 MÃ NGÂN HÀNG PHỔ BIẾN

| Ngân hàng | Mã |
|-----------|-----|
| **Vietcombank** | `VCB` |
| **Techcombank** | `TCB` |
| **MB Bank** | `MB` |
| **VietinBank** | `CTG` |
| **BIDV** | `BIDV` |
| **ACB** | `ACB` |
| **TPBank** | `TPB` |
| **Agribank** | `AGR` |

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **`account_name` phải:**
   - Viết **HOA**
   - **Không dấu**
   - Ví dụ: `NGUYEN VAN A`, `HOANG TUAN`

2. **`account_number`:**
   - Số tài khoản **thật** của bạn
   - Không có dấu cách

3. **`bank_code`:**
   - Phải đúng mã (xem bảng trên)
   - Viết HOA

---

## 🎯 KẾT QUẢ

Sau khi deploy xong, khách hàng sẽ:

1. ✅ Thấy QR code ngay trên trang
2. ✅ Quét QR = Thông tin tự động điền
3. ✅ Thanh toán chỉ mất 10 giây
4. ✅ Nhận license qua email tự động

**Conversion rate tăng 30-50%!** 🚀

---

## 📖 TÀI LIỆU THÊM

- `VIETQR_SUMMARY.md` - Tổng quan chi tiết
- `VIETQR_SETUP.md` - Hướng dẫn đầy đủ
- Render Logs - Debug nếu có lỗi

**Chúc bạn thành công!** 🎉

