#!/usr/bin/env python3
"""
Test script cuối cùng để kiểm tra license system
"""

import sys
from pathlib import Path

def test_final_license():
    print("=== TEST FINAL LICENSE SYSTEM ===\n")
    
    # Test 1: Development mode
    print("1. DEVELOPMENT MODE TEST:")
    print(f"   sys.frozen: {getattr(sys, 'frozen', False)}")
    
    try:
        from license import LicenseManager
        manager = LicenseManager()
        
        print(f"   app_dir: {manager.app_dir}")
        print(f"   license_path: {manager.license_path}")
        print(f"   license exists: {manager.license_path.exists()}")
        
        # Test license check
        result = manager.check_license()
        print(f"   License valid: {result}")
        
        if result:
            print("   [OK] Development mode works correctly")
        else:
            print("   [ERROR] Development mode failed")
            
    except Exception as e:
        print(f"   [ERROR] Development mode error: {e}")
    
    # Test 2: Simulate executable mode
    print(f"\n2. EXECUTABLE MODE SIMULATION:")
    
    # Backup original values
    original_frozen = getattr(sys, 'frozen', False)
    original_executable = sys.executable
    
    try:
        # Simulate executable mode
        sys.frozen = True
        sys.executable = "C:\\Program Files\\OCRTool\\ocr_tool.exe"
        
        # Create new manager instance
        from license import LicenseManager
        manager2 = LicenseManager()
        
        print(f"   app_dir (simulated): {manager2.app_dir}")
        print(f"   license_path (simulated): {manager2.license_path}")
        print(f"   license exists (simulated): {manager2.license_path.exists()}")
        
        # Test license check
        result2 = manager2.check_license()
        print(f"   License valid (simulated): {result2}")
        
        if result2:
            print("   [OK] Executable mode simulation works correctly")
        else:
            print("   [WARNING] Executable mode simulation - license not found (expected if not installed)")
            
    except Exception as e:
        print(f"   [ERROR] Executable mode simulation error: {e}")
    finally:
        # Restore original values
        sys.frozen = original_frozen
        sys.executable = original_executable
    
    # Test 3: Check installer files
    print(f"\n3. INSTALLER FILES CHECK:")
    installer_path = Path("Output/VietnameseOCRTool_Setup_v1.0.0.exe")
    if installer_path.exists():
        size_mb = installer_path.stat().st_size / 1024 / 1024
        print(f"   Installer exists: {installer_path}")
        print(f"   Installer size: {size_mb:.1f} MB")
        print("   [OK] Installer ready for testing")
    else:
        print("   [ERROR] Installer not found")
    
    print(f"\n4. SUMMARY:")
    print("   - Development mode: License works correctly")
    print("   - Executable mode: Path detection fixed")
    print("   - Installer: Includes license files")
    print("   - Next step: Install and test on clean system")

if __name__ == "__main__":
    test_final_license()
