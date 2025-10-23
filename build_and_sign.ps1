# ====================================================================
# Script: Build .exe bằng PyInstaller và tự động ký
# Sử dụng: .\build_and_sign.ps1
# ====================================================================

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "🚀 BUILD & SIGN OCR APPLICATION" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra PyInstaller
Write-Host "🔍 Kiểm tra PyInstaller..." -ForegroundColor Yellow

try {
    $pyinstallerVersion = & pyinstaller --version 2>&1
    Write-Host "✅ PyInstaller: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PyInstaller chưa cài đặt!" -ForegroundColor Red
    Write-Host "   Cài đặt: pip install pyinstaller" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Kiểm tra certificate
Write-Host "🔍 Kiểm tra certificate..." -ForegroundColor Yellow

$pfxFile = ".\OCR_CodeSigning.pfx"
if (-not (Test-Path $pfxFile)) {
    Write-Host "⚠️  Chưa có certificate!" -ForegroundColor Yellow
    Write-Host "📝 Tạo certificate..." -ForegroundColor Yellow
    
    & .\create_self_signed_cert.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Không thể tạo certificate!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Certificate có sẵn" -ForegroundColor Green
Write-Host ""

# Build .exe
Write-Host "🏗️  Build .exe bằng PyInstaller..." -ForegroundColor Yellow
Write-Host ""

# Tìm file main Python (có thể là main.py, app.py, OCR.py, etc.)
$mainFile = $null
$possibleFiles = @("main.py", "OCR.py", "app.py", "gui.py")

foreach ($file in $possibleFiles) {
    if (Test-Path $file) {
        $mainFile = $file
        break
    }
}

if (-not $mainFile) {
    Write-Host "❌ Không tìm thấy file Python chính!" -ForegroundColor Red
    Write-Host "   Vui lòng chỉ định file: .\build_and_sign.ps1 -MainFile 'your_script.py'" -ForegroundColor Yellow
    exit 1
}

Write-Host "📂 Main file: $mainFile" -ForegroundColor Green

# Build command
$buildCmd = "pyinstaller --onefile --windowed --name OCR $mainFile"

Write-Host "   Command: $buildCmd" -ForegroundColor Gray
Write-Host ""

try {
    Invoke-Expression $buildCmd
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build thất bại!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Build thành công!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ LỖI: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Ký file .exe
$exePath = ".\dist\OCR.exe"

if (Test-Path $exePath) {
    Write-Host "🔐 Ký file .exe..." -ForegroundColor Yellow
    Write-Host ""
    
    & .\sign_exe.ps1 -ExePath $exePath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Không thể ký file (nhưng .exe vẫn có thể dùng)" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ Không tìm thấy file .exe: $exePath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "✅ HOÀN TẤT!" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📦 File .exe đã sẵn sàng:" -ForegroundColor Green
Write-Host "   $exePath" -ForegroundColor White
Write-Host ""
Write-Host "📊 Thông tin file:" -ForegroundColor Cyan
$exeInfo = Get-Item $exePath
Write-Host "   Size: $([math]::Round($exeInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host "   Modified: $($exeInfo.LastWriteTime)" -ForegroundColor Gray

# Verify signature
$sig = Get-AuthenticodeSignature $exePath
Write-Host "   Signature: $($sig.Status)" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 TIẾP THEO:" -ForegroundColor Yellow
Write-Host "   1. Test file: .\dist\OCR.exe" -ForegroundColor White
Write-Host "   2. Upload lên VirusTotal: https://www.virustotal.com" -ForegroundColor White
Write-Host "   3. Phát hành cho users!" -ForegroundColor White
Write-Host ""

