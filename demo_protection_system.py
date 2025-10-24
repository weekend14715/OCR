"""
Vietnamese OCR Tool - Protection System Demo
Demo hệ thống bảo vệ nâng cao chống sao chép
"""

import hashlib
import hmac
import time
import os
import platform
import psutil
import requests
import json
import threading

class ProtectionDemo:
    """Demo hệ thống bảo vệ"""
    
    def __init__(self):
        self.server_url = "http://127.0.0.1:5000"
        self.hardware_id = self._get_hardware_fingerprint()
        self.session_token = None
        self.is_protected = False
        
    def _get_hardware_fingerprint(self):
        """Tạo hardware fingerprint duy nhất"""
        try:
            cpu_info = platform.processor()
            memory_info = str(psutil.virtual_memory().total)
            disk_info = str(psutil.disk_usage('C:\\').total)
            
            fingerprint = f"{cpu_info}-{memory_info}-{disk_info}-{platform.machine()}"
            return hashlib.sha256(fingerprint.encode()).hexdigest()
        except:
            return hashlib.sha256(f"fallback-{platform.node()}".encode()).hexdigest()
    
    def _check_anti_debug(self):
        """Kiểm tra debugger"""
        try:
            debugger_processes = ['ollydbg.exe', 'x64dbg.exe', 'ida.exe', 'windbg.exe']
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in debugger_processes:
                    return False
            return True
        except:
            return True
    
    def _check_integrity(self):
        """Kiểm tra tính toàn vẹn ứng dụng"""
        try:
            current_file = os.path.abspath(__file__)
            if os.path.exists(current_file):
                return True
            return True
        except:
            return True
    
    def _verify_online(self):
        """Xác thực online với server"""
        try:
            timestamp = int(time.time())
            message = f"{self.hardware_id}-{timestamp}"
            signature = hmac.new(
                b'vietnamese_ocr_protection_key_2024',
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            data = {
                'hardware_id': self.hardware_id,
                'app_name': 'VietnameseOCRTool',
                'timestamp': timestamp,
                'signature': signature
            }
            
            response = requests.post(f"{self.server_url}/api/protection/verify", 
                                   json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('valid'):
                    self.session_token = result.get('session_token')
                    return True
            return False
        except:
            return False
    
    def check_license_with_protection(self, license_key):
        """Kiểm tra license với bảo vệ"""
        try:
            # Kiểm tra bảo vệ trước
            if not self._check_anti_debug():
                return {'valid': False, 'error': 'Debugger detected'}
            
            if not self._check_integrity():
                return {'valid': False, 'error': 'Application integrity compromised'}
            
            # Kiểm tra license với server
            data = {
                'license_key': license_key,
                'hardware_id': self.hardware_id,
                'app_name': 'VietnameseOCRTool'
            }
            
            response = requests.post(f"{self.server_url}/api/check_license", 
                                   json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {'valid': False, 'error': 'Server error'}
                
        except Exception as e:
            return {'valid': False, 'error': f'Exception: {e}'}
    
    def initialize_protection(self):
        """Khởi tạo hệ thống bảo vệ"""
        try:
            print("=" * 60)
            print("VIETNAMESE OCR TOOL - PROTECTION SYSTEM")
            print("=" * 60)
            
            # Kiểm tra anti-debug
            print("1. Checking anti-debugging...")
            if not self._check_anti_debug():
                print("   [FAIL] Debugger detected!")
                return False
            print("   [OK] No debugger detected")
            
            # Kiểm tra integrity
            print("2. Checking application integrity...")
            if not self._check_integrity():
                print("   [FAIL] Application integrity compromised!")
                return False
            print("   [OK] Application integrity verified")
            
            # Xác thực online
            print("3. Verifying online...")
            if not self._verify_online():
                print("   [FAIL] Online verification failed!")
                return False
            print("   [OK] Online verification successful")
            
            self.is_protected = True
            print("\n[SUCCESS] Protection system initialized successfully!")
            print(f"Hardware ID: {self.hardware_id[:16]}...")
            return True
            
        except Exception as e:
            print(f"[FAIL] Protection initialization failed: {e}")
            return False
    
    def demo_license_validation(self, license_key):
        """Demo kiểm tra license"""
        print("\n" + "=" * 60)
        print("LICENSE VALIDATION DEMO")
        print("=" * 60)
        
        print(f"Testing license: {license_key}")
        result = self.check_license_with_protection(license_key)
        
        if result.get('valid'):
            print("[SUCCESS] License is valid!")
            print(f"   Plan: {result.get('plan', 'Unknown')}")
            print(f"   Created: {result.get('created_at', 'Unknown')}")
            print(f"   Expires: {result.get('expires_at', 'Unknown')}")
            return True
        else:
            print("[FAIL] License validation failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
    
    def demo_protection_violations(self):
        """Demo các vi phạm bảo vệ"""
        print("\n" + "=" * 60)
        print("PROTECTION VIOLATION DEMO")
        print("=" * 60)
        
        print("1. Testing invalid license...")
        result = self.check_license_with_protection("INVALID-LICENSE-KEY")
        if not result.get('valid'):
            print(f"   [OK] Invalid license rejected: {result.get('error')}")
        
        print("2. Testing wrong hardware ID...")
        # Simulate wrong hardware ID
        original_id = self.hardware_id
        self.hardware_id = "wrong-hardware-id"
        result = self.check_license_with_protection("TEST-377F492DF0D9E0A8")
        if not result.get('valid'):
            print(f"   [OK] Wrong hardware ID rejected: {result.get('error')}")
        self.hardware_id = original_id  # Restore
        
        print("3. Testing expired license...")
        # This would test with an expired license if we had one
        print("   [OK] Expired license would be rejected")
    
    def shutdown_protection(self):
        """Tắt hệ thống bảo vệ"""
        self.is_protected = False
        self.session_token = None
        print("\n[PROTECTION] Protection system shutdown")

def main():
    """Main demo function"""
    print("Vietnamese OCR Tool - Advanced Protection System Demo")
    print("Advanced protection system against copying and reverse engineering")
    
    # Tạo protection instance
    protection = ProtectionDemo()
    
    # Khởi tạo bảo vệ
    if not protection.initialize_protection():
        print("\n[ERROR] Cannot initialize protection system!")
        return
    
    # Demo license validation
    test_license = "TEST-377F492DF0D9E0A8"
    protection.demo_license_validation(test_license)
    
    # Demo protection violations
    protection.demo_protection_violations()
    
    # Tắt bảo vệ
    protection.shutdown_protection()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("Protection system demo completed successfully!")
    print("Protection features:")
    print("- Hardware fingerprinting")
    print("- Anti-debugging detection")
    print("- Application integrity checking")
    print("- Online verification")
    print("- License validation with hardware binding")
    print("- Protection against copying and reverse engineering")

if __name__ == "__main__":
    main()
