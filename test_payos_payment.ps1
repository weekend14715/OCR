# Test PayOS Payment Creation
# Sử dụng script này để test tạo payment link PayOS

$API_URL = "http://localhost:5000"  # Hoặc URL server của bạn

Write-Host "=== TEST PAYOS PAYMENT ===" -ForegroundColor Green
Write-Host ""

# Test 1: Tạo payment link cho license 1 tháng
Write-Host "1. Tạo payment link cho license 1 tháng (50,000 VND)..." -ForegroundColor Yellow
$body = @{
    email = "test@example.com"
    license_type = "1_month"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/payment/payos/create" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✓ Thành công!" -ForegroundColor Green
    Write-Host "  Payment Link: $($response.checkoutUrl)" -ForegroundColor Cyan
    Write-Host "  QR Code: $($response.qrCode)" -ForegroundColor Cyan
    Write-Host "  Order Code: $($response.orderCode)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Mở link này để thanh toán:" -ForegroundColor Yellow
    Write-Host "$($response.checkoutUrl)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "✗ Lỗi: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Nhấn Enter để test thêm gói khác..." -ForegroundColor Gray
Read-Host

# Test 2: Tạo payment link cho license 6 tháng
Write-Host "2. Tạo payment link cho license 6 tháng (150,000 VND)..." -ForegroundColor Yellow
$body = @{
    email = "test@example.com"
    license_type = "6_months"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/payment/payos/create" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✓ Thành công!" -ForegroundColor Green
    Write-Host "  Payment Link: $($response.checkoutUrl)" -ForegroundColor Cyan
    Write-Host "  QR Code: $($response.qrCode)" -ForegroundColor Cyan
    Write-Host "  Order Code: $($response.orderCode)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Mở link này để thanh toán:" -ForegroundColor Yellow
    Write-Host "$($response.checkoutUrl)" -ForegroundColor White
} catch {
    Write-Host "✗ Lỗi: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== HƯỚNG DẪN TEST ===" -ForegroundColor Green
Write-Host "1. Copy payment link ở trên" -ForegroundColor White
Write-Host "2. Mở trong browser" -ForegroundColor White
Write-Host "3. Quét QR code bằng app ngân hàng" -ForegroundColor White
Write-Host "4. Hoặc dùng tài khoản test PayOS (nếu có)" -ForegroundColor White
Write-Host ""
Write-Host "Sau khi thanh toán:" -ForegroundColor Yellow
Write-Host "- Webhook sẽ tự động nhận thông báo" -ForegroundColor White
Write-Host "- License sẽ được tạo và gửi qua email" -ForegroundColor White
Write-Host ""
