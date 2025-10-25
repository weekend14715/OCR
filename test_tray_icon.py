#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script để kiểm tra icon system tray
"""

import sys
import os
from PIL import Image

def test_icon_paths():
    """Test các đường dẫn icon khác nhau"""
    print("=== TEST ICON PATHS ===")
    
    # Test trong development mode
    print("\n1. DEVELOPMENT MODE:")
    print(f"   sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"   Current dir: {os.getcwd()}")
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        print(f"   Executable dir: {base_path}")
    else:
        base_path = os.path.abspath(".")
        print(f"   Script dir: {base_path}")
    
    # Test các file icon
    icon_files = ['app_icon.ico', 'icon.png']
    
    for icon_file in icon_files:
        icon_path = os.path.join(base_path, icon_file)
        print(f"\n   Testing: {icon_path}")
        print(f"   Exists: {os.path.exists(icon_path)}")
        
        if os.path.exists(icon_path):
            try:
                image = Image.open(icon_path)
                print(f"   Size: {image.size}")
                print(f"   Mode: {image.mode}")
                print(f"   Format: {image.format}")
                print(f"   [OK] Icon loaded successfully")
            except Exception as e:
                print(f"   [ERROR] Cannot load icon: {e}")
        else:
            print(f"   [MISSING] File not found")

def test_tray_icon_loading():
    """Test việc load icon cho system tray"""
    print("\n=== TEST TRAY ICON LOADING ===")
    
    try:
        from pystray import Icon
        from PIL import Image
        
        # Simulate the icon loading logic from ocr_tool.py
        ICON_FILE = 'app_icon.ico'
        
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.abspath(".")
            
            icon_path = os.path.join(base_path, ICON_FILE)
            print(f"Tim icon tai: {icon_path}")
            
            if icon_path.endswith('.ico'):
                image = Image.open(icon_path)
            else:
                image = Image.open(icon_path)
                
            print(f"[OK] Icon loaded: {image.size}")
            
            # Test tạo icon (không chạy)
            print("[INFO] Icon ready for system tray")
            
        except FileNotFoundError:
            print(f"[ERROR] Khong tim thay file '{ICON_FILE}'")
            image = Image.new('RGB', (64, 64), 'blue')
            print("[INFO] Using default icon")
        except Exception as e:
            print(f"[ERROR] Loi khi tai icon: {e}")
            image = Image.new('RGB', (64, 64), 'blue')
            print("[INFO] Using default icon")
            
    except ImportError as e:
        print(f"[ERROR] Cannot import pystray: {e}")

if __name__ == "__main__":
    test_icon_paths()
    test_tray_icon_loading()
    print("\n=== TEST COMPLETE ===")
