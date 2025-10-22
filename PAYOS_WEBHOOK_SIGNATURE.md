# 🔐 PayOS Webhook Signature Verification

## ⚠️ HIỆN TRẠNG
Hiện tại đã **TẮT signature verification TẠM THỜI** để test webhook hoạt động.

## 🎯 CÁCH THÊM SIGNATURE VERIFICATION SAU NÀY

### Bước 1: Tìm Webhook Signature Key trong PayOS

1. Đăng nhập https://my.payos.vn
2. Chọn merchant **OCR Vietnamese**
3. Vào **Thiết lập nâng cao**
4. Tìm **Webhook Signature Key** (hoặc **Checksum Key**)
5. Copy key này

### Bước 2: Thêm vào biến môi trường Render

1. Vào Render Dashboard → Service **ocr-uufr**
2. Vào **Environment** tab
3. Thêm biến mới:
   - **Key:** `PAYOS_CHECKSUM_KEY`
   - **Value:** [key từ bước 1]
4. Save Changes (Render sẽ tự động deploy lại)

### Bước 3: Thêm code verify signature

Thêm hàm verify vào `license_server/app.py`:

```python
import hmac
import hashlib

def verify_webhook_signature(data, signature):
    """
    Verify PayOS webhook signature
    
    Args:
        data: Dict - webhook data payload
        signature: str - signature từ PayOS
    
    Returns:
        bool: True nếu signature hợp lệ
    """
    checksum_key = os.getenv('PAYOS_CHECKSUM_KEY')
    if not checksum_key:
        print("⚠️ PAYOS_CHECKSUM_KEY not configured")
        return True  # Skip verification if not configured
    
    # Tạo string để sign theo thứ tự của PayOS
    # Format: amount={amount}&cancelUrl={cancelUrl}&description={description}&orderCode={orderCode}&returnUrl={returnUrl}
    
    # Lấy các field cần thiết
    amount = data.get('amount', '')
    cancel_url = data.get('cancelUrl', '')
    description = data.get('description', '')
    order_code = data.get('orderCode', '')
    return_url = data.get('returnUrl', '')
    
    # Tạo data string theo format của PayOS
    data_str = f"amount={amount}&cancelUrl={cancel_url}&description={description}&orderCode={order_code}&returnUrl={return_url}"
    
    # Tạo HMAC SHA256
    computed_signature = hmac.new(
        checksum_key.encode('utf-8'),
        data_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # So sánh signatures
    is_valid = hmac.compare_digest(computed_signature, signature)
    
    if not is_valid:
        print(f"❌ Signature mismatch:")
        print(f"   Expected: {computed_signature}")
        print(f"   Received: {signature}")
        print(f"   Data string: {data_str}")
    
    return is_valid
```

### Bước 4: Bật lại verification

Sửa lại code trong webhook handler:

```python
# Verify signature (QUAN TRỌNG: bảo vệ khỏi fake webhooks)
if signature and not verify_webhook_signature(data.get('data', {}), signature):
    print("⚠️ Invalid signature")
    return jsonify({'error': 'Invalid signature'}), 401
```

## 📚 TÀI LIỆU THAM KHẢO

- PayOS Webhook Documentation: https://payos.vn/docs/webhook
- PayOS Signature Guide: https://payos.vn/docs/webhook/signature

## ⚡ LƯU Ý

- **KHÔNG BAO GIỜ** commit `PAYOS_CHECKSUM_KEY` vào Git
- Chỉ lưu trong biến môi trường Render
- Signature verification là **BẮT BUỘC** khi production
- Hiện tại chỉ tắt để test, phải bật lại sau!

## 🧪 CÁCH TEST

1. Deploy code có hàm verify
2. Tạo thanh toán test trong PayOS
3. Kiểm tra logs trong Render để xem signature có match không
4. Nếu không match, kiểm tra lại format của data string

---

**Status:** ⚠️ Signature verification hiện đang TẮT - cần bật lại sau khi test xong!

