# ====================================================================
# Script: Tạo Self-Signed Code Signing Certificate
# Mục đích: Ký file .exe để giảm cảnh báo Windows SmartScreen
# ====================================================================

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "🔐 TẠO SELF-SIGNED CERTIFICATE" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Thông tin công ty/người phát hành
$CompanyName = "OCR License System"
$SubjectName = "CN=$CompanyName"

# Kiểm tra quyền Admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  CẢNH BÁO: Script cần chạy với quyền Administrator" -ForegroundColor Yellow
    Write-Host "   Nhưng vẫn có thể tạo cert trong CurrentUser store" -ForegroundColor Yellow
    Write-Host ""
}

# Tạo Certificate
Write-Host "📝 Tạo certificate với tên: $CompanyName" -ForegroundColor Green

try {
    # Tạo cert trong CurrentUser\My (Personal) store
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject $SubjectName `
        -KeyUsage DigitalSignature `
        -FriendlyName "$CompanyName Code Signing Certificate" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
        -NotAfter (Get-Date).AddYears(3)
    
    Write-Host "✅ Certificate đã tạo thành công!" -ForegroundColor Green
    Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    Write-Host "   Subject: $($cert.Subject)" -ForegroundColor Gray
    Write-Host "   Valid until: $($cert.NotAfter)" -ForegroundColor Gray
    Write-Host ""
    
    # Export certificate to .pfx file (để backup hoặc dùng trên máy khác)
    $pfxPassword = ConvertTo-SecureString -String "OCR2024!" -Force -AsPlainText
    $pfxPath = ".\OCR_CodeSigning.pfx"
    
    Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pfxPassword | Out-Null
    
    Write-Host "💾 Đã export certificate sang file:" -ForegroundColor Green
    Write-Host "   File: $pfxPath" -ForegroundColor Gray
    Write-Host "   Password: OCR2024!" -ForegroundColor Gray
    Write-Host ""
    
    # Lưu thông tin cert
    $certInfo = @{
        Thumbprint = $cert.Thumbprint
        Subject = $cert.Subject
        NotAfter = $cert.NotAfter
        PfxFile = $pfxPath
        PfxPassword = "OCR2024!"
        CreatedAt = Get-Date
    } | ConvertTo-Json
    
    $certInfo | Out-File "cert_info.json" -Encoding UTF8
    
    Write-Host "📋 Thông tin certificate đã lưu vào: cert_info.json" -ForegroundColor Green
    Write-Host ""
    
    # Hướng dẫn sử dụng
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "📖 HƯỚNG DẪN SỬ DỤNG" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣  Ký file .exe:" -ForegroundColor Yellow
    Write-Host "   .\sign_exe.ps1 -ExePath 'dist\OCR.exe'" -ForegroundColor White
    Write-Host ""
    Write-Host "2️⃣  Build + Sign tự động:" -ForegroundColor Yellow
    Write-Host "   .\build_and_sign.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "3️⃣  Verify signature:" -ForegroundColor Yellow
    Write-Host "   Get-AuthenticodeSignature 'dist\OCR.exe'" -ForegroundColor White
    Write-Host ""
    
    Write-Host "⚠️  LƯU Ý:" -ForegroundColor Red
    Write-Host "   - Certificate này là SELF-SIGNED (tự ký)" -ForegroundColor Yellow
    Write-Host "   - Vẫn sẽ hiện 'Unknown Publisher' khi user chạy" -ForegroundColor Yellow
    Write-Host "   - Nhưng ít cảnh báo hơn file KHÔNG ký" -ForegroundColor Yellow
    Write-Host "   - Để loại bỏ hoàn toàn cảnh báo → Cần mua EV Certificate ($400/năm)" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "✅ HOÀN TẤT!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ LỖI: Không thể tạo certificate" -ForegroundColor Red
    Write-Host "   Chi tiết: $_" -ForegroundColor Red
    exit 1
}

