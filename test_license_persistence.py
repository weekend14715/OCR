#!/usr/bin/env python3
"""
Test script để kiểm tra license persistence
"""

import sys
from pathlib import Path

def test_license_persistence():
    print("=== TEST LICENSE PERSISTENCE ===\n")
    
    # Test trong development mode
    print("1. DEVELOPMENT MODE:")
    print(f"   sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"   sys.executable: {sys.executable}")
    print(f"   __file__: {__file__}")
    
    # Test đường dẫn
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
        print(f"   app_dir (executable): {app_dir}")
    else:
        app_dir = Path(__file__).parent
        print(f"   app_dir (development): {app_dir}")
    
    license_file = app_dir / ".lic"
    print(f"   license_file: {license_file}")
    print(f"   license exists: {license_file.exists()}")
    
    # Test LicenseManager
    try:
        from license import LicenseManager
        manager = LicenseManager()
        
        print(f"\n2. LICENSE MANAGER PATHS:")
        print(f"   app_dir: {manager.app_dir}")
        print(f"   license_path: {manager.license_path}")
        print(f"   appdata_dir: {manager.appdata_dir}")
        print(f"   checksum_path: {manager.checksum_path}")
        
        # Test check license
        print(f"\n3. LICENSE CHECK:")
        result = manager.check_license()
        print(f"   License valid: {result}")
        
        if result:
            print(f"   License file exists: {manager.license_path.exists()}")
            print(f"   Registry exists: {manager._read_registry() is not None}")
            print(f"   Backup exists: {manager._read_backup() is not None}")
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    print(f"\n4. SIMULATION EXECUTABLE MODE:")
    # Simulate executable mode
    sys.frozen = True
    sys.executable = "C:\\Program Files\\OCRTool\\ocr_tool.exe"
    
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
        print(f"   app_dir (simulated): {app_dir}")
        license_file = app_dir / ".lic"
        print(f"   license_file (simulated): {license_file}")
        print(f"   license exists (simulated): {license_file.exists()}")

if __name__ == "__main__":
    test_license_persistence()
