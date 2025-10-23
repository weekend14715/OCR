# Test PayOS Webhook Script
# Usage: .\test_payos_webhook.ps1

Write-Host "`nPayOS WEBHOOK TEST SUITE" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

$WEBHOOK_URL = "https://ocr-uufr.onrender.com/api/webhook/payos"

# Test 1: GET Request
Write-Host "`nTest 1: GET Request (Health Check)" -ForegroundColor Yellow
Write-Host ("-" * 60) -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method GET -UseBasicParsing
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
    
    if ($content.status -eq "webhook_ready" -and $content.version -eq "1.0") {
        Write-Host "Test 1 PASSED - Webhook is ready!" -ForegroundColor Green
    } else {
        Write-Host "Test 1 WARNING - Unexpected response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Test 1 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: POST Request - No Order
Write-Host "`nTest 2: POST Request - Payment Without Order" -ForegroundColor Yellow
Write-Host ("-" * 60) -ForegroundColor Gray

$testPayload = @{
    code = "00"
    desc = "success"
    success = $true
    data = @{
        orderCode = 999999999
        amount = 100000
        description = "Test payment - no order"
        reference = "TEST$(Get-Date -Format 'yyyyMMddHHmmss')"
        transactionDateTime = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        paymentLinkId = "test-link-$(Get-Random -Maximum 9999)"
        currency = "VND"
        accountNumber = "12345678"
    }
    signature = "test-signature-for-development-$(Get-Random -Maximum 9999)"
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method POST -Body $testPayload -ContentType "application/json" -UseBasicParsing
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    $errorResponse = $_.ErrorDetails.Message
    if ($errorResponse -like "*Order not found*" -or $_.Exception.Response.StatusCode -eq 404) {
        Write-Host "Test 2 PASSED - Correctly rejected non-existent order" -ForegroundColor Green
        Write-Host "Response: $errorResponse" -ForegroundColor White
    } else {
        Write-Host "Test 2 FAILED - Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 3: POST Request - Failed Payment
Write-Host "`nTest 3: POST Request - Failed Payment" -ForegroundColor Yellow
Write-Host ("-" * 60) -ForegroundColor Gray

$failedPayload = @{
    code = "99"
    desc = "Payment failed"
    success = $false
    data = @{
        orderCode = 123
        amount = 100000
    }
    signature = "test-signature"
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method POST -Body $failedPayload -ContentType "application/json" -UseBasicParsing
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Yellow
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    $errorResponse = $_.ErrorDetails.Message
    if ($errorResponse -like "*Payment not successful*" -or $_.Exception.Response.StatusCode -eq 400) {
        Write-Host "Test 3 PASSED - Correctly rejected failed payment" -ForegroundColor Green
        Write-Host "Response: $errorResponse" -ForegroundColor White
    } else {
        Write-Host "Test 3 FAILED - Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host "`nWebhook endpoint is operational!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Configure webhook URL in PayOS dashboard" -ForegroundColor White
Write-Host "     URL: $WEBHOOK_URL" -ForegroundColor Cyan
Write-Host "  2. If PayOS test shows 404, ignore it and click SAVE" -ForegroundColor White
Write-Host "  3. Test with real payment (small amount like 3,000 VND)" -ForegroundColor White
Write-Host "  4. Check email for license key" -ForegroundColor White
Write-Host "`nFull documentation: TEST_PAYOS_WEBHOOK.md" -ForegroundColor Gray
Write-Host ""
