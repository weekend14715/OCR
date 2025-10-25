# ============================================
# Build và Ký Installer với Inno Setup
# ============================================
# Script tự động để tạo file cài đặt có chữ ký số

param(
    [string]$CertPassword = "",
    [switch]$SkipBuild = $false,
    [switch]$SkipSigning = $false
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Vietnamese OCR Tool - Installer Builder  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. Kiểm tra các công cụ cần thiết
# ============================================
Write-Host "[1/5] Kiểm tra công cụ..." -ForegroundColor Yellow

# Kiểm tra Inno Setup
$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $InnoSetupPath)) {
    Write-Host "❌ Không tìm thấy Inno Setup!" -ForegroundColor Red
    Write-Host "   Vui lòng tải và cài đặt từ: https://jrsoftware.org/isdl.php" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Inno Setup: OK" -ForegroundColor Green

# Kiểm tra SignTool
$SignToolPath = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
if (-not (Test-Path $SignToolPath)) {
    # Tìm SignTool trong các phiên bản khác
    $WindowsKitsPath = "C:\Program Files (x86)\Windows Kits\10\bin"
    if (Test-Path $WindowsKitsPath) {
        $SignToolPath = Get-ChildItem -Path $WindowsKitsPath -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue | 
                        Select-Object -First 1 -ExpandProperty FullName
    }
}

if (-not $SignToolPath -or -not (Test-Path $SignToolPath)) {
    Write-Host "❌ Không tìm thấy SignTool!" -ForegroundColor Red
    Write-Host "   SignTool là một phần của Windows SDK" -ForegroundColor Yellow
    Write-Host "   Tải từ: https://developer.microsoft.com/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    if (-not $SkipSigning) {
        exit 1
    }
} else {
    Write-Host "✓ SignTool: OK" -ForegroundColor Green
}

# Kiểm tra certificate
$CertPath = "MyCert.pfx"
if (-not (Test-Path $CertPath)) {
    Write-Host "⚠️  Không tìm thấy file certificate: $CertPath" -ForegroundColor Yellow
    Write-Host "   Bạn cần tạo certificate trước khi ký" -ForegroundColor Yellow
    if (-not $SkipSigning) {
        Write-Host ""
        $createCert = Read-Host "Bạn có muốn tạo self-signed certificate ngay bây giờ? (Y/N)"
        if ($createCert -eq "Y" -or $createCert -eq "y") {
            Write-Host ""
            Write-Host "Đang tạo self-signed certificate..." -ForegroundColor Cyan
            & ".\create_self_signed_cert.ps1"
            if (-not (Test-Path $CertPath)) {
                Write-Host "❌ Không thể tạo certificate!" -ForegroundColor Red
                exit 1
            }
        } else {
            exit 1
        }
    }
} else {
    Write-Host "✓ Certificate: OK" -ForegroundColor Green
}

Write-Host ""

# ============================================
# 2. Build ứng dụng bằng PyInstaller (nếu cần)
# ============================================
if (-not $SkipBuild) {
    Write-Host "[2/5] Build ứng dụng bằng PyInstaller..." -ForegroundColor Yellow
    
    if (-not (Test-Path "dist\ocr_tool\ocr_tool.exe")) {
        Write-Host "Đang build ứng dụng..." -ForegroundColor Cyan
        
        # Kiểm tra pyinstaller
        $pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
        if (-not $pyinstaller) {
            Write-Host "❌ PyInstaller chưa được cài đặt!" -ForegroundColor Red
            Write-Host "   Cài đặt bằng: pip install pyinstaller" -ForegroundColor Yellow
            exit 1
        }
        
        # Build với spec file nếu có
        if (Test-Path "ocr_tool.spec") {
            pyinstaller ocr_tool.spec --clean --noconfirm
        } else {
            pyinstaller --name "ocr_tool" `
                        --icon "app_icon.ico" `
                        --windowed `
                        --onedir `
                        --clean `
                        --noconfirm `
                        ocr_tool.py
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Build thất bại!" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✓ Build thành công" -ForegroundColor Green
} else {
    Write-Host "[2/5] Bỏ qua bước build (--SkipBuild)" -ForegroundColor Gray
}

Write-Host ""

# ============================================
# 3. Ký file EXE chính (trước khi đóng gói)
# ============================================
if (-not $SkipSigning) {
    Write-Host "[3/5] Ký file EXE chính..." -ForegroundColor Yellow
    
    $exePath = "dist\ocr_tool\ocr_tool.exe"
    if (Test-Path $exePath) {
        # Nhập mật khẩu certificate nếu chưa có
        if ([string]::IsNullOrEmpty($CertPassword)) {
            $securePassword = Read-Host "Nhập mật khẩu certificate" -AsSecureString
            $CertPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
        }
        
        Write-Host "Đang ký file: $exePath" -ForegroundColor Cyan
        
        & $SignToolPath sign `
            /f $CertPath `
            /p $CertPassword `
            /fd SHA256 `
            /tr http://timestamp.digicert.com `
            /td SHA256 `
            /d "Vietnamese OCR Tool" `
            /du "https://github.com/yourusername/vietnamese-ocr-tool" `
            $exePath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Ký EXE thành công" -ForegroundColor Green
        } else {
            Write-Host "❌ Ký EXE thất bại!" -ForegroundColor Red
            Write-Host "   Kiểm tra lại mật khẩu certificate" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "⚠️  Không tìm thấy file EXE: $exePath" -ForegroundColor Yellow
    }
} else {
    Write-Host "[3/5] Bỏ qua ký EXE (--SkipSigning)" -ForegroundColor Gray
}

Write-Host ""

# ============================================
# 4. Build Installer với Inno Setup
# ============================================
Write-Host "[4/5] Build Installer với Inno Setup..." -ForegroundColor Yellow

# Tạo thư mục Output nếu chưa có
if (-not (Test-Path "Output")) {
    New-Item -ItemType Directory -Path "Output" | Out-Null
}

# Build với Inno Setup
Write-Host "Đang tạo file cài đặt..." -ForegroundColor Cyan

if (-not $SkipSigning) {
    # Build với signing
    & $InnoSetupPath "setup.iss" /Ssigntool="$SignToolPath sign /f `"`$CertPath`" /p `"$CertPassword`" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /d `$qVietnamese OCR Tool Setup`$q /du `$qhttps://github.com/yourusername/vietnamese-ocr-tool`$q `$f"
} else {
    # Build không có signing
    & $InnoSetupPath "setup.iss"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build Installer thành công" -ForegroundColor Green
} else {
    Write-Host "❌ Build Installer thất bại!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# 5. Xác minh chữ ký
# ============================================
if (-not $SkipSigning) {
    Write-Host "[5/5] Xác minh chữ ký số..." -ForegroundColor Yellow
    
    # Tìm file setup vừa tạo
    $setupFile = Get-ChildItem -Path "Output" -Filter "VietnameseOCRTool_Setup*.exe" | 
                 Sort-Object LastWriteTime -Descending | 
                 Select-Object -First 1
    
    if ($setupFile) {
        Write-Host "Đang xác minh: $($setupFile.Name)" -ForegroundColor Cyan
        
        & $SignToolPath verify /pa /v $setupFile.FullName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Chữ ký hợp lệ!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Không thể xác minh chữ ký (có thể do self-signed cert)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "  ✓ HOÀN THÀNH!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "File cài đặt đã sẵn sàng:" -ForegroundColor Cyan
        Write-Host "  📦 $($setupFile.FullName)" -ForegroundColor White
        Write-Host "  📊 Kích thước: $([math]::Round($setupFile.Length / 1MB, 2)) MB" -ForegroundColor White
        Write-Host ""
        Write-Host "Bạn có thể phân phối file này cho người dùng!" -ForegroundColor Green
        Write-Host ""
        
        # Mở thư mục Output
        $openFolder = Read-Host "Mở thư mục Output? (Y/N)"
        if ($openFolder -eq "Y" -or $openFolder -eq "y") {
            explorer.exe "Output"
        }
    } else {
        Write-Host "⚠️  Không tìm thấy file setup trong thư mục Output" -ForegroundColor Yellow
    }
} else {
    Write-Host "[5/5] Bỏ qua xác minh chữ ký (--SkipSigning)" -ForegroundColor Gray
    
    # Tìm file setup
    $setupFile = Get-ChildItem -Path "Output" -Filter "VietnameseOCRTool_Setup*.exe" | 
                 Sort-Object LastWriteTime -Descending | 
                 Select-Object -First 1
    
    if ($setupFile) {
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "  ✓ HOÀN THÀNH (Không có chữ ký)" -ForegroundColor Yellow
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "File cài đặt:" -ForegroundColor Cyan
        Write-Host "  📦 $($setupFile.FullName)" -ForegroundColor White
        Write-Host "  📊 Kích thước: $([math]::Round($setupFile.Length / 1MB, 2)) MB" -ForegroundColor White
        Write-Host ""
        Write-Host "⚠️  File này CHƯA CÓ chữ ký số!" -ForegroundColor Yellow
        Write-Host ""
    }
}

