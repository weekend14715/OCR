#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test nhanh license keys
"""

import os
import sys

# Them thu muc hien tai vao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from license_client_integrated import LicenseClient
    LICENSE_AVAILABLE = True
except ImportError as e:
    print(f"Error: {e}")
    LICENSE_AVAILABLE = False

def clear_and_test_key(key):
    """Clear license cu va test key moi"""
    if not LICENSE_AVAILABLE:
        print("[ERROR] License system khong kha dung")
        return False
    
    # Clear license cu
    license_file = os.path.join(os.getenv('LOCALAPPDATA'), 'VietnameseOCRTool', 'license.json')
    if os.path.exists(license_file):
        try:
            os.remove(license_file)
            print(f"[CLEAR] Da xoa license cu")
        except:
            pass
    
    # Test key moi
    try:
        client = LicenseClient()
        result = client.activate_license(key)
        
        if result:
            print(f"[OK] Key '{key}' hoat dong!")
            info = client.get_license_info()
            if info:
                print(f"Hardware ID: {info.get('hardware_id', 'N/A')}")
            return True
        else:
            print(f"[FAIL] Key '{key}' khong hoat dong!")
            return False
    except Exception as e:
        print(f"[ERROR] Loi: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Su dung: python quick_test_keys.py <license_key>")
        print("Vi du: python quick_test_keys.py TEST-KEY-12345")
        return
    
    key = sys.argv[1]
    clear_and_test_key(key)

if __name__ == "__main__":
    main()