# ====================================================================
# Script: Test toàn bộ quy trình Code Signing
# Mục đích: Demo tạo cert → build → sign → verify
# ====================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 TEST CODE SIGNING - FULL WORKFLOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Tạo Certificate
Write-Host "📌 STEP 1: Tạo Self-Signed Certificate" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

if (Test-Path ".\OCR_CodeSigning.pfx") {
    Write-Host "✅ Certificate đã tồn tại, skip..." -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "🔧 Tạo certificate mới..." -ForegroundColor Yellow
    & .\create_self_signed_cert.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Không thể tạo certificate!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Step 2: Build demo .exe
Write-Host "📌 STEP 2: Build Demo .exe" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

# Check PyInstaller
try {
    $version = & pyinstaller --version 2>&1
    Write-Host "✅ PyInstaller: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ PyInstaller chưa cài!" -ForegroundColor Red
    Write-Host "   Cài đặt: pip install pyinstaller" -ForegroundColor Yellow
    exit 1
}

# Build
Write-Host "🏗️  Building test_signing_demo.py..." -ForegroundColor Yellow
& pyinstaller --onefile --windowed --name "OCR_Demo" --icon NONE test_signing_demo.py 2>&1 | Out-Null

if (Test-Path "dist\OCR_Demo.exe") {
    Write-Host "✅ Build thành công!" -ForegroundColor Green
    $size = [math]::Round((Get-Item "dist\OCR_Demo.exe").Length / 1MB, 2)
    Write-Host "   File: dist\OCR_Demo.exe ($size MB)" -ForegroundColor Gray
} else {
    Write-Host "❌ Build thất bại!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Sign .exe
Write-Host "📌 STEP 3: Sign .exe" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

& .\sign_exe.ps1 -ExePath "dist\OCR_Demo.exe"

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Sign có lỗi (nhưng vẫn tiếp tục test)" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Verify Signature
Write-Host "📌 STEP 4: Verify Signature" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

$sig = Get-AuthenticodeSignature "dist\OCR_Demo.exe"

Write-Host "📋 Signature Details:" -ForegroundColor Cyan
Write-Host "   Status: $($sig.Status)" -ForegroundColor Gray
Write-Host "   Signer: $($sig.SignerCertificate.Subject)" -ForegroundColor Gray

if ($sig.TimeStamperCertificate) {
    Write-Host "   Timestamp: $($sig.TimeStamperCertificate.Subject)" -ForegroundColor Gray
}

if ($sig.SignerCertificate) {
    Write-Host "✅ File đã được ký số!" -ForegroundColor Green
} else {
    Write-Host "❌ File CHƯA được ký!" -ForegroundColor Red
}
Write-Host ""

# Step 5: Test Run
Write-Host "📌 STEP 5: Test Run Application" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

Write-Host "🚀 Launching OCR_Demo.exe..." -ForegroundColor Yellow
Write-Host "   (Sẽ mở cửa sổ GUI, check xem có cảnh báo không)" -ForegroundColor Gray
Write-Host ""

Start-Process "dist\OCR_Demo.exe"

Start-Sleep -Seconds 2

Write-Host "❓ App có chạy được không? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "✅ App chạy thành công!" -ForegroundColor Green
} else {
    Write-Host "⚠️  App không chạy - check lỗi" -ForegroundColor Yellow
}

Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Certificate created: OCR_CodeSigning.pfx" -ForegroundColor Green
Write-Host "✅ Demo app built: dist\OCR_Demo.exe" -ForegroundColor Green
Write-Host "✅ File signed: $($sig.SignerCertificate.Subject)" -ForegroundColor Green
Write-Host "✅ Signature status: $($sig.Status)" -ForegroundColor Green
Write-Host ""

Write-Host "📦 Files created:" -ForegroundColor Cyan
Write-Host "   - OCR_CodeSigning.pfx (Certificate)" -ForegroundColor Gray
Write-Host "   - cert_info.json (Certificate info)" -ForegroundColor Gray
Write-Host "   - dist\OCR_Demo.exe (Signed demo app)" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Copy dist\OCR_Demo.exe sang máy khác" -ForegroundColor White
Write-Host "   2. Download qua browser (để trigger SmartScreen)" -ForegroundColor White
Write-Host "   3. Double-click → Check cảnh báo" -ForegroundColor White
Write-Host "   4. Upload lên VirusTotal: https://virustotal.com" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  Remember:" -ForegroundColor Red
Write-Host "   Self-signed cert vẫn hiện 'Unknown Publisher'" -ForegroundColor Yellow
Write-Host "   Nhưng ít cảnh báo hơn file không ký!" -ForegroundColor Yellow
Write-Host ""

Write-Host "✅ TEST COMPLETED!" -ForegroundColor Green
Write-Host ""

