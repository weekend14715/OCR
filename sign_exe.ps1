# ====================================================================
# Script: Ký file .exe bằng Self-Signed Certificate
# Sử dụng: .\sign_exe.ps1 -ExePath "dist\OCR.exe"
# ====================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ExePath,
    
    [Parameter(Mandatory=$false)]
    [string]$PfxFile = ".\OCR_CodeSigning.pfx",
    
    [Parameter(Mandatory=$false)]
    [string]$PfxPassword = "OCR2024!"
)

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "🔐 KÝ FILE .EXE" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra file .exe có tồn tại không
if (-not (Test-Path $ExePath)) {
    Write-Host "❌ LỖI: Không tìm thấy file: $ExePath" -ForegroundColor Red
    exit 1
}

Write-Host "📂 File cần ký: $ExePath" -ForegroundColor Green
Write-Host "   Size: $((Get-Item $ExePath).Length / 1MB) MB" -ForegroundColor Gray
Write-Host ""

# Phương pháp 1: Dùng certificate từ .pfx file (ưu tiên)
if (Test-Path $PfxFile) {
    Write-Host "🔑 Sử dụng certificate từ file: $PfxFile" -ForegroundColor Green
    
    try {
        # Load .pfx file
        $certPassword = ConvertTo-SecureString -String $PfxPassword -Force -AsPlainText
        $cert = Get-PfxCertificate -FilePath $PfxFile -Password $certPassword
        
        Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
        Write-Host "   Subject: $($cert.Subject)" -ForegroundColor Gray
        Write-Host ""
        
        # Ký file
        Write-Host "✍️  Đang ký file..." -ForegroundColor Yellow
        
        $signature = Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
        
        if ($signature.Status -eq "Valid") {
            Write-Host "✅ KÝ THÀNH CÔNG!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 Thông tin chữ ký:" -ForegroundColor Cyan
            Write-Host "   Status: $($signature.Status)" -ForegroundColor Gray
            Write-Host "   Signer: $($signature.SignerCertificate.Subject)" -ForegroundColor Gray
            Write-Host "   Timestamp: $($signature.TimeStamperCertificate.Subject)" -ForegroundColor Gray
            Write-Host ""
            
            # Verify
            Write-Host "🔍 Verify chữ ký..." -ForegroundColor Yellow
            $verify = Get-AuthenticodeSignature -FilePath $ExePath
            
            if ($verify.Status -eq "Valid") {
                Write-Host "✅ Chữ ký hợp lệ!" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Status: $($verify.Status)" -ForegroundColor Yellow
                Write-Host "   (Self-signed cert sẽ hiện 'UnknownError' hoặc 'NotTrusted' - Điều này BÌnh THƯỜNG)" -ForegroundColor Gray
            }
            
        } else {
            Write-Host "❌ KÝ THẤT BẠI!" -ForegroundColor Red
            Write-Host "   Status: $($signature.Status)" -ForegroundColor Red
            Write-Host "   Message: $($signature.StatusMessage)" -ForegroundColor Red
            exit 1
        }
        
    } catch {
        Write-Host "❌ LỖI: $_" -ForegroundColor Red
        exit 1
    }
    
} else {
    # Phương pháp 2: Dùng certificate từ Windows Certificate Store
    Write-Host "⚠️  Không tìm thấy file .pfx: $PfxFile" -ForegroundColor Yellow
    Write-Host "🔍 Tìm certificate trong Windows Certificate Store..." -ForegroundColor Yellow
    
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like "*OCR*" } | Select-Object -First 1
    
    if ($cert) {
        Write-Host "✅ Tìm thấy certificate:" -ForegroundColor Green
        Write-Host "   Subject: $($cert.Subject)" -ForegroundColor Gray
        Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "✍️  Đang ký file..." -ForegroundColor Yellow
        
        $signature = Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
        
        if ($signature.Status -eq "Valid") {
            Write-Host "✅ KÝ THÀNH CÔNG!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Status: $($signature.Status)" -ForegroundColor Yellow
            Write-Host "   (Self-signed cert có thể hiện status khác 'Valid' nhưng vẫn work)" -ForegroundColor Gray
        }
        
    } else {
        Write-Host "❌ LỖI: Không tìm thấy certificate!" -ForegroundColor Red
        Write-Host "   Vui lòng chạy: .\create_self_signed_cert.ps1" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📖 TIẾP THEO" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Upload file lên VirusTotal để scan:" -ForegroundColor Yellow
Write-Host "   https://www.virustotal.com" -ForegroundColor White
Write-Host ""
Write-Host "2. Test file trên máy Windows khác" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Khi phát hành:" -ForegroundColor Yellow
Write-Host "   - Nén file .exe + cert_info.json vào .zip" -ForegroundColor White
Write-Host "   - Thêm README.txt hướng dẫn cài đặt" -ForegroundColor White
Write-Host ""
Write-Host "✅ HOÀN TẤT!" -ForegroundColor Green

