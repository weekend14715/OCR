# Hướng dẫn xóa hotkey đã lưu

## Tổng quan
Các script này giúp bạn xóa hotkey (phím tắt) đã lưu trong Vietnamese OCR Tool.

## Các file có sẵn

### 1. `clear_hotkey.bat` (Windows Batch)
- **Cách chạy**: Double-click hoặc chạy từ Command Prompt
- **Ưu điểm**: Đơn giản, không cần cài đặt gì thêm
- **Sử dụng**: Phù hợp cho người dùng Windows cơ bản

### 2. `clear_hotkey.ps1` (PowerShell)
- **Cách chạy**: 
  - Right-click → "Run with PowerShell"
  - Hoặc mở PowerShell và chạy: `.\clear_hotkey.ps1`
- **Ưu điểm**: Hiển thị màu sắc đẹp, xử lý lỗi tốt hơn
- **Lưu ý**: Có thể cần thay đổi Execution Policy

### 3. `clear_hotkey.py` (Python)
- **Cách chạy**: 
  - `python clear_hotkey.py`
  - Hoặc `python3 clear_hotkey.py`
- **Ưu điểm**: Cross-platform, dễ tùy chỉnh
- **Yêu cầu**: Cần cài Python

## Cách hoạt động

1. **Kiểm tra thư mục config**: `%LOCALAPPDATA%\VietnameseOCRTool\`
2. **Hiển thị nội dung**: Cho bạn xem hotkey hiện tại
3. **Xác nhận xóa**: Hỏi bạn có chắc chắn muốn xóa không
4. **Xóa file**: Xóa `config.ini` chứa hotkey
5. **Dọn dẹp**: Xóa thư mục config nếu trống

## Lưu ý quan trọng

- ⚠️ **Sau khi xóa hotkey, lần chạy tiếp theo ứng dụng sẽ yêu cầu chọn hotkey mới**
- ✅ **An toàn**: Script chỉ xóa file config, không ảnh hưởng đến ứng dụng chính
- 🔄 **Có thể hoàn tác**: Bạn có thể chọn hotkey mới bất kỳ lúc nào

## Vị trí lưu trữ hotkey

```
%LOCALAPPDATA%\VietnameseOCRTool\
└── config.ini          ← File chứa hotkey
```

## Troubleshooting

### Lỗi "Execution Policy" (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Lỗi "Permission denied" (Batch/Python)
- Chạy Command Prompt/PowerShell với quyền Administrator
- Hoặc chạy script từ thư mục khác

### Không tìm thấy file config
- Có thể bạn chưa bao giờ sử dụng hotkey
- Hoặc đã xóa rồi

## Liên hệ hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Đường dẫn thư mục config có đúng không
2. Quyền truy cập file
3. Ứng dụng có đang chạy không (nên tắt trước khi xóa)
