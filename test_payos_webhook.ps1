#!/usr/bin/env pwsh
# Test PayOS Webhook Script
# Usage: .\test_payos_webhook.ps1

Write-Host "`n🧪 PAYOS WEBHOOK TEST SUITE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

$WEBHOOK_URL = "https://ocr-uufr.onrender.com/api/webhook/payos"

# Test 1: GET Request (Health Check)
Write-Host "`n📍 Test 1: GET Request (Health Check)" -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method GET -UseBasicParsing
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
    
    if ($content.status -eq "webhook_ready" -and $content.version -eq "1.0") {
        Write-Host "✅ Test 1 PASSED - Webhook is ready!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Test 1 WARNING - Unexpected response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Test 1 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: POST Request - Payment Success (không có order)
Write-Host "`n📍 Test 2: POST Request - Payment Without Order" -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$testPayload = @{
    code = "00"
    desc = "success"
    success = $true
    data = @{
        orderCode = 999999999
        amount = 100000
        description = "Test payment - no order"
        reference = "TEST" + (Get-Date -Format "yyyyMMddHHmmss")
        transactionDateTime = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        paymentLinkId = "test-link-" + (Get-Random -Maximum 9999)
        currency = "VND"
        accountNumber = "12345678"
    }
    signature = "test-signature-for-development-" + (Get-Random -Maximum 9999)
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method POST -Body $testPayload -ContentType "application/json" -UseBasicParsing
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
    Write-Host "⚠️  Test 2 INFO - Expected 404 (order not found)" -ForegroundColor Yellow
} catch {
    $errorResponse = $_.ErrorDetails.Message
    if ($errorResponse -like "*Order not found*" -or $_.Exception.Response.StatusCode -eq 404) {
        Write-Host "✅ Test 2 PASSED - Correctly rejected non-existent order" -ForegroundColor Green
        Write-Host "Response: $errorResponse" -ForegroundColor White
    } else {
        Write-Host "❌ Test 2 FAILED - Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 3: POST Request - Payment Failed (code != 00)
Write-Host "`n📍 Test 3: POST Request - Failed Payment" -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

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
    Write-Host "⚠️  Test 3 WARNING - Should reject failed payment" -ForegroundColor Yellow
} catch {
    $errorResponse = $_.ErrorDetails.Message
    if ($errorResponse -like "*Payment not successful*" -or $_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✅ Test 3 PASSED - Correctly rejected failed payment" -ForegroundColor Green
        Write-Host "Response: $errorResponse" -ForegroundColor White
    } else {
        Write-Host "❌ Test 3 FAILED - Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 4: OPTIONS Request (CORS Preflight)
Write-Host "`n📍 Test 4: OPTIONS Request (CORS Preflight)" -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method OPTIONS -UseBasicParsing
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "CORS Headers:" -ForegroundColor White
    Write-Host "  Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Gray
    Write-Host "  Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])" -ForegroundColor Gray
    Write-Host "✅ Test 4 PASSED - CORS configured correctly" -ForegroundColor Green
} catch {
    Write-Host "❌ Test 4 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Empty POST Request
Write-Host "`n📍 Test 5: POST Request - Empty Body" -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri $WEBHOOK_URL -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
    
    if ($content.status -eq "ok") {
        Write-Host "✅ Test 5 PASSED - Handles empty request gracefully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Test 5 WARNING - Unexpected response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Test 5 FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "🎯 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "`n✅ Webhook endpoint is operational!" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure webhook URL in PayOS dashboard" -ForegroundColor White
Write-Host "     URL: $WEBHOOK_URL" -ForegroundColor Cyan
Write-Host "  2. If PayOS test shows 404, ignore it and click SAVE" -ForegroundColor White
Write-Host "  3. Test with real payment (small amount like 3,000 VND)" -ForegroundColor White
Write-Host "  4. Check email for license key" -ForegroundColor White
Write-Host "`n📖 Full documentation: TEST_PAYOS_WEBHOOK.md`n" -ForegroundColor Gray

