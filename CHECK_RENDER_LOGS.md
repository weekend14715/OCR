# 🔍 Kiểm tra Render Logs

## Bước 1: Mở Render Dashboard
https://dashboard.render.com

## Bước 2: Vào Service `ocr-uufr`
Click vào service name

## Bước 3: Xem Logs tab
Click "Logs" ở menu bên trái

## Bước 4: Tìm các dòng log quan trọng

### ✅ Payment được tạo thành công:
```
[PayOS] Calling payment_requests.create()...
[PayOS] Response received: <class '...'>
[PayOS] ✅ Payment request created successfully!
[PayOS]    Payment ID: ...
[PayOS]    Checkout URL: https://pay.payos.vn/...
[PayOS]    QR Code: ✅ Present (length: 1000+)  ← QUAN TRỌNG!
```

### ❌ QR Code bị missing:
```
[PayOS]    QR Code: ❌ MISSING (length: 0)  ← VẤN ĐỀ Ở ĐÂY!
```

## Bước 5: Debug

### Nếu thấy "❌ MISSING":
PayOS API không trả về QR code → Có thể:
1. PayOS chưa hỗ trợ QR trong `payment_requests.create()`
2. Cần field/param đặc biệt để request QR
3. QR code ở field khác (không phải qrCode/qr_code)

### Nếu thấy "✅ Present":
QR code có ở backend nhưng frontend không nhận được → Kiểm tra:
1. Network tab trong Chrome DevTools
2. Response của `/api/payment/create-order`
3. JavaScript console có lỗi không

## Bước 6: Check Network trong Browser

1. Mở https://ocr-uufr.onrender.com
2. F12 → Network tab
3. Click "Tạo đơn hàng"
4. Xem request `/api/payment/create-order`:
   - Status: 200?
   - Response có `qr_code` field không?
   - `qr_code` value là gì? (URL? base64? empty string?)

## Bước 7: Check Console

1. F12 → Console tab
2. Có error nào không?
3. Check: `console.log('QR Code:', data.qr_code)`

---

## 🎯 Kế hoạch tiếp theo

### Nếu QR code = empty string trong logs:
→ PayOS API không trả về QR code
→ Cần dùng checkout_url và open trong tab mới
→ PayOS web UI sẽ hiển thị QR code

### Nếu QR code có dữ liệu:
→ Kiểm tra format (URL hay base64?)
→ Update frontend để hiển thị đúng format

