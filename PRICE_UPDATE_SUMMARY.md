# 📝 Tóm Tắt Thay Đổi Giá Gói Test

## 🎯 Mục Đích
Thay đổi giá gói Test từ **1,000₫** → **2,000₫**

## ✅ Các File Đã Thay Đổi

### 1. `license_server/payment_gateway.py`
**Thay đổi:** Cập nhật PRICING config
```python
PRICING = {
    'test': {
        'name': 'Test Plan (2,000đ)',  # Đổi từ 1,000đ
        'price': 2000,                  # Đổi từ 1000
        'duration_days': 1,
        'plan_type': 'test'
    },
    ...
}
```

### 2. `license_server/templates/index.html`

#### a) Hiển thị giá trên pricing card
```html
<div class="plan-price">2,000₫</div>  <!-- Đổi từ 1,000₫ -->
<button onclick="showPurchaseModal('test', '2,000₫')">
    🧪 Test Ngay - 2,000₫  <!-- Đổi từ 1,000₫ -->
</button>
```

#### b) Modal hiển thị động theo gói đã chọn
```javascript
function showPurchaseModal(plan, price) {
    // Hiển thị tên gói và giá tương ứng
    let planName = plan === 'test' ? 'Gói Test' : 'Gói Kích Hoạt Trọn Đời';
    modalText.innerHTML = `<strong>${planName}</strong><br>Giá: ${price}`;
    
    // Lưu plan type và price để dùng sau
    window.currentPlanType = plan;
    window.currentPlanPrice = price;
}
```

#### c) Số tiền chuyển khoản hiển thị động
```html
<!-- Thêm id="transferAmount" để update động -->
<div><strong>💰 Số tiền:</strong> 
    <span id="transferAmount">100,000₫</span>
</div>
```

#### d) Gửi đúng plan type và amount khi tạo order
```javascript
async function createOrder() {
    // Lấy plan type và price từ window
    const planType = window.currentPlanType || 'lifetime';
    const priceString = window.currentPlanPrice || '100,000₫';
    
    // Chuyển đổi price string thành số
    const amount = parseInt(priceString.replace(/[,₫]/g, ''));
    
    // Gửi request với plan type và amount đúng
    const response = await fetch('/api/payment/create-order', {
        method: 'POST',
        body: JSON.stringify({
            customer_email: email,
            plan_type: planType,  // 'test' hoặc 'lifetime'
            amount: amount        // 2000 hoặc 100000
        })
    });
    
    // Update số tiền hiển thị
    document.getElementById('transferAmount').innerText = window.currentPlanPrice;
}
```

### 3. `license_server/payos_handler.py`
**Thay đổi:** Default amount cho simulate endpoint
```python
def simulate_payment():
    """
    Example: {"orderCode": 123456, "amount": 2000}  # Đổi từ 10000
    """
    amount = test_data.get('amount', 2000)  # Đổi từ 10000
```

## 🎨 Cải Tiến Thêm

### ✨ Modal giờ hiển thị động theo gói đã chọn:

**Trước:**
- Modal luôn hiển thị "Gói Kích Hoạt Trọn Đời - 100,000₫"
- Số tiền chuyển khoản luôn là 100,000₫
- Không phân biệt gói Test và Lifetime

**Sau:**
- Modal hiển thị đúng tên gói: "Gói Test" hoặc "Gói Kích Hoạt Trọn Đời"
- Giá hiển thị đúng: 2,000₫ hoặc 100,000₫
- Số tiền chuyển khoản tự động update theo gói đã chọn
- Gửi đúng `plan_type` và `amount` đến server

## 🧪 Test

### Test Gói Test (2,000₫):
1. Mở trang web
2. Click "🧪 Test Ngay - 2,000₫"
3. Verify modal hiển thị:
   - Tên: "Gói Test"
   - Giá: "2,000₫"
4. Nhập email và tạo order
5. Verify số tiền chuyển khoản: "2,000₫"

### Test Gói Lifetime (100,000₫):
1. Click "🚀 Mua Ngay - Chỉ 100,000₫"
2. Verify modal hiển thị:
   - Tên: "Gói Kích Hoạt Trọn Đời"
   - Giá: "100,000₫"
3. Nhập email và tạo order
4. Verify số tiền chuyển khoản: "100,000₫"

## 📊 Bảng Giá Hiện Tại

| Gói | Giá | Thời Hạn | Mục Đích |
|-----|-----|----------|----------|
| **Test** | **2,000₫** | 1 ngày | Test hệ thống |
| Lifetime | 100,000₫ | Trọn đời | Sử dụng thực tế |

## ✅ Checklist Deploy

- [x] Update `payment_gateway.py` - PRICING config
- [x] Update `index.html` - Pricing card display
- [x] Update `index.html` - Button text
- [x] Update `index.html` - Modal dynamic display
- [x] Update `index.html` - Transfer amount dynamic
- [x] Update `index.html` - Create order with correct plan_type
- [x] Update `payos_handler.py` - Simulate default amount
- [ ] Commit changes
- [ ] Push to GitHub
- [ ] Deploy to Render
- [ ] Test trên production

## 🚀 Deploy Commands

```bash
# Commit changes
git add .
git commit -m "Update test plan price from 1,000₫ to 2,000₫ and fix modal dynamic pricing"

# Push to GitHub (auto deploy to Render)
git push origin main
```

## 🔍 Verify After Deploy

```bash
# Test API endpoint
curl https://ocr-uufr.onrender.com/api/health

# Open browser and test
# 1. Click "Test Ngay - 2,000₫"
# 2. Verify modal shows "Gói Test - 2,000₫"
# 3. Create order and verify transfer amount is 2,000₫
```

---

**Cập nhật:** 2025-10-23  
**Người thực hiện:** AI Assistant  
**Trạng thái:** ✅ Hoàn thành - Chờ deploy

