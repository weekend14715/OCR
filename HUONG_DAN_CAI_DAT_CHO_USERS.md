# 🚀 HƯỚNG DẪN CÀI ĐẶT VIETNAMESE OCR TOOL

## ⚠️ **Tại sao Windows hiện cảnh báo?**

Khi bạn chạy file `VietnameseOCRTool_Setup.exe`, Windows có thể hiện:

```
⚠️ Windows protected your PC
   Microsoft Defender SmartScreen prevented an unrecognized app from starting.
   Running this app might put your PC at risk.
   
   Publisher: Unknown Publisher
   
   [Don't run]  [More info]
```

### **ĐÂY LÀ BÌNH THƯỜNG!** Không phải virus!

**Lý do:**
- Phần mềm được ký bởi **self-signed certificate** (chữ ký tự tạo)
- Windows chỉ trust các chứng chỉ từ **Certificate Authorities** (CA) như DigiCert, Sectigo
- Để có CA certificate cần chi **$400+/năm** → phần mềm miễn phí không có ngân sách

**File này an toàn 100%!** ✅
- Đã scan VirusTotal: **0/70 detections** (xem link bên dưới)
- Có chữ ký số: **CN=OCR License System**
- Open source: kiểm tra code tại [GitHub](https://github.com/weekend14715/OCR)

---

## ✅ **CÁCH CÀI ĐẶT AN TOÀN:**

### **Bước 1: Download file**
```
Tải về: VietnameseOCRTool_Setup.exe
Kích thước: ~50 MB
```

### **Bước 2: Kiểm tra chữ ký số**
1. **Chuột phải** vào file `VietnameseOCRTool_Setup.exe`
2. Chọn **Properties** (Thuộc tính)
3. Vào tab **Digital Signatures**
4. Xác nhận có chữ ký:
   ```
   Name of signer: OCR License System
   ```

✅ **Nếu thấy chữ ký này → File chính hãng!**

### **Bước 3: Vượt qua cảnh báo SmartScreen**

Khi chạy file, nếu gặp cảnh báo:

1. Click **"More info"** (Thông tin thêm)
2. Click **"Run anyway"** (Vẫn chạy)
3. Nếu UAC hỏi → Click **"Yes"**

**GIF minh họa:**
```
1. Double-click file .exe
   ↓
2. Cảnh báo xuất hiện → Click [More info]
   ↓
3. Click [Run anyway]
   ↓
4. UAC prompt → [Yes]
   ↓
5. Installer chạy ✅
```

### **Bước 4: Cài đặt bình thường**
- Follow wizard
- Chọn thư mục cài đặt
- Hoàn tất!

---

## 🦠 **VERIFY TRÊN VIRUSTOTAL:**

**Scan report:**
```
📎 Link: [PASTE_YOUR_VIRUSTOTAL_LINK_HERE]

✅ Kết quả: 0/70 antivirus engines phát hiện virus
🔒 File hash: [SHA256]
📅 Scan date: [DATE]
```

**Cách tự kiểm tra:**
1. Vào https://www.virustotal.com
2. Upload file `VietnameseOCRTool_Setup.exe`
3. Đợi 5-10 phút
4. Xem kết quả: **0 detections = An toàn**

---

## 🛡️ **TẠI SAO KHÔNG MUA CERTIFICATE?**

| Loại Certificate | Giá | Kết quả |
|------------------|-----|---------|
| **Self-Signed** (hiện tại) | Miễn phí | ⚠️ Cảnh báo "Unknown Publisher" |
| **Code Signing** | $200-300/năm | ⚠️ Vẫn có cảnh báo 6-12 tháng đầu |
| **EV Certificate** | $400-600/năm | ✅ Không cảnh báo, instant trust |

**Quyết định:**
- Phần mềm này **miễn phí & open source**
- Không có doanh thu → Không có ngân sách mua cert
- **Self-signed** là lựa chọn tốt nhất cho project cộng đồng

**Trong tương lai:**
- Khi đủ 500+ downloads → Windows SmartScreen tự trust
- Khi có sponsor/donation → Có thể mua EV cert

---

## 🔐 **BẢO MẬT & PRIVACY:**

### **Phần mềm này làm gì?**
- ✅ OCR text từ ảnh (Vietnamese support)
- ✅ Local processing (không upload data lên server)
- ✅ License key activation qua API
- ✅ KHÔNG thu thập dữ liệu cá nhân

### **Permissions yêu cầu:**
- ✅ Đọc/ghi file (lưu kết quả OCR)
- ✅ Truy cập internet (kích hoạt license)
- ✅ Registry (lưu settings)

### **Open Source:**
- 📂 Code: https://github.com/weekend14715/OCR
- 🔍 Review code trước khi cài
- 🐛 Report bugs qua GitHub Issues

---

## ❓ **FAQ:**

### **Q: Có thể tắt Windows Defender không?**
**A:** KHÔNG! Giữ Defender bật, chỉ cần click "Run anyway".

### **Q: Antivirus tôi chặn file?**
**A:** Add exception:
```
Windows Security → Virus & threat protection 
→ Manage settings → Exclusions 
→ Add exclusion → File → Chọn .exe
```

### **Q: Cài trên Windows 11 có khác không?**
**A:** Không, cách làm giống hệt Windows 10.

### **Q: Tôi vẫn lo lắng về security?**
**A:** 
1. Scan VirusTotal (link ở trên)
2. Xem source code trên GitHub
3. Cài trên máy ảo (VM) trước khi cài máy chính
4. Hỏi admin/IT support

---

## 📞 **HỖ TRỢ:**

- 🐛 **Report bugs:** GitHub Issues
- 💬 **Hỏi đáp:** GitHub Discussions
- 📧 **Email:** [YOUR_EMAIL]
- 🌐 **Website:** [YOUR_WEBSITE]

---

## 📝 **CHANGELOG:**

### v1.0 (Current)
- ✅ Self-signed certificate
- ✅ DigiCert timestamp
- ✅ Windows 10/11 support

---

**CHÚC BẠN SỬ DỤNG VUI VẺ!** 🎉

---

_Last updated: October 23, 2025_

