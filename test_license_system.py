"""
Script test hệ thống license
"""

from license import LicenseManager

def test_license():
    print("="*70)
    print("🧪 TEST HỆ THỐNG BẢN QUYỀN")
    print("="*70)
    
    manager = LicenseManager()
    
    print(f"\n📍 Thông tin hệ thống:")
    print(f"   HWID: {manager.hwid}")
    print(f"   License file: {manager.license_path}")
    print(f"   Backup file: {manager.checksum_path}")
    print(f"   Registry: {manager.REGISTRY_PATH}")
    
    print(f"\n🔍 Kiểm tra license hiện tại...")
    is_valid = manager.check_license()
    
    if is_valid:
        print("\n" + "="*70)
        print("✅ TEST PASSED - License hợp lệ!")
        print("="*70)
        return True
    else:
        print("\n" + "="*70)
        print("❌ TEST FAILED - License không hợp lệ hoặc chưa kích hoạt")
        print("="*70)
        return False

if __name__ == "__main__":
    test_license()
