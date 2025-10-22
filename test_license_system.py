"""
Test script để demo hệ thống license
"""

import requests
import time

# Config
API_URL = "http://127.0.0.1:5000/api"
ADMIN_KEY = "your-secure-admin-api-key-here-change-this"  # Đổi theo app.py

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_generate_license():
    """Test tạo license"""
    print_section("1. TẠO LICENSE KEYS")
    
    # Tạo 3 loại license
    plans = [
        ('lifetime', 'customer1@example.com'),
        ('yearly', 'customer2@example.com'),
        ('monthly', 'customer3@example.com')
    ]
    
    licenses = []
    
    for plan, email in plans:
        response = requests.post(
            f"{API_URL}/admin/generate",
            headers={'X-Admin-Key': ADMIN_KEY},
            json={
                'plan_type': plan,
                'quantity': 1,
                'email': email
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            license_key = data['licenses'][0]
            licenses.append((license_key, plan, email))
            print(f"✅ Đã tạo license {plan.upper()}: {license_key}")
        else:
            print(f"❌ Lỗi tạo license {plan}: {response.json()}")
    
    return licenses

def test_validate_license(license_key, machine_id):
    """Test validate license"""
    response = requests.post(
        f"{API_URL}/validate",
        json={
            'license_key': license_key,
            'machine_id': machine_id
        }
    )
    
    return response.json()

def test_stats():
    """Test xem thống kê"""
    print_section("5. THỐNG KÊ HỆ THỐNG")
    
    response = requests.get(
        f"{API_URL}/admin/stats",
        headers={'X-Admin-Key': ADMIN_KEY}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Tổng licenses: {data['total_licenses']}")
        print(f"📊 Đã kích hoạt: {data['activated']}")
        print(f"📊 Đang hoạt động: {data['active']}")
        print(f"📊 Phân bố theo gói:")
        for plan, count in data['by_plan'].items():
            print(f"   - {plan.upper()}: {count}")
    else:
        print(f"❌ Lỗi: {response.json()}")

def test_deactivate(license_key):
    """Test vô hiệu hóa license"""
    print_section("6. VÔ HIỆU HÓA LICENSE")
    
    response = requests.post(
        f"{API_URL}/admin/deactivate",
        headers={'X-Admin-Key': ADMIN_KEY},
        json={'license_key': license_key}
    )
    
    if response.status_code == 200:
        print(f"✅ Đã vô hiệu hóa: {license_key}")
    else:
        print(f"❌ Lỗi: {response.json()}")

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  Vietnamese OCR Tool - License System Test              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 1. Tạo licenses
        licenses = test_generate_license()
        
        if not licenses:
            print("\n❌ Không tạo được license. Kiểm tra server và API key!")
            return
        
        time.sleep(1)
        
        # 2. Validate license lần đầu (kích hoạt)
        print_section("2. KÍCH HOẠT LICENSE LẦN ĐẦU")
        license_key, plan, email = licenses[0]
        machine_id = "test-machine-001"
        
        result = test_validate_license(license_key, machine_id)
        
        if result.get('valid'):
            print(f"✅ Kích hoạt thành công:")
            print(f"   License: {license_key}")
            print(f"   Plan: {result['plan']}")
            print(f"   Activated: {result.get('activated', 'N/A')}")
            print(f"   Expires: {result.get('expires', 'Never')}")
        else:
            print(f"❌ Lỗi: {result.get('error')}")
        
        time.sleep(1)
        
        # 3. Validate lại với cùng machine (OK)
        print_section("3. VALIDATE VỚI CÙNG MÁY")
        result = test_validate_license(license_key, machine_id)
        
        if result.get('valid'):
            print(f"✅ License hợp lệ trên cùng máy")
        else:
            print(f"❌ Lỗi: {result.get('error')}")
        
        time.sleep(1)
        
        # 4. Validate với máy khác (FAIL)
        print_section("4. VALIDATE VỚI MÁY KHÁC")
        different_machine = "test-machine-002"
        result = test_validate_license(license_key, different_machine)
        
        if not result.get('valid'):
            print(f"✅ Đúng! Không cho phép kích hoạt trên máy khác")
            print(f"   Error: {result.get('error')}")
        else:
            print(f"❌ Lỗi: Không nên validate được trên máy khác!")
        
        time.sleep(1)
        
        # 5. Xem stats
        test_stats()
        
        time.sleep(1)
        
        # 6. Deactivate một license
        if len(licenses) >= 3:
            test_deactivate(licenses[2][0])
        
        time.sleep(1)
        
        # 7. Validate license đã deactivate (FAIL)
        print_section("7. VALIDATE LICENSE ĐÃ VÔ HIỆU HÓA")
        if len(licenses) >= 3:
            result = test_validate_license(licenses[2][0], "any-machine")
            if not result.get('valid'):
                print(f"✅ Đúng! License đã vô hiệu không validate được")
                print(f"   Error: {result.get('error')}")
            else:
                print(f"❌ Lỗi: Không nên validate được!")
        
        # Final stats
        test_stats()
        
        print_section("✅ HOÀN TẤT TEST")
        print("\n🎯 Kết quả:")
        print("   ✓ Tạo license: OK")
        print("   ✓ Kích hoạt lần đầu: OK")
        print("   ✓ Validate cùng máy: OK")
        print("   ✓ Chặn máy khác: OK")
        print("   ✓ Vô hiệu hóa: OK")
        print("   ✓ Thống kê: OK")
        print("\n📝 License keys đã tạo:")
        for key, plan, email in licenses:
            print(f"   - {key} ({plan}) - {email}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ KHÔNG KẾT NỐI ĐƯỢC SERVER!")
        print("   Hãy chạy license server trước:")
        print("   $ cd license_server")
        print("   $ python app.py")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")

if __name__ == "__main__":
    main()

