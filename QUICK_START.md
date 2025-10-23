# 🚀 Quick Start - Ký số file .exe

## ⚡ Cách nhanh nhất (1 lệnh)

```powershell
# Tạo certificate + Build + Sign
.\build_and_sign.ps1
```

**Hoàn tất!** File `.exe` đã được ký số trong `dist\OCR.exe`

---

## 📝 Chi tiết từng bước

### **Bước 1: Tạo Certificate (Chỉ làm 1 lần)**

```powershell
.\create_self_signed_cert.ps1
```

**Output:**
```
🔐 TẠO SELF-SIGNED CERTIFICATE
✅ Certificate đã tạo thành công!
💾 Đã export certificate sang file: .\OCR_CodeSigning.pfx
   Password: OCR2024!
```

**Files tạo ra:**
- `OCR_CodeSigning.pfx` - Certificate file (⚠️ GIỮ BÍ MẬT!)
- `cert_info.json` - Thông tin certificate

---

### **Bước 2: Ký file .exe**

**Nếu đã có file .exe:**
```powershell
.\sign_exe.ps1 -ExePath "dist\OCR.exe"
```

**Nếu chưa build:**
```powershell
.\build_and_sign.ps1
```

**Output:**
```
🔐 KÝ FILE .EXE
✅ KÝ THÀNH CÔNG!
📋 Thông tin chữ ký:
   Status: Valid
   Signer: CN=OCR License System
```

---

## ✅ Verify Signature

```powershell
Get-AuthenticodeSignature "dist\OCR.exe"
```

**Kết quả mong đợi:**
```
SignerCertificate      : CN=OCR License System
TimeStamperCertificate : CN=DigiCert Timestamp
Status                 : Valid
```

---

## 📦 Đóng gói Release

### **1. Test file .exe:**
```powershell
.\dist\OCR.exe
```

### **2. Tạo package:**
```powershell
# Tạo folder release
mkdir release
Copy-Item "dist\OCR.exe" "release\"
Copy-Item "README_INSTALLATION.txt" "release\README.txt"

# Zip
Compress-Archive -Path "release\*" -DestinationPath "OCR_v1.0.0_signed.zip"
```

### **3. Upload VirusTotal:**
1. Truy cập: https://www.virustotal.com
2. Upload `OCR.exe`
3. Đợi scan → Share link với users

---

## 🎯 User Installation

Khi user download file:

1. **Extract .zip**
2. **Double-click OCR.exe**
3. **Windows SmartScreen hiện cảnh báo:**
   - Click **"More info"**
   - Click **"Run anyway"**
4. **Done!**

(Chỉ cần làm 1 lần, lần sau Windows sẽ nhớ)

---

## ⚠️ Important Notes

### **✅ Làm:**
- ✅ Keep `OCR_CodeSigning.pfx` an toàn
- ✅ Backup certificate file
- ✅ Sign mọi release versions
- ✅ Include README_INSTALLATION.txt

### **❌ Không làm:**
- ❌ Commit `.pfx` file lên Git
- ❌ Share password `OCR2024!`
- ❌ Release unsigned .exe
- ❌ Thay đổi certificate khi đã phát hành

---

## 🔄 Workflow

```
┌─────────────────┐
│ Write Python    │
│ code            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ build_and_sign  │  ← Chạy script này
│ .ps1            │
└────────┬────────┘
         │
         ├─► Build .exe (PyInstaller)
         │
         ├─► Sign .exe (Certificate)
         │
         └─► Verify signature
                  │
                  ▼
         ┌─────────────────┐
         │ dist\OCR.exe    │
         │ (Signed ✓)      │
         └─────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Package & Ship  │
         └─────────────────┘
```

---

## 📚 Tài liệu

- **Chi tiết:** `SIGNING_GUIDE.md`
- **User guide:** `README_INSTALLATION.txt`
- **Persistent storage:** `PERSISTENT_STORAGE_SETUP.md`

---

**🎉 Ready to sign your .exe files!**
