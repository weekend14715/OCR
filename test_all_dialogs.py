#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test tat ca cac cua so license
"""

import sys
import os

# Them thu muc hien tai vao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_license_dialog():
    """Test license dialog"""
    try:
        from license_dialog import show_license_dialog
        print("=== TEST LICENSE DIALOG ===")
        print("Dang mo cua so nhap license...")
        result = show_license_dialog()
        print(f"Ket qua: {result}")
        print("OK - Cua so co the dong duoc!")
        return True
    except Exception as e:
        print(f"LOI: {e}")
        return False

def test_license_info():
    """Test license info window"""
    try:
        from ocr_tool import show_license_info
        print("\n=== TEST LICENSE INFO WINDOW ===")
        print("Dang mo cua so thong tin license...")
        show_license_info()
        print("OK - Cua so co the dong duoc!")
        return True
    except Exception as e:
        print(f"LOI: {e}")
        return False

def main():
    print("=" * 50)
    print("TEST TAT CA CAC CUA SO LICENSE")
    print("=" * 50)
    
    # Test license dialog
    dialog_ok = test_license_dialog()
    
    # Test license info
    info_ok = test_license_info()
    
    print("\n" + "=" * 50)
    print("KET QUA TEST:")
    print(f"License Dialog: {'PASS' if dialog_ok else 'FAIL'}")
    print(f"License Info: {'PASS' if info_ok else 'FAIL'}")
    print("=" * 50)
    
    if dialog_ok and info_ok:
        print("TAT CA CAC CUA SO DEU HOAT DONG TOT!")
    else:
        print("CO MOT SO CUA SO CO VAN DE!")

if __name__ == "__main__":
    main()
