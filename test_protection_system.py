"""
Test Protection System
Script để test các tính năng bảo vệ của Vietnamese OCR Tool
"""

import os
import sys
import time
import requests
import json
from protection_system import AdvancedProtection

def test_hardware_fingerprint():
    """Test hardware fingerprint generation"""
    print("🔍 Testing hardware fingerprint...")
    
    protection = AdvancedProtection()
    fingerprint = protection._get_hardware_fingerprint()
    
    print(f"✅ Hardware fingerprint: {fingerprint[:16]}...")
    print(f"   Length: {len(fingerprint)}")
    
    # Test uniqueness
    fingerprint2 = protection._get_hardware_fingerprint()
    if fingerprint == fingerprint2:
        print("✅ Fingerprint is consistent")
    else:
        print("❌ Fingerprint is inconsistent")
    
    return fingerprint

def test_anti_debug():
    """Test anti-debugging functionality"""
    print("\n🛡️ Testing anti-debugging...")
    
    protection = AdvancedProtection()
    is_clean = protection._check_anti_debug()
    
    if is_clean:
        print("✅ No debugger detected")
    else:
        print("❌ Debugger detected")
    
    return is_clean

def test_integrity_check():
    """Test application integrity checking"""
    print("\n🔍 Testing integrity check...")
    
    protection = AdvancedProtection()
    is_intact = protection._check_integrity()
    
    if is_intact:
        print("✅ Application integrity verified")
    else:
        print("❌ Application integrity compromised")
    
    return is_intact

def test_encryption():
    """Test encryption/decryption functionality"""
    print("\n🔐 Testing encryption...")
    
    protection = AdvancedProtection()
    
    # Test data
    test_data = "This is a test message for encryption"
    
    # Encrypt
    encrypted = protection._encrypt_data(test_data)
    print(f"✅ Encrypted: {encrypted[:32]}...")
    
    # Decrypt
    decrypted = protection._decrypt_data(encrypted)
    print(f"✅ Decrypted: {decrypted}")
    
    # Verify
    if decrypted == test_data:
        print("✅ Encryption/Decryption successful")
        return True
    else:
        print("❌ Encryption/Decryption failed")
        return False

def test_license_server_connection():
    """Test connection to license server"""
    print("\n🌐 Testing license server connection...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ License server is running")
            return True
        else:
            print(f"❌ License server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to license server")
        print("   Make sure license server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ License server error: {e}")
        return False

def test_protection_verification():
    """Test protection verification with server"""
    print("\n🔐 Testing protection verification...")
    
    protection = AdvancedProtection()
    
    try:
        # Test protection verification
        result = protection._verify_online()
        
        if result:
            print("✅ Protection verification successful")
            print(f"   Session token: {protection.session_token[:16]}...")
            return True
        else:
            print("❌ Protection verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Protection verification error: {e}")
        return False

def test_license_validation():
    """Test license validation with protection"""
    print("\n🎫 Testing license validation...")
    
    protection = AdvancedProtection()
    
    # Test with dummy license key
    test_license = "TEST-1234-5678-9012"
    
    try:
        result = protection.check_license_with_protection(test_license)
        
        print(f"✅ License validation result: {result.get('valid', False)}")
        if not result.get('valid'):
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return result.get('valid', False)
        
    except Exception as e:
        print(f"❌ License validation error: {e}")
        return False

def test_protection_thread():
    """Test protection thread functionality"""
    print("\n🔄 Testing protection thread...")
    
    protection = AdvancedProtection()
    
    try:
        # Initialize protection
        if protection.initialize_protection():
            print("✅ Protection system initialized")
            
            # Wait a bit to see if thread is running
            time.sleep(2)
            
            if protection.is_protected:
                print("✅ Protection thread is running")
                
                # Shutdown protection
                protection.shutdown_protection()
                print("✅ Protection system shutdown")
                return True
            else:
                print("❌ Protection thread not running")
                return False
        else:
            print("❌ Failed to initialize protection system")
            return False
            
    except Exception as e:
        print(f"❌ Protection thread error: {e}")
        return False

def run_all_tests():
    """Chạy tất cả các test"""
    print("🧪 Vietnamese OCR Tool - Protection System Tests")
    print("=" * 60)
    
    tests = [
        ("Hardware Fingerprint", test_hardware_fingerprint),
        ("Anti-Debug", test_anti_debug),
        ("Integrity Check", test_integrity_check),
        ("Encryption", test_encryption),
        ("License Server Connection", test_license_server_connection),
        ("Protection Verification", test_protection_verification),
        ("License Validation", test_license_validation),
        ("Protection Thread", test_protection_thread),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Protection system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Vietnamese OCR Tool - Protection System Test")
        print("\nUsage:")
        print("  python test_protection_system.py          # Run all tests")
        print("  python test_protection_system.py --help   # Show this help")
        print("\nPrerequisites:")
        print("  - License server running on port 5000")
        print("  - All dependencies installed")
        print("  - Protection system modules available")
        return
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
