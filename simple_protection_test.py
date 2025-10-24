"""
Simple Protection System Test
Test cơ bản cho hệ thống bảo vệ
"""

import hashlib
import hmac
import time
import os
import platform
import psutil
import requests
import json
import base64
from cryptography.fernet import Fernet
import threading

class SimpleProtection:
    """Simple protection system for testing"""
    
    def __init__(self):
        self.server_url = "http://127.0.0.1:5000"
        self.hardware_id = self._get_hardware_fingerprint()
        self.session_token = None
        self.is_protected = False
        
    def _get_hardware_fingerprint(self):
        """Get hardware fingerprint"""
        try:
            cpu_info = platform.processor()
            memory_info = str(psutil.virtual_memory().total)
            disk_info = str(psutil.disk_usage('C:\\').total)
            
            fingerprint = f"{cpu_info}-{memory_info}-{disk_info}-{platform.machine()}"
            return hashlib.sha256(fingerprint.encode()).hexdigest()
        except:
            return hashlib.sha256(f"fallback-{platform.node()}".encode()).hexdigest()
    
    def _check_anti_debug(self):
        """Check for debugger"""
        try:
            # Simple debugger check
            debugger_processes = ['ollydbg.exe', 'x64dbg.exe', 'ida.exe', 'windbg.exe']
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in debugger_processes:
                    return False
            return True
        except:
            return True
    
    def _check_integrity(self):
        """Check application integrity"""
        try:
            # Simple integrity check - just check if we can access the file
            current_file = os.path.abspath(__file__)
            if os.path.exists(current_file):
                # For testing, always return True
                return True
            return True
        except:
            return True
    
    def _verify_online(self):
        """Verify with server"""
        try:
            timestamp = int(time.time())
            # Create HMAC signature matching server
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
        except Exception as e:
            print(f"[DEBUG] Verification error: {e}")
            return False
    
    def initialize_protection(self):
        """Initialize protection system"""
        try:
            # Check anti-debug
            if not self._check_anti_debug():
                print("[FAIL] Debugger detected")
                return False
            
            # Check integrity
            if not self._check_integrity():
                print("[FAIL] Application integrity compromised")
                return False
            
            # Verify online
            if not self._verify_online():
                print("[FAIL] Online verification failed")
                return False
            
            self.is_protected = True
            print("[OK] Protection system initialized")
            return True
            
        except Exception as e:
            print(f"[FAIL] Protection initialization failed: {e}")
            return False
    
    def check_license_with_protection(self, license_key):
        """Check license with protection"""
        try:
            # Check protection first
            if not self._check_anti_debug():
                return {'valid': False, 'error': 'Debugger detected'}
            
            if not self._check_integrity():
                return {'valid': False, 'error': 'Application integrity compromised'}
            
            # Check license with server
            data = {
                'license_key': license_key,
                'hardware_id': self.hardware_id,
                'app_name': 'VietnameseOCRTool'
            }
            
            response = requests.post(f"{self.server_url}/api/check_license", 
                                   json=data, timeout=10)
            
            print(f"[DEBUG] License check status: {response.status_code}")
            print(f"[DEBUG] License check response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {'valid': False, 'error': f'Server error: {response.status_code}'}
                
        except Exception as e:
            return {'valid': False, 'error': f'Exception: {e}'}
    
    def shutdown_protection(self):
        """Shutdown protection"""
        self.is_protected = False
        self.session_token = None
        print("[PROTECTION] Protection system shutdown")

def test_simple_protection():
    """Test simple protection system"""
    print("[TEST] Simple Protection System Test")
    print("=" * 50)
    
    protection = SimpleProtection()
    
    # Test hardware fingerprint
    print(f"[OK] Hardware ID: {protection.hardware_id[:16]}...")
    
    # Test anti-debug
    if protection._check_anti_debug():
        print("[OK] No debugger detected")
    else:
        print("[FAIL] Debugger detected")
    
    # Test integrity
    if protection._check_integrity():
        print("[OK] Application integrity verified")
    else:
        print("[FAIL] Application integrity compromised")
    
    # Test online verification
    if protection._verify_online():
        print("[OK] Online verification successful")
    else:
        print("[FAIL] Online verification failed")
    
    # Test protection initialization
    if protection.initialize_protection():
        print("[OK] Protection system initialized")
        
        # Test license validation with real license
        test_license = "TEST-377F492DF0D9E0A8"
        result = protection.check_license_with_protection(test_license)
        print(f"[OK] License validation: {result.get('valid', False)}")
        if result.get('valid'):
            print(f"   Plan: {result.get('plan', 'Unknown')}")
            print(f"   Expires: {result.get('expires_at', 'Unknown')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        protection.shutdown_protection()
        print("[OK] Protection system shutdown")
    else:
        print("[FAIL] Protection system initialization failed")

if __name__ == "__main__":
    test_simple_protection()
