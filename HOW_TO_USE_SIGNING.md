# 🎓 Hướng dẫn sử dụng Code Signing từ A-Z

## 🎯 Mục tiêu

Ký số file `.exe` để:
- ✅ Giảm cảnh báo Windows SmartScreen
- ✅ Tăng độ tin cậy của ứng dụng
- ✅ Chứng minh file không bị thay đổi (integrity)

---

## 🧪 Test nhanh (5 phút)

### **Chạy demo hoàn chỉnh:**

```powershell
.\TEST_SIGNING.ps1
```

**Script này sẽ:**
1. ✅ Tạo self-signed certificate
2. ✅ Build demo app (`test_signing_demo.py`)
3. ✅ Sign file `.exe`
4. ✅ Verify signature
5. ✅ Test run app

**Kết quả:** File `dist\OCR_Demo.exe` đã được ký số!

---

## 📚 Sử dụng cho dự án thật

### **Scenario 1: Đã có file .exe**

```powershell
# Bước 1: Tạo certificate (lần đầu tiên)
.\create_self_signed_cert.ps1

# Bước 2: Ký file .exe
.\sign_exe.ps1 -ExePath "path\to\your\app.exe"

# Bước 3: Verify
Get-AuthenticodeSignature "path\to\your\app.exe"
```

---

### **Scenario 2: Build từ Python script**

```powershell
# All-in-one: Build + Sign
.\build_and_sign.ps1

# Kết quả: dist\OCR.exe (signed)
```

**Lưu ý:** Script tự động tìm file Python chính (`main.py`, `OCR.py`, `app.py`, etc.)

---

### **Scenario 3: Custom build**

```powershell
# Bước 1: Build .exe theo ý bạn
pyinstaller --onefile --windowed --icon myicon.ico main.py

# Bước 2: Sign
.\sign_exe.ps1 -ExePath "dist\main.exe"
```

---

## 🔑 Certificate Management

### **Thông tin Certificate:**

- **File:** `OCR_CodeSigning.pfx`
- **Password:** `OCR2024!`
- **Validity:** 3 năm
- **Type:** Self-signed Code Signing

### **⚠️ BẢO MẬT QUAN TRỌNG:**

```
❌ KHÔNG commit .pfx lên Git
❌ KHÔNG share password công khai
❌ KHÔNG gửi qua email/chat không mã hóa
✅ Backup file .pfx an toàn
✅ Dùng password manager
✅ Chỉ install trên máy dev tin cậy
```

### **Backup Certificate:**

```powershell
# Copy sang USB/Cloud an toàn
Copy-Item "OCR_CodeSigning.pfx" "D:\Backup\Certificates\"
Copy-Item "cert_info.json" "D:\Backup\Certificates\"
```

### **Restore trên máy mới:**

```powershell
# Import .pfx vào Windows Certificate Store
Import-PfxCertificate -FilePath "OCR_CodeSigning.pfx" -CertStoreLocation Cert:\CurrentUser\My

# Hoặc dùng .pfx trực tiếp
.\sign_exe.ps1 -ExePath "app.exe" -PfxFile "OCR_CodeSigning.pfx" -PfxPassword "OCR2024!"
```

---

## 📦 Release Process

### **1. Build signed release:**

```powershell
# Build & Sign
.\build_and_sign.ps1

# Kết quả: dist\OCR.exe
```

### **2. Verify:**

```powershell
# Check signature
$sig = Get-AuthenticodeSignature "dist\OCR.exe"
Write-Host "Status: $($sig.Status)"
Write-Host "Signer: $($sig.SignerCertificate.Subject)"
```

### **3. Package:**

```powershell
# Tạo release folder
mkdir release
Copy-Item "dist\OCR.exe" "release\"
Copy-Item "README_INSTALLATION.txt" "release\README.txt"

# Zip
Compress-Archive -Path "release\*" -DestinationPath "OCR_v1.0.0_signed.zip"
```

### **4. Upload VirusTotal:**

1. Truy cập: https://www.virustotal.com
2. Upload `OCR.exe`
3. Đợi scan (2-3 phút)
4. Copy link kết quả
5. Share link trong README

**Ví dụ:**
```
✅ VirusTotal Scan: 0/70 detections
🔗 https://virustotal.com/gui/file/abc123.../detection
```

---

## 🔍 Verify Signature

### **Method 1: PowerShell**

```powershell
Get-AuthenticodeSignature "dist\OCR.exe" | Format-List *
```

### **Method 2: Windows UI**

1. Chuột phải `OCR.exe` → **Properties**
2. Tab **"Digital Signatures"**
3. Select signature → **Details**
4. **View Certificate**

### **Method 3: Script**

```powershell
$sig = Get-AuthenticodeSignature "dist\OCR.exe"

if ($sig.SignerCertificate) {
    Write-Host "✅ Signed" -ForegroundColor Green
    Write-Host "   Subject: $($sig.SignerCertificate.Subject)"
    Write-Host "   Valid: $($sig.SignerCertificate.NotBefore) → $($sig.SignerCertificate.NotAfter)"
} else {
    Write-Host "❌ Not signed" -ForegroundColor Red
}
```

---

## 👥 User Installation Guide

### **Hướng dẫn cho Users (trong README_INSTALLATION.txt):**

```
1. Download OCR_v1.0.0_signed.zip
2. Extract files
3. Double-click OCR.exe
4. Nếu thấy cảnh báo SmartScreen:
   → Click "More info"
   → Click "Run anyway"
5. Done!
```

**Tại sao vẫn có cảnh báo?**
- Self-signed certificate chưa được Microsoft trust
- Cần EV Certificate ($400/năm) để loại bỏ hoàn toàn

**File có an toàn không?**
- ✅ Có chữ ký số
- ✅ Đã scan VirusTotal
- ✅ Source code công khai

---

## 🚀 Advanced: CI/CD Integration

### **GitHub Actions Example:**

```yaml
name: Build & Sign

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pyinstaller
      
      - name: Import Certificate
        run: |
          $pfxBytes = [Convert]::FromBase64String($env:CERT_PFX_BASE64)
          [IO.File]::WriteAllBytes("cert.pfx", $pfxBytes)
        env:
          CERT_PFX_BASE64: ${{ secrets.CERT_PFX_BASE64 }}
      
      - name: Build & Sign
        run: |
          pyinstaller --onefile --windowed main.py
          .\sign_exe.ps1 -ExePath "dist\main.exe" -PfxFile "cert.pfx" -PfxPassword "$env:CERT_PASSWORD"
        env:
          CERT_PASSWORD: ${{ secrets.CERT_PASSWORD }}
      
      - name: Upload Release
        uses: actions/upload-artifact@v3
        with:
          name: OCR-signed
          path: dist\main.exe
```

**Setup Secrets:**
```powershell
# Convert .pfx to Base64
$bytes = [IO.File]::ReadAllBytes("OCR_CodeSigning.pfx")
$base64 = [Convert]::ToBase64String($bytes)
Write-Output $base64

# Add to GitHub Secrets:
# CERT_PFX_BASE64 = <base64 string>
# CERT_PASSWORD = OCR2024!
```

---

## 📊 Monitoring & Metrics

### **Track signature status:**

```powershell
# Check all .exe in dist folder
Get-ChildItem -Path dist -Filter *.exe | ForEach-Object {
    $sig = Get-AuthenticodeSignature $_.FullName
    [PSCustomObject]@{
        File = $_.Name
        Signed = ($null -ne $sig.SignerCertificate)
        Status = $sig.Status
        Signer = $sig.SignerCertificate.Subject
    }
} | Format-Table -AutoSize
```

### **Verify before release:**

```powershell
# Pre-release checklist
function Test-Release {
    param($ExePath)
    
    $checks = @{
        "File exists" = Test-Path $ExePath
        "Signed" = (Get-AuthenticodeSignature $ExePath).SignerCertificate -ne $null
        "Size > 1MB" = (Get-Item $ExePath).Length -gt 1MB
    }
    
    $checks.GetEnumerator() | ForEach-Object {
        $icon = if ($_.Value) { "✅" } else { "❌" }
        Write-Host "$icon $($_.Key)"
    }
}

Test-Release "dist\OCR.exe"
```

---

## ❓ Troubleshooting

### **Issue: "Cannot find certificate"**

```powershell
# List installed certs
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert

# Re-create if needed
.\create_self_signed_cert.ps1
```

### **Issue: "Set-AuthenticodeSignature failed"**

```powershell
# Try using .pfx file directly
.\sign_exe.ps1 -ExePath "app.exe" -PfxFile "OCR_CodeSigning.pfx"
```

### **Issue: "Timestamp server timeout"**

```powershell
# Change timestamp server in sign_exe.ps1
# Replace:
-TimestampServer "http://timestamp.digicert.com"
# With:
-TimestampServer "http://timestamp.comodoca.com"
# Or:
-TimestampServer "http://timestamp.globalsign.com"
```

### **Issue: Certificate expired**

```powershell
# Create new certificate
.\create_self_signed_cert.ps1

# Re-sign all .exe files
Get-ChildItem -Path dist -Filter *.exe | ForEach-Object {
    .\sign_exe.ps1 -ExePath $_.FullName
}
```

---

## 🎓 Best Practices

### **✅ Do:**

1. **Always sign releases**
   - Mọi version phát hành cho users
   - Bao gồm beta/alpha releases

2. **Backup certificate**
   - Lưu `.pfx` file an toàn
   - Document password

3. **Verify before release**
   - Check signature status
   - Test trên máy sạch
   - Scan VirusTotal

4. **Include documentation**
   - README_INSTALLATION.txt
   - Hướng dẫn bypass SmartScreen
   - Link VirusTotal scan

5. **Version control**
   - Git tag releases
   - Track signed versions
   - Keep release notes

### **❌ Don't:**

1. **Never commit sensitive files**
   - `.pfx` files
   - Passwords
   - Private keys

2. **Don't reuse passwords**
   - Mỗi project = password riêng
   - Dùng password manager

3. **Don't skip verification**
   - Luôn verify sau khi sign
   - Test trước khi phát hành

4. **Don't ignore warnings**
   - Signature failures
   - Certificate expiry
   - Linter errors

---

## 📈 Roadmap

### **Current: Self-Signed (Free)**
- ✅ Basic signing
- ⚠️ Still shows "Unknown Publisher"
- ⏱️ Time: 10 phút setup

### **Future: OV Certificate ($200/năm)**
- ✅ Organization validation
- ✅ Company name shown
- ⏱️ Time: 2-5 ngày validation

### **Future: EV Certificate ($400/năm)**
- ✅ Extended validation
- ✅ Instant trust
- ✅ No SmartScreen warnings
- ⏱️ Time: 5-10 ngày validation

---

## 📚 Resources

- **Microsoft Docs:** https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools
- **DigiCert:** https://www.digicert.com/signing/code-signing-certificates
- **Sectigo:** https://sectigo.com/ssl-certificates-tls/code-signing
- **VirusTotal:** https://www.virustotal.com
- **SmartScreen Info:** https://www.microsoft.com/en-us/wdsi/filesubmission

---

## ✅ Quick Reference

| Task | Command |
|------|---------|
| Tạo certificate | `.\create_self_signed_cert.ps1` |
| Ký .exe có sẵn | `.\sign_exe.ps1 -ExePath "app.exe"` |
| Build + Sign | `.\build_and_sign.ps1` |
| Test full flow | `.\TEST_SIGNING.ps1` |
| Verify signature | `Get-AuthenticodeSignature "app.exe"` |

---

**🎉 Happy Signing!**

