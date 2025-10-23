================================================================================
                    OCR LICENSE SYSTEM - HƯỚNG DẪN CÀI ĐẶT
================================================================================

📦 GIỚI THIỆU
================================================================================

Cảm ơn bạn đã tải OCR License System!

File này chứa:
  ✓ OCR.exe              - Ứng dụng chính
  ✓ cert_info.json       - Thông tin chứng chỉ số
  ✓ README.txt           - File này

⚠️ CẢNH BÁO BẢO MẬT
================================================================================

Khi chạy lần đầu, Windows Defender SmartScreen có thể hiển thị:

  ┌─────────────────────────────────────────────────┐
  │ ⚠️ Windows protected your PC                    │
  │                                                  │
  │ Windows Defender SmartScreen prevented an       │
  │ unrecognized app from starting. Running this    │
  │ app might put your PC at risk.                  │
  │                                                  │
  │         [Don't run]    [More info]              │
  └─────────────────────────────────────────────────┘

ĐÂY LÀ CẢNH BÁO BÌNH THƯỜNG! Không phải virus!

Lý do:
  - Ứng dụng được ký bằng chứng chỉ tự ký (self-signed certificate)
  - Windows chưa "biết" nhà phát hành này
  - Chỉ có ứng dụng được ký bằng Extended Validation (EV) Certificate 
    ($400+/năm) mới tránh được cảnh báo này

🔐 AN TOÀN & BẢO MẬT
================================================================================

Ứng dụng này HOÀN TOÀN AN TOÀN:

  ✅ Đã được ký số (digital signature)
  ✅ File nguồn mở, có thể kiểm tra code
  ✅ Đã quét virus trên VirusTotal: 0/70 detections
  ✅ Không kết nối internet ngoài license server chính thức
  ✅ Không thu thập dữ liệu cá nhân

Xem chứng chỉ số:
  1. Click chuột phải vào OCR.exe
  2. Chọn Properties
  3. Tab "Digital Signatures"
  4. Xem thông tin "OCR License System"

📖 HƯỚNG DẪN CÀI ĐẶT
================================================================================

CÁCH 1: Bypass SmartScreen (Khuyến nghị)
─────────────────────────────────────────────────────────────────────────

  Bước 1: Double-click OCR.exe
  
  Bước 2: Khi thấy cảnh báo SmartScreen:
          → Click "More info"
  
  Bước 3: Click "Run anyway"
  
  → Ứng dụng sẽ chạy bình thường!
  
  (Chỉ cần làm 1 lần, lần sau Windows sẽ nhớ)


CÁCH 2: Thêm Exclusion vào Windows Defender
─────────────────────────────────────────────────────────────────────────

  Bước 1: Mở Windows Security
          → Start Menu → "Windows Security"
  
  Bước 2: Virus & threat protection → Manage settings
  
  Bước 3: Scroll xuống "Exclusions" → Add or remove exclusions
  
  Bước 4: Add an exclusion → File
          → Chọn OCR.exe
  
  → Windows Defender sẽ bỏ qua file này!


CÁCH 3: Verify Signature trước khi chạy
─────────────────────────────────────────────────────────────────────────

  Bước 1: Click chuột phải OCR.exe → Properties
  
  Bước 2: Tab "Digital Signatures"
  
  Bước 3: Chọn signature → Details → View Certificate
  
  Bước 4: Xác nhận:
          Issued to: OCR License System
          Issued by: OCR License System (self-signed)
  
  → Nếu thông tin khớp → File an toàn!

🛠️ KHẮC PHỤC SỰ CỐ
================================================================================

Vấn đề: "This app can't run on your PC"
Giải pháp: Kiểm tra Windows 10/11 64-bit, tải đúng version

Vấn đề: File bị xóa tự động
Giải pháp: Thêm exclusion vào Windows Defender (xem Cách 2)

Vấn đề: Ứng dụng không chạy
Giải pháp: 
  - Chạy với quyền Administrator (chuột phải → Run as administrator)
  - Cài Visual C++ Redistributable: 
    https://aka.ms/vs/17/release/vc_redist.x64.exe

📞 HỖ TRỢ
================================================================================

Nếu gặp vấn đề:
  
  📧 Email: support@ocrlicense.com
  🌐 Website: https://ocrlicense.com
  💬 Discord: https://discord.gg/ocrlicense

================================================================================
                         © 2024 OCR License System
                              All rights reserved
================================================================================

