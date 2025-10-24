"""
Test License Activation với key thật từ server
Key test: FBB6-4E8A-3EE0-96E8
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add license module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'license'))

from license.license_activator import LicenseActivator
from license.hardware_id import get_hardware_id

def test_real_key():
    """Test với key thật từ server"""
    
    # Key thật từ server
    REAL_KEY = "FBB6-4E8A-3EE0-96E8"
    
    print("=" * 70)
    print("🧪 TEST LICENSE ACTIVATION WITH REAL KEY")
    print("=" * 70)
    
    # Khởi tạo activator
    activator = LicenseActivator()
    
    print(f"\n📋 Thông tin hệ thống:")
    print(f"   Hardware ID: {activator.hwid[:32]}...")
    print(f"   API Server: {activator.API_BASE_URL}")
    
    print(f"\n🔑 License Key:")
    print(f"   Key: {REAL_KEY}")
    
    # Test 1: Validate format
    print(f"\n✓ Step 1: Validate Format")
    is_valid_format = activator._validate_key_format(REAL_KEY)
    print(f"   Result: {'✅ PASS' if is_valid_format else '❌ FAIL'}")
    
    if not is_valid_format:
        print("\n❌ Key format không hợp lệ!")
        return False
    
    # Test 2: Activate online
    print(f"\n✓ Step 2: Activate Online")
    print(f"   Đang kết nối server...")
    
    result = activator.activate_online(REAL_KEY)
    
    print(f"\n📊 KẾT QUẢ KÍCH HOẠT:")
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    
    if result['success']:
        print(f"\n✅ KÍCH HOẠT THÀNH CÔNG!")
        
        if result.get('data'):
            data = result['data']
            print(f"\n📦 Thông tin License:")
            print(f"   Plan: {data.get('plan', 'N/A')}")
            print(f"   Activated: {data.get('activated', 'N/A')}")
            print(f"   Expires: {data.get('expires', 'Lifetime')}")
    else:
        print(f"\n❌ KÍCH HOẠT THẤT BẠI!")
        print(f"   Lỗi: {result.get('error', 'Unknown')}")
        
        # Chi tiết debug
        if result.get('error'):
            error = result['error']
            print(f"\n🔍 Chi tiết lỗi:")
            
            if 'Invalid license key' in error:
                print(f"   → Key không tồn tại trong database")
                print(f"   → Kiểm tra lại key hoặc tạo key mới từ admin panel")
            
            elif 'already activated on another machine' in error:
                print(f"   → Key đã được kích hoạt trên máy khác")
                print(f"   → Liên hệ admin để chuyển license")
            
            elif 'expired' in error.lower():
                print(f"   → License đã hết hạn")
                print(f"   → Cần gia hạn hoặc mua license mới")
            
            elif 'deactivated' in error.lower():
                print(f"   → License đã bị vô hiệu hóa")
                print(f"   → Liên hệ support")
    
    print("\n" + "=" * 70)
    return result['success']


if __name__ == "__main__":
    try:
        success = test_real_key()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

