# PowerShell Script để thêm Windows Defender Exclusion
# Chạy với quyền Administrator!

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Add Windows Defender Exclusion for OCR Project        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra quyền Admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: Script này cần chạy với quyền Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Cách chạy:" -ForegroundColor Yellow
    Write-Host "  1. Mở PowerShell AS ADMINISTRATOR" -ForegroundColor Yellow
    Write-Host "  2. cd F:\OCR\OCR" -ForegroundColor Yellow
    Write-Host "  3. .\Add_Exclusion_Admin.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Hoặc:" -ForegroundColor Yellow
    Write-Host "  - Chuột phải vào file Add_Exclusion_Admin.ps1" -ForegroundColor Yellow
    Write-Host "  - Chọn 'Run with PowerShell' (as Administrator)" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Có quyền Administrator!" -ForegroundColor Green
Write-Host ""

# Đường dẫn project
$projectPath = "F:\OCR\OCR"

Write-Host "📁 Thêm exclusion cho: $projectPath" -ForegroundColor Cyan
Write-Host ""

try {
    # Thêm exclusion cho folder
    Add-MpPreference -ExclusionPath $projectPath
    Write-Host "✅ Đã thêm exclusion cho folder thành công!" -ForegroundColor Green
    Write-Host ""
    
    # Hiển thị danh sách exclusions hiện tại
    Write-Host "📋 Danh sách Exclusions hiện tại:" -ForegroundColor Cyan
    $exclusions = Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
    if ($exclusions) {
        foreach ($path in $exclusions) {
            Write-Host "   - $path" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   (Không có exclusion nào)" -ForegroundColor Gray
    }
    Write-Host ""
    
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              ✅ HOÀN TẤT!                                 ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Bạn có thể build lại bằng cách chạy:" -ForegroundColor Cyan
    Write-Host "  .\rebuild_after_exclusion.bat" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "❌ ERROR: Không thể thêm exclusion!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Chi tiết lỗi:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Hãy thử thêm thủ công:" -ForegroundColor Yellow
    Write-Host "  1. Mở Windows Security" -ForegroundColor Yellow
    Write-Host "  2. Virus & threat protection → Manage settings" -ForegroundColor Yellow
    Write-Host "  3. Exclusions → Add or remove exclusions" -ForegroundColor Yellow
    Write-Host "  4. Add an exclusion → Folder → Chọn F:\OCR\OCR" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

pause

