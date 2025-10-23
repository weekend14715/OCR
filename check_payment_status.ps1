#!/usr/bin/env pwsh
# =====================================================================
# CHECK PAYMENT STATUS - Debug Tool
# =====================================================================
# Kiểm tra trạng thái thanh toán và xem logs

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "   🔍 CHECK PAYMENT STATUS" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Lấy Order ID từ user
$OrderID = Read-Host "Nhập Order ID (VD: 123456789)"

if ([string]::IsNullOrWhiteSpace($OrderID)) {
    Write-Host "❌ Order ID không được để trống!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 Đang kiểm tra order: $OrderID..." -ForegroundColor Yellow
Write-Host ""

# API endpoint
$API_URL = "https://ocr-uufr.onrender.com/api/order/status/$OrderID"

try {
    $response = Invoke-RestMethod -Uri $API_URL -Method Get -ContentType "application/json"
    
    Write-Host "✅ TÌM THẤY ORDER!" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📋 ORDER DETAILS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Order ID:        " -NoNewline
    Write-Host $response.order_id -ForegroundColor White
    Write-Host "Plan Type:       " -NoNewline
    Write-Host $response.plan_type -ForegroundColor White
    Write-Host "Amount:          " -NoNewline
    Write-Host "$($response.amount) VND" -ForegroundColor Yellow
    Write-Host ""
    
    # Payment Status với màu
    Write-Host "Payment Status:  " -NoNewline
    if ($response.payment_status -eq "completed") {
        Write-Host "✅ COMPLETED" -ForegroundColor Green
    } elseif ($response.payment_status -eq "pending") {
        Write-Host "⏳ PENDING (Chưa thanh toán)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ $($response.payment_status)" -ForegroundColor Red
    }
    Write-Host ""
    
    # License Key
    if ($response.license_key) {
        Write-Host "License Key:     " -NoNewline
        Write-Host $response.license_key -ForegroundColor Green
    } else {
        Write-Host "License Key:     " -NoNewline
        Write-Host "(Chưa có - chưa thanh toán)" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Timestamps
    Write-Host "Created At:      $($response.created_at)" -ForegroundColor Gray
    if ($response.paid_at) {
        Write-Host "Paid At:         $($response.paid_at)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    
    # Kết luận
    if ($response.payment_status -eq "completed") {
        Write-Host "🎉 THANH TOÁN THÀNH CÔNG!" -ForegroundColor Green
        Write-Host ""
        Write-Host "✅ License key đã được tạo" -ForegroundColor Green
        Write-Host "✅ Email đã được gửi (nếu có cấu hình email)" -ForegroundColor Green
        Write-Host ""
    } elseif ($response.payment_status -eq "pending") {
        Write-Host "⏳ CHƯA THANH TOÁN" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Có thể do:" -ForegroundColor Yellow
        Write-Host "  1. User chưa scan QR và thanh toán" -ForegroundColor Gray
        Write-Host "  2. PayOS webhook chưa được cấu hình" -ForegroundColor Gray
        Write-Host "  3. Webhook bị lỗi (xem logs trên Render)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "👉 Hướng dẫn:" -ForegroundColor Cyan
        Write-Host "  - Kiểm tra PayOS Dashboard xem giao dịch có status gì" -ForegroundColor Gray
        Write-Host "  - Kiểm tra Render logs: https://dashboard.render.com" -ForegroundColor Gray
        Write-Host "  - Verify webhook URL: https://ocr-uufr.onrender.com/payos/webhook" -ForegroundColor Gray
        Write-Host ""
    }
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($statusCode -eq 404) {
        Write-Host "❌ KHÔNG TÌM THẤY ORDER!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Order ID '$OrderID' không tồn tại trong database." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Kiểm tra lại:" -ForegroundColor Cyan
        Write-Host "  1. Order ID có đúng không?" -ForegroundColor Gray
        Write-Host "  2. Order có được tạo thành công không?" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "❌ LỖI: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

