# 🔐 Code Signing Guide - Ký số file .exe

## 📋 Mục đích

Ký số file `.exe` để giảm cảnh báo **Windows SmartScreen** và tăng độ tin cậy cho users.

---

## 🚀 Quick Start

### **1. Tạo Self-Signed Certificate**

```powershell
.\create_self_signed_cert.ps1
```

**Kết quả:**
- ✅ Certificate được tạo trong Windows Certificate Store
- ✅ Export sang file `OCR_CodeSigning.pfx`
- ✅ Password: `OCR2024!`
- ✅ Thông tin lưu trong `cert_info.json`

---

### **2. Ký file .exe có sẵn**

```powershell
.\sign_exe.ps1 -ExePath "dist\OCR.exe"
```

**Kết quả:**
- ✅ File `.exe` được ký số
- ✅ Verify chữ ký tự động
- ✅ Timestamp từ DigiCert (đảm bảo chữ ký vẫn valid sau khi cert expire)

---

### **3. Build & Sign tự động**

```powershell
.\build_and_sign.ps1
```

**Thực hiện:**
1. Check PyInstaller
2. Tạo certificate (nếu chưa có)
3. Build `.exe` từ Python script
4. Tự động ký file `.exe`
5. Verify chữ ký

---

## 📁 Files đã tạo

| File | Mô tả |
|------|-------|
| `create_self_signed_cert.ps1` | Script tạo self-signed certificate |
| `sign_exe.ps1` | Script ký file .exe |
| `build_and_sign.ps1` | Script build + sign tự động |
| `OCR_CodeSigning.pfx` | Certificate file (QUAN TRỌNG - giữ bí mật!) |
| `cert_info.json` | Thông tin certificate |
| `README_INSTALLATION.txt` | Hướng dẫn user cài đặt |

---

## 🔑 Certificate Information

### **Certificate Details:**
- **Type:** Self-Signed Code Signing Certificate
- **Subject:** CN=OCR License System
- **Validity:** 3 năm
- **Store Location:** `Cert:\CurrentUser\My`
- **Password:** `OCR2024!`

### **⚠️ BẢO MẬT:**

**GIỮ BÍ MẬT:**
- ❌ **KHÔNG** commit `OCR_CodeSigning.pfx` lên Git
- ❌ **KHÔNG** share password `OCR2024!`
- ❌ **KHÔNG** gửi file .pfx qua email/chat

**Đã thêm vào `.gitignore`:**
```gitignore
*.pfx
cert_info.json
```

---

## 🛠️ Sử dụng

### **Workflow 1: Development**

```powershell
# Lần đầu: Tạo certificate
.\create_self_signed_cert.ps1

# Mỗi lần build
pyinstaller --onefile --windowed main.py
.\sign_exe.ps1 -ExePath "dist\main.exe"
```

### **Workflow 2: Automated Build**

```powershell
# All-in-one
.\build_and_sign.ps1
```

### **Workflow 3: CI/CD**

```yaml
# GitHub Actions example
- name: Sign .exe
  run: |
    # Import certificate từ GitHub Secrets
    $pfxBytes = [Convert]::FromBase64String($env:CERT_PFX_BASE64)
    [IO.File]::WriteAllBytes("cert.pfx", $pfxBytes)
    
    # Sign
    .\sign_exe.ps1 -ExePath "dist\OCR.exe" -PfxFile "cert.pfx" -PfxPassword $env:CERT_PASSWORD
  env:
    CERT_PFX_BASE64: ${{ secrets.CERT_PFX_BASE64 }}
    CERT_PASSWORD: ${{ secrets.CERT_PASSWORD }}
```

---

## 🔍 Verify Signature

### **PowerShell:**
```powershell
Get-AuthenticodeSignature "dist\OCR.exe"
```

**Output mong đợi:**
```
Status        : Valid (hoặc UnknownError cho self-signed)
SignerCertificate : CN=OCR License System
TimeStamperCertificate : CN=DigiCert Timestamp...
```

### **Windows UI:**
1. Chuột phải file `.exe` → **Properties**
2. Tab **"Digital Signatures"**
3. Xem thông tin signer

---

## ⚠️ Limitations của Self-Signed Certificate

### **Vẫn hiện cảnh báo:**

```
⚠️ Windows Defender SmartScreen
   Unknown Publisher
   
   [More info] → [Run anyway]
```

### **So sánh:**

| Certificate Type | SmartScreen Warning | User Action Required |
|------------------|---------------------|---------------------|
| **Unsigned** | ⚠️⚠️⚠️ "Dangerous file" | Click 3 times |
| **Self-signed** | ⚠️⚠️ "Unknown publisher" | Click 2 times |
| **OV Certificate** | ⚠️ "Unverified publisher" | Click 1 time |
| **EV Certificate** | ✅ No warning | No action |

### **Khi nào nên nâng cấp:**

- **100+ users:** Mua OV Certificate ($200/năm)
- **1000+ users:** Mua EV Certificate ($400/năm)
- **Enterprise:** EV + Build reputation với Microsoft

---

## 📦 Packaging for Release

### **Tạo release package:**

```powershell
# Build & Sign
.\build_and_sign.ps1

# Tạo release folder
mkdir release
Copy-Item "dist\OCR.exe" "release\"
Copy-Item "README_INSTALLATION.txt" "release\README.txt"
Copy-Item "cert_info.json" "release\"

# Zip
Compress-Archive -Path "release\*" -DestinationPath "OCR_v1.0.0_signed.zip"
```

**Release package chứa:**
- ✅ `OCR.exe` (signed)
- ✅ `README.txt` (hướng dẫn bypass SmartScreen)
- ✅ `cert_info.json` (để user verify)

---

## 🧪 Testing

### **Test 1: Verify Signature**
```powershell
$sig = Get-AuthenticodeSignature "dist\OCR.exe"
if ($sig.SignerCertificate) { 
    Write-Host "✅ Signed" 
} else { 
    Write-Host "❌ Not signed" 
}
```

### **Test 2: VirusTotal**
1. Upload `.exe` lên https://www.virustotal.com
2. Đợi scan (2-3 phút)
3. Check kết quả: **0/70 detections** = Good ✅

### **Test 3: Windows SmartScreen**
1. Copy `.exe` sang máy Windows mới (VM hoặc máy khác)
2. Download qua browser (để trigger SmartScreen)
3. Double-click → Xác nhận chỉ cần "More info → Run anyway"

---

## 🎯 Roadmap

### **Phase 1: MVP (Hiện tại)**
- ✅ Self-signed certificate
- ✅ Auto-build scripts
- ✅ User guide

### **Phase 2: Growth (100+ users)**
- [ ] Mua OV Certificate
- [ ] Submit to Microsoft SmartScreen
- [ ] Build reputation score

### **Phase 3: Scale (1000+ users)**
- [ ] Upgrade to EV Certificate
- [ ] Zero warnings
- [ ] Auto-update mechanism

---

## 📞 Troubleshooting

### **Issue: "Cannot create certificate"**
```powershell
# Chạy với quyền Admin
Start-Process powershell -Verb RunAs
.\create_self_signed_cert.ps1
```

### **Issue: "Set-AuthenticodeSignature failed"**
```powershell
# Check certificate tồn tại
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert

# Re-import .pfx
Import-PfxCertificate -FilePath "OCR_CodeSigning.pfx" -CertStoreLocation Cert:\CurrentUser\My
```

### **Issue: "Timestamp server unreachable"**
```powershell
# Thử timestamp server khác
Set-AuthenticodeSignature -FilePath "app.exe" -Certificate $cert -TimestampServer "http://timestamp.comodoca.com"
```

---

## 📚 Resources

- **Microsoft Code Signing:** https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools
- **DigiCert EV Code Signing:** https://www.digicert.com/signing/code-signing-certificates
- **VirusTotal:** https://www.virustotal.com
- **Microsoft SmartScreen:** https://www.microsoft.com/en-us/wdsi/filesubmission

---

## ✅ Checklist trước khi Release

- [ ] Certificate đã tạo
- [ ] File .exe đã signed
- [ ] Verify signature success
- [ ] VirusTotal scan clean (0 detections)
- [ ] README_INSTALLATION.txt included
- [ ] Test trên máy Windows mới
- [ ] Zip file ready to distribute

---

**🎉 All set! Ready to release signed application!**

