# PowerShell script để xóa hotkey đã lưu
# Vietnamese OCR Tool - Clear Saved Hotkey

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "        XOA PHIM TAT DA LUU" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Lấy đường dẫn thư mục config
$configDir = Join-Path $env:LOCALAPPDATA "VietnameseOCRTool"
$configFile = Join-Path $configDir "config.ini"

Write-Host "[INFO] Dang kiem tra thu muc config..." -ForegroundColor Blue

# Kiểm tra thư mục config
if (-not (Test-Path $configDir)) {
    Write-Host "[WARNING] Thu muc config khong ton tai: $configDir" -ForegroundColor Yellow
    Write-Host "[INFO] Co the ban chua su dung phim tat bao gio." -ForegroundColor Green
    Read-Host "Nhan Enter de thoat"
    exit 1
}

Write-Host "[OK] Tim thay thu muc config: $configDir" -ForegroundColor Green
Write-Host ""

# Kiểm tra file config.ini
if (-not (Test-Path $configFile)) {
    Write-Host "[WARNING] File config.ini khong ton tai: $configFile" -ForegroundColor Yellow
    Write-Host "[INFO] Co the ban chua luu phim tat bao gio." -ForegroundColor Green
    Read-Host "Nhan Enter de thoat"
    exit 1
}

Write-Host "[OK] Tim thay file config.ini" -ForegroundColor Green
Write-Host ""

# Hiển thị nội dung file config hiện tại
Write-Host "[INFO] Noi dung file config hien tai:" -ForegroundColor Blue
Write-Host "----------------------------------------" -ForegroundColor Gray
Get-Content $configFile -Encoding UTF8
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host ""

# Xác nhận xóa
$confirm = Read-Host "Ban co chac chan muon xoa phim tat da luu? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "[INFO] Huy bo thao tac." -ForegroundColor Yellow
    Read-Host "Nhan Enter de thoat"
    exit 0
}

Write-Host ""
Write-Host "[INFO] Dang xoa phim tat..." -ForegroundColor Blue

try {
    # Xóa file config.ini
    Remove-Item $configFile -Force
    Write-Host "[OK] Da xoa file config.ini thanh cong!" -ForegroundColor Green
    
    # Kiểm tra xem thư mục có còn file nào khác không
    $remainingFiles = Get-ChildItem $configDir -File | Where-Object { $_.Name -ne "config.ini" }
    
    if ($remainingFiles.Count -eq 0) {
        Write-Host "[INFO] Thu muc config da trong, dang xoa thu muc..." -ForegroundColor Blue
        Remove-Item $configDir -Force
        Write-Host "[OK] Da xoa thu muc config thanh cong!" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Thu muc config van con $($remainingFiles.Count) file khac, giu lai thu muc." -ForegroundColor Yellow
        Write-Host "Cac file con lai:" -ForegroundColor Gray
        $remainingFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
    }
    
} catch {
    Write-Host "[ERROR] Loi khi xoa: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Nhan Enter de thoat"
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] DA XOA PHIM TAT THANH CONG!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Cac thao tac da thuc hien:" -ForegroundColor Blue
Write-Host "- Xoa file config.ini chua phim tat" -ForegroundColor White
Write-Host "- Xoa thu muc config neu trong" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Lan chay tiep theo, ung dung se yeu cau chon phim tat moi." -ForegroundColor Green
Write-Host ""
Read-Host "Nhan Enter de thoat"
