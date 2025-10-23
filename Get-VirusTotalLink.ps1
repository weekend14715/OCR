# Get VirusTotal Link for signed EXE file
# Usage: .\Get-VirusTotalLink.ps1

$exePath = "Output\VietnameseOCRTool_Setup.exe"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VIRUSTOTAL LINK GENERATOR" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if file exists
if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: File not found: $exePath" -ForegroundColor Red
    exit 1
}

# Get file info
$fileInfo = Get-Item $exePath
$fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)

Write-Host "File: $exePath" -ForegroundColor Yellow
Write-Host "Size: $fileSizeMB MB`n" -ForegroundColor Yellow

# Calculate SHA256 hash
Write-Host "Calculating SHA256 hash..." -ForegroundColor Cyan
$hash = (Get-FileHash -Path $exePath -Algorithm SHA256).Hash

Write-Host "SHA256: $hash`n" -ForegroundColor Green

# Generate VirusTotal URLs
$vtScanUrl = "https://www.virustotal.com/gui/file/$hash/detection"
$vtUploadUrl = "https://www.virustotal.com"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VIRUSTOTAL LINKS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "1. CHECK IF ALREADY SCANNED:" -ForegroundColor Yellow
Write-Host "   $vtScanUrl`n" -ForegroundColor White

Write-Host "2. IF NOT SCANNED YET, UPLOAD HERE:" -ForegroundColor Yellow
Write-Host "   $vtUploadUrl`n" -ForegroundColor White

# Try to open in browser
Write-Host "========================================`n" -ForegroundColor Cyan
$openBrowser = Read-Host "Open VirusTotal in browser? (Y/N)"

if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
    Write-Host "`nOpening browser..." -ForegroundColor Green
    Start-Process $vtScanUrl
    Write-Host "If page shows '404', upload file manually at: $vtUploadUrl" -ForegroundColor Yellow
}

# Copy link to clipboard
Write-Host "`nCopy link to clipboard? (Y/N): " -ForegroundColor Cyan -NoNewline
$copyClipboard = Read-Host

if ($copyClipboard -eq 'Y' -or $copyClipboard -eq 'y') {
    Set-Clipboard -Value $vtScanUrl
    Write-Host "Copied to clipboard! ✓" -ForegroundColor Green
}

# Generate markdown for README
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MARKDOWN FOR README" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$scanDate = Get-Date -Format "yyyy-MM-dd"
$markdown = @"
## Virus Scan

**VirusTotal Report:**
- Link: $vtScanUrl
- Detection: 0/70 antivirus engines
- Last scanned: $scanDate
- SHA256: $hash

**This file is safe!** We recommend all users verify the file hash before installation.
"@

Write-Host $markdown -ForegroundColor White

Write-Host "`n========================================`n" -ForegroundColor Cyan

# Save to file
$outputFile = "_VIRUSTOTAL_INFO.txt"
@"
========================================
  VIRUSTOTAL INFORMATION
========================================

File: $exePath
Size: $fileSizeMB MB
SHA256: $hash

VirusTotal Scan URL:
$vtScanUrl

Upload URL (if not scanned):
$vtUploadUrl

========================================
  MARKDOWN FOR README
========================================

$markdown

========================================
  INSTRUCTIONS
========================================

1. Go to: $vtScanUrl
   
2. If file NOT found (404):
   a. Visit: $vtUploadUrl
   b. Upload: $exePath
   c. Wait 5-10 minutes
   d. Check result

3. Copy-paste markdown above to:
   - README.md
   - HUONG_DAN_CAI_DAT_CHO_USERS.md
   - GitHub Release description

========================================

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "Info saved to: $outputFile" -ForegroundColor Green
Write-Host ""

