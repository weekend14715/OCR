#!/usr/bin/env python3
"""
Script để thay thế text tiếng Việt có dấu
"""

def fix_vietnamese():
    replacements = {
        'KIỂM TRA BẢN QUYỀN': 'KIEM TRA BAN QUYEN',
        'Đọc license từ các nguồn': 'Doc license tu cac nguon',
        'Chưa có license. Cần kích hoạt!': 'Chua co license. Can kich hoat!',
        'License bị giả mạo hoặc không hợp lệ!': 'License bi gia mao hoac khong hop le!',
        'Không thể giải mã license!': 'Khong the giai ma license!',
        'License không khớp với máy này!': 'License khong khop voi may nay!',
        'License đã hết hạn!': 'License da het han!',
        'BẢN QUYỀN HỢP LỆ': 'BAN QUYEN HOP LE',
        'Người dùng hủy kích hoạt': 'Nguoi dung huy kich hoat',
        'Kích hoạt thất bại': 'Kich hoat that bai',
        'Đã kích hoạt và lưu license thành công!': 'Da kich hoat va luu license thanh cong!',
        'Lỗi khi lưu license!': 'Loi khi luu license!',
        'Đang lưu license...': 'Dang luu license...',
        'Đã lưu license vào 3 nơi': 'Da luu license vao 3 noi',
        'Lỗi khi lưu': 'Loi khi luu',
        'Không thể lưu Registry': 'Khong the luu Registry',
        'Không thể lưu backup': 'Khong the luu backup',
        'Đã lưu backup vào thư mục app': 'Da luu backup vao thu muc app',
        'Tìm thấy file license': 'Tim thay file license',
        'Lỗi đọc file': 'Loi doc file',
        'Không tìm thấy file license': 'Khong tim thay file license',
        'Tìm thấy Registry': 'Tim thay Registry',
        'Không tìm thấy Registry': 'Khong tim thay Registry',
        'Lỗi đọc Registry': 'Loi doc Registry',
        'Tìm thấy backup': 'Tim thay backup',
        'Lỗi đọc backup': 'Loi doc backup',
        'Tìm thấy backup (fallback)': 'Tim thay backup (fallback)',
        'Lỗi đọc backup fallback': 'Loi doc backup fallback',
        'Không tìm thấy backup': 'Khong tim thay backup',
        'Chỉ tìm thấy 1 nguồn license (chấp nhận)': 'Chi tim thay 1 nguon license (chap nhan)',
        'Dữ liệu nhất quán': 'Du lieu nhat quan',
        'License sẽ hết hạn sau': 'License se het han sau',
        'ngày': 'ngay',
        'Đã xóa file license': 'Da xoa file license',
        'Không thể xóa file': 'Khong the xoa file',
        'Đã xóa Registry': 'Da xoa Registry',
        'Không thể xóa Registry': 'Khong the xoa Registry',
        'Đã xóa backup': 'Da xoa backup',
        'Không thể xóa backup': 'Khong the xoa backup',
        'Đã hủy kích hoạt hoàn toàn': 'Da huy kich hoat hoan toan',
        'Hợp lệ': 'Hop le',
        'Không hợp lệ': 'Khong hop le',
        'Kết quả': 'Ket qua'
    }
    
    # Đọc file
    with open('license/license_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Thay thế text
    for vietnamese, ascii in replacements.items():
        content = content.replace(vietnamese, ascii)
    
    # Ghi lại file
    with open('license/license_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Da thay the text tieng Viet thanh cong!")

if __name__ == "__main__":
    fix_vietnamese()