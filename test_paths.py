#!/usr/bin/env python3
"""
Test script để kiểm tra đường dẫn license trong development vs executable
"""

import sys
from pathlib import Path

def test_paths():
    print("=== KIEM TRA DUONG DAN LICENSE ===\n")
    
    # Kiểm tra môi trường
    print(f"Mo truong: {'Executable' if getattr(sys, 'frozen', False) else 'Development'}")
    print(f"sys.executable: {sys.executable}")
    print(f"__file__: {__file__}")
    
    # Test logic đường dẫn
    if getattr(sys, 'frozen', False):
        # Chạy từ executable (PyInstaller)
        app_dir = Path(sys.executable).parent
        print(f"Executable mode - app_dir: {app_dir}")
    else:
        # Chạy từ source code
        app_dir = Path(__file__).parent
        print(f"Development mode - app_dir: {app_dir}")
    
    # Kiểm tra file license
    license_file = app_dir / ".lic"
    print(f"License file path: {license_file}")
    print(f"License file exists: {license_file.exists()}")
    
    # Test LicenseManager
    try:
        from license import LicenseManager
        manager = LicenseManager()
        print(f"\nLicenseManager paths:")
        print(f"   app_dir: {manager.app_dir}")
        print(f"   license_path: {manager.license_path}")
        print(f"   appdata_dir: {manager.appdata_dir}")
        print(f"   checksum_path: {manager.checksum_path}")
        
        # Test check license
        print(f"\nTesting license check...")
        result = manager.check_license()
        print(f"   License valid: {result}")
        
    except Exception as e:
        print(f"Loi khi test LicenseManager: {e}")

if __name__ == "__main__":
    test_paths()
