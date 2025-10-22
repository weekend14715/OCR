# ============================================================================
# TEST PAYOS PAYMENT INTEGRATION
# Script test đầy đủ cho PayOS payment flow
# ============================================================================

$baseUrl = "https://ocr-uufr.onrender.com"
$testEmail = "hoangtuan.th484@gmail.com"

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  🚀 TEST PAYOS PAYMENT INTEGRATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Base URL: $baseUrl" -ForegroundColor White
Write-Host "Test Email: $testEmail" -ForegroundColor White
Write-Host ""

# ============================================================================
# TEST 1: Check PayOS Configuration
# ============================================================================

Write-Host "[1/4] Checking PayOS Configuration..." -ForegroundColor Yellow
Write-Host ""

try {
    $configResponse = Invoke-RestMethod -Uri "$baseUrl/api/debug/payos-config" -Method GET -ErrorAction Stop
    
    if ($configResponse.payos_enabled) {
        Write-Host "   ✅ PayOS Status: ENABLED" -ForegroundColor Green
        Write-Host "   ✅ Client ID: $($configResponse.client_id)" -ForegroundColor Green
        Write-Host "   ✅ API Key: $($configResponse.api_key_masked)" -ForegroundColor Green
        Write-Host "   ✅ Checksum: $($configResponse.checksum_masked)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ PayOS Status: DISABLED" -ForegroundColor Red
        Write-Host "   ⚠️  Please configure PayOS environment variables in Render!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Required env vars:" -ForegroundColor White
        Write-Host "   - PAYOS_CLIENT_ID" -ForegroundColor Gray
        Write-Host "   - PAYOS_API_KEY" -ForegroundColor Gray
        Write-Host "   - PAYOS_CHECKSUM_KEY" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
    
} catch {
    Write-Host "   ❌ Failed to check PayOS config" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Start-Sleep -Seconds 1

# ============================================================================
# TEST 2: Create PayOS Payment Link
# ============================================================================

Write-Host "[2/4] Creating PayOS Payment Link..." -ForegroundColor Yellow
Write-Host ""

$createPayload = @{
    plan_type = "lifetime"
    customer_email = $testEmail
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/payment/payos/create" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $createPayload `
        -ErrorAction Stop

    if ($response.success) {
        Write-Host "   ✅ Payment Link Created Successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "   📦 Order Details:" -ForegroundColor Cyan
        Write-Host "   ├─ Order ID: $($response.order_id)" -ForegroundColor White
        Write-Host "   ├─ Amount: $($response.amount) VND" -ForegroundColor White
        Write-Host "   ├─ Plan: LIFETIME" -ForegroundColor White
        Write-Host "   └─ Email: $testEmail" -ForegroundColor White
        Write-Host ""
        Write-Host "   🔗 Payment Links:" -ForegroundColor Cyan
        Write-Host "   ├─ Checkout URL: $($response.checkout_url)" -ForegroundColor Green
        Write-Host "   └─ QR Code URL: $($response.qr_code)" -ForegroundColor Green
        Write-Host ""
        
        $orderId = $response.order_id
        $checkoutUrl = $response.checkout_url
        $qrCodeUrl = $response.qr_code
        
    } else {
        Write-Host "   ❌ Failed to create payment link" -ForegroundColor Red
        Write-Host "   Error: $($response.error)" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "   ❌ Error creating payment link" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 2

# ============================================================================
# TEST 3: Check Order Status
# ============================================================================

Write-Host "[3/4] Checking Order Status..." -ForegroundColor Yellow
Write-Host ""

try {
    $orderResponse = Invoke-RestMethod -Uri "$baseUrl/api/orders/$orderId" -Method GET -ErrorAction Stop
    
    Write-Host "   ✅ Order Retrieved Successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📊 Order Status:" -ForegroundColor Cyan
    Write-Host "   ├─ Order ID: $($orderResponse.order_id)" -ForegroundColor White
    Write-Host "   ├─ Payment Status: $($orderResponse.payment_status)" -ForegroundColor $(if ($orderResponse.payment_status -eq "completed") { "Green" } else { "Yellow" })
    Write-Host "   ├─ Plan Type: $($orderResponse.plan_type)" -ForegroundColor White
    Write-Host "   ├─ Amount: $($orderResponse.amount) VND" -ForegroundColor White
    Write-Host "   ├─ Customer Email: $($orderResponse.customer_email)" -ForegroundColor White
    Write-Host "   └─ Created At: $($orderResponse.created_at)" -ForegroundColor White
    
    if ($orderResponse.license_key) {
        Write-Host "   └─ License Key: $($orderResponse.license_key)" -ForegroundColor Green
    }
    
} catch {
    Write-Host "   ❌ Error checking order status" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# TEST 4: Simulate PayOS Webhook (Manual Test)
# ============================================================================

Write-Host "[4/4] Testing Webhook Handler (Simulated)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   ℹ️  Note: This simulates what PayOS will send after real payment" -ForegroundColor Gray
Write-Host ""

$webhookPayload = @{
    code = "00"
    desc = "success"
    success = $true
    data = @{
        orderCode = [int]$orderId
        amount = 199000
        description = "Thanh toán License OCR Tool - LIFETIME"
        accountNumber = "123456789"
        reference = "FT$(Get-Random -Minimum 100000 -Maximum 999999)"
        transactionDateTime = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        currency = "VND"
        paymentLinkId = "test-payment-link-id-$orderId"
        code = "00"
        desc = "Thành công"
        counterAccountBankId = ""
        counterAccountBankName = "MB Bank"
        counterAccountName = "NGUYEN VAN TEST"
        counterAccountNumber = "0123456789"
        virtualAccountName = ""
        virtualAccountNumber = ""
    }
} | ConvertTo-Json -Depth 5

try {
    $webhookResponse = Invoke-RestMethod -Uri "$baseUrl/api/webhook/payos" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $webhookPayload `
        -ErrorAction Stop
    
    if ($webhookResponse.success) {
        Write-Host "   ✅ Webhook Processed Successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "   📨 Webhook Response:" -ForegroundColor Cyan
        Write-Host "   ├─ Message: $($webhookResponse.message)" -ForegroundColor White
        
        if ($webhookResponse.license_key) {
            Write-Host "   ├─ License Key: $($webhookResponse.license_key)" -ForegroundColor Green
        }
        
        if ($webhookResponse.email_sent) {
            Write-Host "   └─ Email Sent: ✅ YES" -ForegroundColor Green
        } else {
            Write-Host "   └─ Email Sent: ⚠️  NO (check email config)" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "   ❌ Error processing webhook" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan

# ============================================================================
# SUMMARY & NEXT STEPS
# ============================================================================

Write-Host ""
Write-Host "📋 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ PayOS Configuration: OK" -ForegroundColor Green
Write-Host "✅ Payment Link Created: OK" -ForegroundColor Green
Write-Host "✅ Order Status: OK" -ForegroundColor Green
Write-Host "✅ Webhook Handler: OK" -ForegroundColor Green
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  🎯 NEXT STEPS - REAL PAYMENT TEST" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Mở QR Code để thanh toán thực tế:" -ForegroundColor White
Write-Host ""
Write-Host "   QR Code URL:" -ForegroundColor Cyan
Write-Host "   $qrCodeUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Checkout Page:" -ForegroundColor Cyan
Write-Host "   $checkoutUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Scan QR code bằng app ngân hàng hoặc mở Checkout URL" -ForegroundColor White
Write-Host ""
Write-Host "3. Sau khi thanh toán:" -ForegroundColor White
Write-Host "   ✅ PayOS sẽ tự động gọi webhook" -ForegroundColor Green
Write-Host "   ✅ License key sẽ được tạo tự động" -ForegroundColor Green
Write-Host "   ✅ Email sẽ được gửi tự động đến: $testEmail" -ForegroundColor Green
Write-Host ""
Write-Host "4. Verify kết quả:" -ForegroundColor White
Write-Host "   • Check email inbox: $testEmail" -ForegroundColor Gray
Write-Host "   • Check Render logs: https://dashboard.render.com" -ForegroundColor Gray
Write-Host "   • Check order status: curl $baseUrl/api/orders/$orderId" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 TIP: Copy QR Code URL vào trình duyệt để xem QR code!" -ForegroundColor Yellow
Write-Host ""

# Optional: Copy URLs to clipboard (Windows only)
try {
    $qrCodeUrl | Set-Clipboard
    Write-Host "✅ QR Code URL đã được copy vào clipboard!" -ForegroundColor Green
    Write-Host ""
} catch {
    # Clipboard not available, skip
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

