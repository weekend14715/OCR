"""
Script hủy kích hoạt license
Sử dụng khi muốn chuyển license sang máy khác
"""

import sys
import io

# Fix encoding cho Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from license import LicenseManager

def deactivate():
    print("\n" + "="*70)
    print("HUY KICH HOAT LICENSE")
    print("="*70)
    print("\nCANH BAO: Thao tac nay se xoa toan bo license tren may nay!")
    print("Ban se can nhap lai license key de su dung ung dung.\n")
    
    confirm = input("Ban co chac chan muon huy kich hoat? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\nDa huy thao tac.")
        return
    
    print("\nDang huy kich hoat...")
    
    manager = LicenseManager()
    success = manager.deactivate_license()
    
    if success:
        print("\n" + "="*70)
        print("OK - Da huy kich hoat thanh cong!")
        print("="*70)
        print("\nBan co the su dung license key nay de kich hoat tren may khac.")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("CANH BAO - Mot so thanh phan khong the xoa")
        print("="*70)
        print("\nVui long thu lai hoac xoa thu cong:")
        print(f"  1. File: {manager.license_path}")
        print(f"  2. Registry: {manager.REGISTRY_PATH}")
        print(f"  3. Backup: {manager.checksum_path}")
        print("="*70 + "\n")

if __name__ == "__main__":
    try:
        deactivate()
    except Exception as e:
        print(f"\nLOI: {e}\n")

