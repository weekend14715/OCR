#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xóa hotkey đã lưu
Vietnamese OCR Tool - Clear Saved Hotkey
"""

import os
import sys
import shutil
from pathlib import Path

def clear_hotkey():
    """Xóa hotkey đã lưu."""
    print("=" * 50)
    print("        XOA PHIM TAT DA LUU")
    print("=" * 50)
    print()
    
    # Lấy đường dẫn thư mục config
    app_name = "VietnameseOCRTool"
    config_dir = Path(os.getenv('LOCALAPPDATA')) / app_name
    config_file = config_dir / 'config.ini'
    
    print("[INFO] Dang kiem tra thu muc config...")
    
    # Kiểm tra thư mục config
    if not config_dir.exists():
        print(f"[WARNING] Thu muc config khong ton tai: {config_dir}")
        print("[INFO] Co the ban chua su dung phim tat bao gio.")
        input("Nhan Enter de thoat...")
        return False
    
    print(f"[OK] Tim thay thu muc config: {config_dir}")
    print()
    
    # Kiểm tra file config.ini
    if not config_file.exists():
        print(f"[WARNING] File config.ini khong ton tai: {config_file}")
        print("[INFO] Co the ban chua luu phim tat bao gio.")
        input("Nhan Enter de thoat...")
        return False
    
    print("[OK] Tim thay file config.ini")
    print()
    
    # Hiển thị nội dung file config hiện tại
    print("[INFO] Noi dung file config hien tai:")
    print("-" * 40)
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"[ERROR] Khong the doc file: {e}")
    print("-" * 40)
    print()
    
    # Xác nhận xóa
    confirm = input("Ban co chac chan muon xoa phim tat da luu? (y/n): ")
    if confirm.lower() != 'y':
        print("[INFO] Huy bo thao tac.")
        input("Nhan Enter de thoat...")
        return False
    
    print()
    print("[INFO] Dang xoa phim tat...")
    
    try:
        # Xóa file config.ini
        config_file.unlink()
        print("[OK] Da xoa file config.ini thanh cong!")
        
        # Kiểm tra xem thư mục có còn file nào khác không
        remaining_files = [f for f in config_dir.iterdir() if f.is_file() and f.name != 'config.ini']
        
        if not remaining_files:
            print("[INFO] Thu muc config da trong, dang xoa thu muc...")
            shutil.rmtree(config_dir)
            print("[OK] Da xoa thu muc config thanh cong!")
        else:
            print(f"[INFO] Thu muc config van con {len(remaining_files)} file khac, giu lai thu muc.")
            print("Cac file con lai:")
            for file in remaining_files:
                print(f"  - {file.name}")
        
    except Exception as e:
        print(f"[ERROR] Loi khi xoa: {e}")
        input("Nhan Enter de thoat...")
        return False
    
    print()
    print("=" * 50)
    print("[SUCCESS] DA XOA PHIM TAT THANH CONG!")
    print("=" * 50)
    print()
    print("[INFO] Cac thao tac da thuc hien:")
    print("- Xoa file config.ini chua phim tat")
    print("- Xoa thu muc config neu trong")
    print()
    print("[INFO] Lan chay tiep theo, ung dung se yeu cau chon phim tat moi.")
    print()
    input("Nhan Enter de thoat...")
    return True

if __name__ == "__main__":
    try:
        clear_hotkey()
    except KeyboardInterrupt:
        print("\n[INFO] Thoat chuong trinh.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Loi khong mong muon: {e}")
        input("Nhan Enter de thoat...")
        sys.exit(1)
