#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script đơn giản để tạo file icon.png từ app_icon.ico
Chạy script này nếu bạn chưa có file icon.png
"""

import os
import sys

def create_icon_png():
    """Tạo icon.png từ app_icon.ico"""
    
    # Kiểm tra xem đã có icon.png chưa
    if os.path.exists('icon.png'):
        print("✓ File icon.png đã tồn tại!")
        response = input("Bạn có muốn tạo lại không? (y/N): ").strip().lower()
        if response != 'y':
            print("Đã hủy.")
            return True
    
    # Kiểm tra xem có app_icon.ico không
    if not os.path.exists('app_icon.ico'):
        print("❌ Lỗi: Không tìm thấy file app_icon.ico")
        print("Vui lòng đảm bảo file app_icon.ico tồn tại trong thư mục này.")
        return False
    
    try:
        # Import PIL
        from PIL import Image
        
        print("⏳ Đang chuyển đổi app_icon.ico → icon.png...")
        
        # Mở file ICO
        img = Image.open('app_icon.ico')
        
        # Lấy kích thước lớn nhất (ICO có thể chứa nhiều kích thước)
        sizes = img.info.get('sizes', [(64, 64)])
        if sizes:
            max_size = max(sizes, key=lambda s: s[0] * s[1])
            print(f"📐 Kích thước: {max_size[0]}x{max_size[1]} pixels")
        
        # Chuyển đổi và lưu thành PNG
        img.save('icon.png', 'PNG')
        
        print("✅ Đã tạo thành công file icon.png!")
        print(f"📁 Vị trí: {os.path.abspath('icon.png')}")
        
        # Kiểm tra kích thước file
        size_kb = os.path.getsize('icon.png') / 1024
        print(f"📦 Kích thước: {size_kb:.2f} KB")
        
        return True
        
    except ImportError:
        print("❌ Lỗi: Chưa cài đặt thư viện Pillow!")
        print("\nVui lòng cài đặt:")
        print("    pip install Pillow")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False


def main():
    print("=" * 60)
    print("  Công cụ tạo Icon PNG từ ICO")
    print("=" * 60)
    print()
    
    success = create_icon_png()
    
    print()
    print("=" * 60)
    
    if success:
        print("🎉 Hoàn thành!")
        print("\nBạn có thể tiếp tục build ứng dụng bằng:")
        print("    pyinstaller ocr_tool.spec")
        print("hoặc:")
        print("    build_all.bat")
    else:
        print("❌ Thất bại!")
        print("\nVui lòng khắc phục lỗi và thử lại.")
    
    print("=" * 60)
    
    # Pause on Windows
    if sys.platform == 'win32':
        input("\nNhấn Enter để thoát...")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

