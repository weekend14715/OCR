#!/usr/bin/env pwsh
# Test Email Production - Kiểm tra email sau khi setup hoàn tất

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  EMAIL PRODUCTION TEST - OCR LICENSE SERVER" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://ocr-uufr.onrender.com"

# ==============================================================================
# TEST 1: KIỂM TRA EMAIL CONFIG
# ==============================================================================

Write-Host "[1/3] Checking Email Configuration..." -ForegroundColor Yellow
Write-Host ""

try {
    $configResponse = Invoke-RestMethod -Uri "$baseUrl/api/debug/email-config" -Method GET
    
    if ($configResponse.status -like "*OK*") {
        Write-Host "  Status:   " -NoNewline -ForegroundColor White
        Write-Host $configResponse.status -ForegroundColor Green
        
        Write-Host "  Accounts: " -NoNewline -ForegroundColor White
        Write-Host $configResponse.accounts_count -ForegroundColor Green
        
        foreach ($acc in $configResponse.accounts) {
            Write-Host "    - Email: $($acc.email)" -ForegroundColor Gray
            Write-Host "      Password: " -NoNewline -ForegroundColor Gray
            if ($acc.has_password) {
                Write-Host "OK ($($acc.password_length) chars)" -ForegroundColor Green
            } else {
                Write-Host "MISSING!" -ForegroundColor Red
            }
            Write-Host "      Daily Limit: $($acc.daily_limit)" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "  OK - Email config loaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "  ERROR!" -ForegroundColor Red
        Write-Host "  Status: $($configResponse.status)" -ForegroundColor Red
        Write-Host "  Error: $($configResponse.error)" -ForegroundColor Red
        
        if ($configResponse.fix) {
            Write-Host ""
            Write-Host "  Fix: $($configResponse.fix)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "STOP - Please fix email config first!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAILED to connect to server!" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
# TEST 2: GUI EMAIL TEST
# ==============================================================================

Write-Host "[2/3] Sending Test Email..." -ForegroundColor Yellow
Write-Host ""

$testEmail = Read-Host "  Enter email to receive test (default: hoangtuan.th484@gmail.com)"
if ([string]::IsNullOrWhiteSpace($testEmail)) {
    $testEmail = "hoangtuan.th484@gmail.com"
}

Write-Host "  Sending to: $testEmail" -ForegroundColor Gray
Write-Host "  Please wait..." -ForegroundColor Gray
Write-Host ""

try {
    $emailBody = @{
        to_email = $testEmail
    } | ConvertTo-Json

    $emailResponse = Invoke-RestMethod -Uri "$baseUrl/api/debug/test-email" -Method POST -Body $emailBody -ContentType "application/json"
    
    if ($emailResponse.success) {
        Write-Host "  SUCCESS - Email sent!" -ForegroundColor Green
        Write-Host "    To:      $($emailResponse.to_email)" -ForegroundColor Green
        Write-Host "    Via:     $($emailResponse.account_used)" -ForegroundColor Green
        Write-Host "    Message: $($emailResponse.message)" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "  CHECK YOUR INBOX!" -ForegroundColor Yellow
        Write-Host "  (Check Spam folder if not found)" -ForegroundColor Gray
    } else {
        Write-Host "  FAILED to send email!" -ForegroundColor Red
        Write-Host "    Error: $($emailResponse.message)" -ForegroundColor Red
        
        if ($emailResponse.traceback) {
            Write-Host ""
            Write-Host "  Traceback:" -ForegroundColor Gray
            Write-Host $emailResponse.traceback -ForegroundColor DarkGray
        }
    }
} catch {
    Write-Host "  ERROR!" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
# TEST 3: GENERATE LICENSE + SEND EMAIL (ADMIN)
# ==============================================================================

Write-Host "[3/3] Test License Generation + Email (Admin)" -ForegroundColor Yellow
Write-Host ""

$testAdmin = Read-Host "  Do you want to test admin license generation? (y/N)"

if ($testAdmin -eq 'y' -or $testAdmin -eq 'Y') {
    Write-Host ""
    $adminKey = Read-Host "  Enter Admin API Key"
    
    if ([string]::IsNullOrWhiteSpace($adminKey)) {
        Write-Host "  Skipped (no API key provided)" -ForegroundColor Yellow
    } else {
        $licenseEmail = Read-Host "  Email for license (default: $testEmail)"
        if ([string]::IsNullOrWhiteSpace($licenseEmail)) {
            $licenseEmail = $testEmail
        }
        
        Write-Host ""
        Write-Host "  Creating license..." -ForegroundColor Gray
        
        try {
            $licenseBody = @{
                plan_type = "lifetime"
                quantity = 1
                email = $licenseEmail
            } | ConvertTo-Json
            
            $headers = @{
                "X-Admin-Key" = $adminKey
                "Content-Type" = "application/json"
            }
            
            $licenseResponse = Invoke-RestMethod -Uri "$baseUrl/api/admin/generate" -Method POST -Body $licenseBody -Headers $headers
            
            if ($licenseResponse.success) {
                Write-Host ""
                Write-Host "  LICENSE CREATED!" -ForegroundColor Green
                Write-Host "    Key:     $($licenseResponse.licenses[0])" -ForegroundColor Green
                Write-Host "    Plan:    $($licenseResponse.plan)" -ForegroundColor Green
                Write-Host "    Email:   $($licenseResponse.email)" -ForegroundColor Green
                
                if ($licenseResponse.email_sent) {
                    Write-Host "    Email:   SENT!" -ForegroundColor Green
                    Write-Host "    Via:     $($licenseResponse.email_result)" -ForegroundColor Green
                } else {
                    Write-Host "    Email:   NOT SENT" -ForegroundColor Yellow
                    if ($licenseResponse.email_result) {
                        Write-Host "    Reason:  $($licenseResponse.email_result)" -ForegroundColor Yellow
                    }
                }
            } else {
                Write-Host "  FAILED!" -ForegroundColor Red
                Write-Host "  Error: $($licenseResponse.error)" -ForegroundColor Red
            }
        } catch {
            Write-Host "  ERROR!" -ForegroundColor Red
            Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  Skipped" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TEST COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Check email inbox: $testEmail" -ForegroundColor White
Write-Host "  2. If email not received, check Spam folder" -ForegroundColor White
Write-Host "  3. If still not working, check Render logs" -ForegroundColor White
Write-Host ""

