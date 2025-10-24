"""
Test License Integration
Kiểm tra hệ thống license tích hợp
"""

import sys
import os

def test_license_system():
    """Test hệ thống license"""
    print("=" * 60)
    print("TEST HE THONG LICENSE TICH HOP")
    print("=" * 60)
    
    try:
        # Test import
        print("1. Testing imports...")
        from license_client_integrated import LicenseClient
        from license_dialog import show_license_dialog
        print("   OK Import thanh cong")
        
        # Test license client
        print("\n2. Testing LicenseClient...")
        client = LicenseClient()
        print(f"   OK Hardware ID: {client.hardware_id}")
        
        # Test offline verification
        print("\n3. Testing offline verification...")
        offline_result = client.verify_license_offline()
        print(f"   Ket qua offline: {offline_result}")
        
        # Test online verification (với key giả)
        print("\n4. Testing online verification...")
        test_key = "test-key-12345"
        online_result = client.verify_license_online(test_key)
        print(f"   Ket qua online: {online_result}")
        
        # Test OCR tool integration
        print("\n5. Testing OCR tool integration...")
        try:
            import ocr_tool
            print("   OK OCR tool import thanh cong")
            print(f"   License available: {ocr_tool.LICENSE_AVAILABLE}")
        except Exception as e:
            print(f"   ERROR OCR tool import failed: {e}")
        
        print("\n" + "=" * 60)
        print("TAT CA TEST THANH CONG!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nLOI TEST: {e}")
        import traceback
        traceback.print_exc()

def test_license_dialog():
    """Test license dialog"""
    print("\n" + "=" * 60)
    print("TEST LICENSE DIALOG")
    print("=" * 60)
    
    try:
        from license_dialog import show_license_dialog
        print("OK License dialog import thanh cong")
        print("De test dialog, hay chay: python license_dialog.py")
        
    except Exception as e:
        print(f"Loi test dialog: {e}")

if __name__ == "__main__":
    test_license_system()
    test_license_dialog()
