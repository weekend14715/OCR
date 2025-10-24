#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test va clear license keys
Dung de test cac key khac nhau va clear key cu
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Them thu muc hien tai vao path de import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from license_client_integrated import LicenseClient
    LICENSE_AVAILABLE = True
except ImportError as e:
    print(f"Error: Cannot import LicenseClient: {e}")
    LICENSE_AVAILABLE = False

def get_license_file_path():
    """Lay duong dan file license"""
    app_name = "VietnameseOCRTool"
    config_dir = os.path.join(os.getenv('LOCALAPPDATA'), app_name)
    return os.path.join(config_dir, 'license.json')

def clear_license():
    """Xoa license hien tai"""
    license_file = get_license_file_path()
    
    if os.path.exists(license_file):
        try:
            os.remove(license_file)
            print(f"[OK] Da xoa file license: {license_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Loi khi xoa license: {e}")
            return False
    else:
        print("[INFO] Khong tim thay file license de xoa")
        return True

def backup_license():
    """Backup license hien tai"""
    license_file = get_license_file_path()
    
    if os.path.exists(license_file):
        backup_file = license_file + ".backup"
        try:
            shutil.copy2(license_file, backup_file)
            print(f"[OK] Da backup license: {backup_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Loi khi backup license: {e}")
            return False
    else:
        print("[INFO] Khong co license de backup")
        return True

def restore_license():
    """Khoi phuc license tu backup"""
    license_file = get_license_file_path()
    backup_file = license_file + ".backup"
    
    if os.path.exists(backup_file):
        try:
            shutil.copy2(backup_file, license_file)
            print(f"[OK] Da khoi phuc license tu: {backup_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Loi khi khoi phuc license: {e}")
            return False
    else:
        print("[ERROR] Khong tim thay file backup")
        return False

def test_license_key(license_key):
    """Test mot license key cu the"""
    if not LICENSE_AVAILABLE:
        print("[ERROR] License system khong kha dung")
        return False
    
    print(f"\n{'='*60}")
    print(f"TESTING LICENSE KEY: {license_key}")
    print(f"{'='*60}")
    
    try:
        # Clear license cu
        clear_license()
        
        # Tao license client moi
        client = LicenseClient()
        
        # Test license key
        print(f"[TEST] Dang test key: {license_key}")
        result = client.activate_license(license_key)
        
        if result:
            print("[OK] License key hop le!")
            
            # Lay thong tin license
            info = client.get_license_info()
            if info:
                print(f"[INFO] License Key: {info.get('license_key', 'N/A')}")
                print(f"[INFO] Hardware ID: {info.get('hardware_id', 'N/A')}")
                print(f"[INFO] Status: {info.get('status', 'N/A')}")
            
            return True
        else:
            print("[ERROR] License key khong hop le!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Loi khi test license: {e}")
        return False

def test_multiple_keys(keys):
    """Test nhieu license keys"""
    print(f"\n{'='*60}")
    print("TESTING MULTIPLE LICENSE KEYS")
    print(f"{'='*60}")
    
    results = {}
    
    for i, key in enumerate(keys, 1):
        print(f"\n[TEST {i}/{len(keys)}] Testing: {key}")
        results[key] = test_license_key(key)
        
        if results[key]:
            print(f"[SUCCESS] Key {i} hoat dong!")
        else:
            print(f"[FAILED] Key {i} khong hoat dong!")
    
    # Tong ket
    print(f"\n{'='*60}")
    print("KET QUA TONG KET")
    print(f"{'='*60}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"Tong so keys test: {total_count}")
    print(f"So keys thanh cong: {success_count}")
    print(f"So keys that bai: {total_count - success_count}")
    
    print("\nChi tiet:")
    for key, success in results.items():
        status = "THANH CONG" if success else "THAT BAI"
        print(f"  {key[:20]}... : {status}")
    
    return results

def show_current_license():
    """Hien thi license hien tai"""
    if not LICENSE_AVAILABLE:
        print("[ERROR] License system khong kha dung")
        return
    
    try:
        client = LicenseClient()
        info = client.get_license_info()
        
        if info:
            print(f"\n{'='*60}")
            print("LICENSE HIEN TAI")
            print(f"{'='*60}")
            print(f"License Key: {info.get('license_key', 'N/A')}")
            print(f"Hardware ID: {info.get('hardware_id', 'N/A')}")
            print(f"Status: {info.get('status', 'N/A')}")
            print(f"File: {get_license_file_path()}")
        else:
            print("[INFO] Khong co license nao duoc kich hoat")
            
    except Exception as e:
        print(f"[ERROR] Loi khi lay thong tin license: {e}")

def interactive_menu():
    """Menu tuong tac"""
    while True:
        print(f"\n{'='*60}")
        print("LICENSE KEY TESTER & MANAGER")
        print(f"{'='*60}")
        print("1. Hien thi license hien tai")
        print("2. Clear license hien tai")
        print("3. Backup license hien tai")
        print("4. Khoi phuc license tu backup")
        print("5. Test mot license key")
        print("6. Test nhieu license keys")
        print("7. Test keys mau")
        print("0. Thoat")
        print(f"{'='*60}")
        
        try:
            choice = input("Chon tuy chon (0-7): ").strip()
            
            if choice == "0":
                print("Tam biet!")
                break
            elif choice == "1":
                show_current_license()
            elif choice == "2":
                if clear_license():
                    print("[OK] Da clear license thanh cong!")
                else:
                    print("[ERROR] Khong the clear license!")
            elif choice == "3":
                if backup_license():
                    print("[OK] Da backup license thanh cong!")
                else:
                    print("[ERROR] Khong the backup license!")
            elif choice == "4":
                if restore_license():
                    print("[OK] Da khoi phuc license thanh cong!")
                else:
                    print("[ERROR] Khong the khoi phuc license!")
            elif choice == "5":
                key = input("Nhap license key de test: ").strip()
                if key:
                    test_license_key(key)
                else:
                    print("[ERROR] License key khong duoc de trong!")
            elif choice == "6":
                print("Nhap cac license keys (moi key mot dong, Enter trong de ket thuc):")
                keys = []
                while True:
                    key = input("Key: ").strip()
                    if not key:
                        break
                    keys.append(key)
                
                if keys:
                    test_multiple_keys(keys)
                else:
                    print("[ERROR] Khong co key nao de test!")
            elif choice == "7":
                # Test keys mau
                sample_keys = [
                    "TEST-KEY-12345-ABCDE-67890",
                    "DEMO-KEY-54321-EDCBA-09876",
                    "SAMPLE-KEY-11111-22222-33333",
                    "INVALID-KEY-TEST",
                    "ANOTHER-TEST-KEY-99999"
                ]
                test_multiple_keys(sample_keys)
            else:
                print("[ERROR] Tuy chon khong hop le!")
                
        except KeyboardInterrupt:
            print("\n\nTam biet!")
            break
        except Exception as e:
            print(f"[ERROR] Loi: {e}")

def main():
    """Ham main"""
    print("LICENSE KEY TESTER & MANAGER")
    print("=" * 60)
    
    if not LICENSE_AVAILABLE:
        print("[ERROR] License system khong kha dung!")
        print("Dam bao file license_client_integrated.py co trong thu muc hien tai.")
        return
    
    # Kiem tra tham so dong lenh
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            clear_license()
        elif command == "backup":
            backup_license()
        elif command == "restore":
            restore_license()
        elif command == "show":
            show_current_license()
        elif command == "test" and len(sys.argv) > 2:
            test_license_key(sys.argv[2])
        else:
            print("Su dung:")
            print("  python test_license_keys.py                    # Menu tuong tac")
            print("  python test_license_keys.py clear             # Clear license")
            print("  python test_license_keys.py backup            # Backup license")
            print("  python test_license_keys.py restore           # Restore license")
            print("  python test_license_keys.py show              # Hien thi license")
            print("  python test_license_keys.py test <key>        # Test key cu the")
    else:
        # Chay menu tuong tac
        interactive_menu()

if __name__ == "__main__":
    main()