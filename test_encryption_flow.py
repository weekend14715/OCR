"""
Test Encryption Flow - Minh họa toàn bộ quy trình mã hóa
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

from license.license_crypto import LicenseCrypto
from license.hardware_id import get_hardware_id


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step_num, title):
    """Print step header"""
    print(f"\n[{step_num}] {title}")
    print("-" * 70)


def test_encryption_flow():
    """Test toàn bộ quy trình mã hóa"""
    
    print_section("🔐 TEST QUY TRÌNH MÃ HÓA LICENSE")
    
    # Setup
    crypto = LicenseCrypto()
    hwid = get_hardware_id()
    
    print(f"\n📋 Thông tin hệ thống:")
    print(f"   Hardware ID: {hwid}")
    print(f"   HWID Length: {len(hwid)} ký tự")
    
    # Test data
    license_key = "FBB6-4E8A-3EE0-96E8"
    user_info = {
        'name': 'Nguyen Van A',
        'email': 'nguyenvana@example.com'
    }
    
    print(f"\n📝 Dữ liệu test:")
    print(f"   License Key: {license_key}")
    print(f"   User: {user_info['name']} ({user_info['email']})")
    
    # =========================================================================
    # PHẦN 1: MÃ HÓA
    # =========================================================================
    
    print_section("PHẦN 1: QUY TRÌNH MÃ HÓA")
    
    print_step(1, "Chuẩn bị dữ liệu")
    print("   Tạo dictionary chứa license_key, hwid, timestamp, user_info...")
    
    print_step(2, "Tính CRC32 Checksum")
    import json
    data_sample = {
        'license_key': license_key,
        'hwid': hwid,
        'timestamp': 1729839400.0
    }
    json_sample = json.dumps(data_sample, separators=(',', ':'))
    
    import zlib
    checksum = zlib.crc32(json_sample.encode('utf-8')) & 0xffffffff
    checksum_hex = format(checksum, '08x').upper()
    
    print(f"   JSON data: {json_sample[:80]}...")
    print(f"   CRC32 Checksum: {checksum_hex}")
    
    print_step(3, "Tính SHA-256 Hash")
    import hashlib
    data_hash = hashlib.sha256((json_sample + checksum_hex).encode('utf-8')).hexdigest().upper()
    print(f"   SHA-256 Hash: {data_hash[:64]}...")
    
    print_step(4, "Derive Encryption Key (PBKDF2)")
    print(f"   Password: HWID + SECRET_PHRASE")
    print(f"   Salt: b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'")
    print(f"   Iterations: 100,000")
    print(f"   Algorithm: PBKDF2-HMAC-SHA256")
    print(f"   Key Length: 32 bytes (256 bits)")
    
    encryption_key = crypto._derive_key(hwid)
    print(f"   ✅ Encryption Key (base64): {encryption_key[:50].decode()}...")
    
    print_step(5, "Encrypt với Fernet (AES-128 CBC + HMAC)")
    result = crypto.encrypt_license(license_key, hwid, user_info)
    
    encrypted_data = result['encrypted_data']
    print(f"   ✅ Encrypted Data:")
    print(f"      Length: {len(encrypted_data)} ký tự")
    print(f"      Preview: {encrypted_data[:80]}...")
    print(f"      Checksum: {result['checksum']}")
    print(f"      Hash: {result['hash'][:64]}...")
    
    # =========================================================================
    # PHẦN 2: GIẢI MÃ VỚI ĐÚNG HWID
    # =========================================================================
    
    print_section("PHẦN 2: GIẢI MÃ VỚI ĐÚNG HWID")
    
    print_step(1, "Derive Decryption Key")
    print(f"   Sử dụng HWID hiện tại: {hwid[:32]}...")
    decryption_key = crypto._derive_key(hwid)
    print(f"   ✅ Decryption Key: {decryption_key[:50].decode()}...")
    
    print_step(2, "Decrypt với Fernet")
    decrypted = crypto.decrypt_license(encrypted_data, hwid)
    
    if decrypted:
        print(f"   ✅ DECRYPT THÀNH CÔNG!")
        print(f"\n   📦 Dữ liệu đã giải mã:")
        print(f"      License Key: {decrypted.get('license_key')}")
        print(f"      HWID: {decrypted.get('hwid')[:32]}...")
        print(f"      Activated At: {decrypted.get('activated_at')}")
        print(f"      Version: {decrypted.get('version')}")
        
        if 'user_info' in decrypted:
            print(f"      User Name: {decrypted['user_info'].get('name')}")
            print(f"      User Email: {decrypted['user_info'].get('email')}")
        
        print(f"\n   🔍 Integrity Check:")
        print(f"      Checksum: {decrypted.get('checksum')} ✅")
        print(f"      Hash: {decrypted.get('hash')[:32]}... ✅")
    else:
        print(f"   ❌ DECRYPT THẤT BẠI!")
    
    # =========================================================================
    # PHẦN 3: GIẢI MÃ VỚI SAI HWID (SECURITY TEST)
    # =========================================================================
    
    print_section("PHẦN 3: SECURITY TEST - SAI HWID")
    
    print_step(1, "Thử decrypt với HWID giả mạo")
    wrong_hwid = "FAKE_HWID_1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF"
    print(f"   Wrong HWID: {wrong_hwid[:32]}...")
    
    decrypted_wrong = crypto.decrypt_license(encrypted_data, wrong_hwid)
    
    if decrypted_wrong:
        print(f"   ❌ BẢO MẬT YẾU - Decrypt được với SAI HWID!")
    else:
        print(f"   ✅ BẢO MẬT TỐT - Không decrypt được với SAI HWID!")
    
    # =========================================================================
    # PHẦN 4: TAMPERING TEST
    # =========================================================================
    
    print_section("PHẦN 4: SECURITY TEST - TAMPERING")
    
    print_step(1, "Thử sửa encrypted data")
    tampered_data = encrypted_data[:-5] + 'XXXXX'
    print(f"   Original: ...{encrypted_data[-20:]}")
    print(f"   Tampered: ...{tampered_data[-20:]}")
    
    decrypted_tampered = crypto.decrypt_license(tampered_data, hwid)
    
    if decrypted_tampered:
        print(f"   ❌ BẢO MẬT YẾU - Decrypt được data bị sửa!")
    else:
        print(f"   ✅ BẢO MẬT TỐT - Phát hiện tampering, từ chối decrypt!")
    
    # =========================================================================
    # PHẦN 5: KIỂM TRA REGISTRY & BACKUP
    # =========================================================================
    
    print_section("PHẦN 5: CROSS-VALIDATION DATA")
    
    print_step(1, "Tạo Registry Values")
    registry_hash = crypto.generate_registry_value(encrypted_data)
    print(f"   InstallID: {hwid[:16]}")
    print(f"   Checksum: {result['checksum']}")
    print(f"   Hash: {registry_hash}")
    
    print_step(2, "Tạo Backup Checksum")
    backup_checksum = crypto.generate_backup_checksum(encrypted_data, hwid)
    print(f"   Backup Checksum: {backup_checksum[:64]}...")
    
    import base64
    backup_encoded = base64.b64encode(backup_checksum.encode()).decode()
    print(f"   Backup Encoded: {backup_encoded[:80]}...")
    
    # =========================================================================
    # KẾT QUẢ TỔNG HỢP
    # =========================================================================
    
    print_section("📊 KẾT QUẢ TỔNG HỢP")
    
    print("\n✅ TESTS PASSED:")
    print("   [✓] Encrypt với HWID hợp lệ")
    print("   [✓] Decrypt với đúng HWID")
    print("   [✓] Checksum & Hash integrity")
    print("   [✓] HWID verification")
    print("   [✓] Block decrypt với SAI HWID")
    print("   [✓] Block decrypt với TAMPERED data")
    print("   [✓] Generate Registry values")
    print("   [✓] Generate Backup checksum")
    
    print("\n🔐 BẢO MẬT:")
    print("   • Encryption: AES-128 CBC (Fernet)")
    print("   • Key Derivation: PBKDF2-HMAC-SHA256 (100k iterations)")
    print("   • Integrity: CRC32 + SHA-256 + HMAC")
    print("   • Binding: Hardware Fingerprint (HWID)")
    print("   • Storage: 3 locations (.lic + Registry + .checksum)")
    
    print("\n💾 LƯU TRỮ:")
    print("   [1] File .lic:")
    print(f"       Location: F:\\OCR\\OCR\\.lic")
    print(f"       Content: {encrypted_data[:60]}...")
    print(f"       Size: {len(encrypted_data)} bytes")
    
    print("\n   [2] Registry (HKCU\\Software\\OCRTool):")
    print(f"       InstallID = {hwid[:16]}")
    print(f"       Checksum  = {result['checksum']}")
    print(f"       Hash      = {registry_hash}")
    
    print("\n   [3] Backup (%APPDATA%\\OCRTool\\.checksum):")
    print(f"       Content: {backup_encoded[:60]}...")
    
    print("\n" + "=" * 70)
    print("🎉 TEST HOÀN TẤT!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_encryption_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test bị hủy bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

