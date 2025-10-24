#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Dependencies Installation
Test cài đặt dependencies cho build system
"""

import subprocess
import sys

def test_install_dependencies():
    """Test cài đặt dependencies"""
    print("[PACKAGE] Testing dependencies installation...")
    
    dependencies = [
        'pyinstaller',
        'cryptography', 
        'psutil',
        'requests',
        'numpy',
        'Pillow',
        'pytesseract',
        'keyboard',
        'pyperclip',
        'pystray'
    ]
    
    success_count = 0
    total_deps = len(dependencies)
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep], 
                check=True,
                capture_output=True,
                text=True
            )
            print(f"[OK] Installed {dep}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install {dep}")
            print(f"   Error: {e.stderr}")
        except Exception as e:
            print(f"[ERROR] Unexpected error installing {dep}: {e}")
    
    print(f"\n[SUMMARY] Installation Summary:")
    print(f"   Successfully installed: {success_count}/{total_deps}")
    print(f"   Failed: {total_deps - success_count}/{total_deps}")
    
    if success_count == total_deps:
        print("[SUCCESS] All dependencies installed successfully!")
        return True
    else:
        print("[ERROR] Some dependencies failed to install")
        return False

def test_import_dependencies():
    """Test import các dependencies đã cài"""
    print("\n[IMPORT] Testing imports...")
    
    modules_to_test = [
        ('PyInstaller', 'PyInstaller'),
        ('cryptography', 'cryptography'),
        ('psutil', 'psutil'),
        ('requests', 'requests'),
        ('numpy', 'numpy'),
        ('PIL', 'Pillow'),
        ('pytesseract', 'pytesseract'),
        ('keyboard', 'keyboard'),
        ('pyperclip', 'pyperclip'),
        ('pystray', 'pystray')
    ]
    
    success_count = 0
    total_modules = len(modules_to_test)
    
    for module_name, package_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"[OK] {package_name} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"[ERROR] Failed to import {package_name}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error importing {package_name}: {e}")
    
    print(f"\n[SUMMARY] Import Summary:")
    print(f"   Successfully imported: {success_count}/{total_modules}")
    print(f"   Failed: {total_modules - success_count}/{total_modules}")
    
    return success_count == total_modules

def main():
    """Main test function"""
    print("[TEST] Testing Dependencies for Build System")
    print("=" * 50)
    
    # Test 1: Install dependencies
    install_success = test_install_dependencies()
    
    # Test 2: Test imports
    import_success = test_import_dependencies()
    
    print("\n" + "=" * 50)
    if install_success and import_success:
        print("[SUCCESS] All tests passed! Build system ready.")
        return True
    else:
        print("[ERROR] Some tests failed. Please check errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
