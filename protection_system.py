"""
Advanced Protection System for Vietnamese OCR Tool
Hệ thống bảo vệ nâng cao chống sao chép và reverse engineering
"""

import hashlib
import hmac
import time
import os
import sys
import platform
import uuid
import psutil
import requests
import json
import base64
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import threading
import ctypes
from ctypes import wintypes
import subprocess

class AdvancedProtection:
    """Hệ thống bảo vệ nâng cao"""
    
    def __init__(self):
        self.server_url = "http://127.0.0.1:5000"
        self.app_name = "VietnameseOCRTool"
        self.protection_key = self._generate_protection_key()
        self.session_token = None
        self.last_verification = 0
        self.verification_interval = 300  # 5 phút
        self.is_protected = False
        
    def _generate_protection_key(self):
        """Tạo key bảo vệ dựa trên hardware fingerprint"""
        try:
            # Lấy thông tin phần cứng
            cpu_info = platform.processor()
            memory_info = str(psutil.virtual_memory().total)
            disk_info = str(psutil.disk_usage('/').total) if os.name != 'nt' else str(psutil.disk_usage('C:\\').total)
            
            # Tạo fingerprint
            fingerprint = f"{cpu_info}-{memory_info}-{disk_info}-{platform.machine()}"
            key = hashlib.sha256(fingerprint.encode()).digest()
            
            # Tạo Fernet key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'vietnamese_ocr_protection',
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(key))
            
        except Exception as e:
            # Fallback key nếu không lấy được hardware info
            return base64.urlsafe_b64encode(b'fallback_protection_key_123456789012345678901234567890')
    
    def _encrypt_data(self, data):
        """Mã hóa dữ liệu"""
        try:
            f = Fernet(self.protection_key)
            encrypted_data = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception:
            return base64.urlsafe_b64encode(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data):
        """Giải mã dữ liệu"""
        try:
            f = Fernet(self.protection_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return base64.urlsafe_b64decode(encrypted_data.encode()).decode()
    
    def _get_hardware_fingerprint(self):
        """Lấy hardware fingerprint duy nhất"""
        try:
            # CPU info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_freq_str = str(cpu_freq.max) if cpu_freq else "unknown"
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_total = str(memory.total)
            
            # Disk info
            disk = psutil.disk_usage('/') if os.name != 'nt' else psutil.disk_usage('C:\\')
            disk_total = str(disk.total)
            
            # Network interfaces
            network_interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:  # MAC address
                        network_interfaces.append(addr.address)
            
            # Boot time
            boot_time = str(psutil.boot_time())
            
            # Tạo fingerprint
            fingerprint_data = f"{cpu_count}-{cpu_freq_str}-{memory_total}-{disk_total}-{'-'.join(network_interfaces[:3])}-{boot_time}"
            
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            # Fallback fingerprint
            return hashlib.sha256(f"{platform.node()}-{uuid.getnode()}-{platform.processor()}".encode()).hexdigest()
    
    def _check_anti_debug(self):
        """Kiểm tra anti-debugging"""
        try:
            # Kiểm tra debugger
            if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
                return False
            
            # Kiểm tra process debugger trên Windows
            if os.name == 'nt':
                kernel32 = ctypes.windll.kernel32
                is_debugger_present = kernel32.IsDebuggerPresent()
                if is_debugger_present:
                    return False
            
            # Kiểm tra process list cho debugger tools
            debugger_processes = [
                'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 'ida.exe', 'ida64.exe',
                'ghidra.exe', 'radare2.exe', 'gdb.exe', 'lldb.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in debugger_processes:
                        return False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return True
            
        except Exception:
            return True  # Nếu không kiểm tra được, cho phép chạy
    
    def _check_integrity(self):
        """Kiểm tra tính toàn vẹn của ứng dụng"""
        try:
            # Lấy đường dẫn file hiện tại
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = __file__
            
            # Kiểm tra file size (có thể bị thay đổi)
            file_size = os.path.getsize(app_path)
            
            # Kiểm tra thời gian tạo file
            file_time = os.path.getctime(app_path)
            current_time = time.time()
            
            # Nếu file được tạo quá gần thời điểm hiện tại (có thể bị copy)
            if current_time - file_time < 60:  # 1 phút
                return False
            
            # Kiểm tra xem có file license.dat trong thư mục không
            license_file = os.path.join(os.path.dirname(app_path), 'license.dat')
            if os.path.exists(license_file):
                # Kiểm tra thời gian tạo license file
                license_time = os.path.getctime(license_file)
                if current_time - license_time < 60:
                    return False
            
            return True
            
        except Exception:
            return True
    
    def _verify_online(self):
        """Xác thực online với server"""
        try:
            hardware_id = self._get_hardware_fingerprint()
            current_time = int(time.time())
            
            # Tạo signature
            message = f"{hardware_id}-{current_time}"
            signature = hmac.new(
                self.protection_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Gửi request đến server
            response = requests.post(
                f"{self.server_url}/api/protection/verify",
                json={
                    'hardware_id': hardware_id,
                    'timestamp': current_time,
                    'signature': signature,
                    'app_name': self.app_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    self.session_token = data.get('session_token')
                    self.last_verification = current_time
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _start_protection_thread(self):
        """Khởi động thread bảo vệ liên tục"""
        def protection_loop():
            while self.is_protected:
                try:
                    # Kiểm tra anti-debug
                    if not self._check_anti_debug():
                        self._terminate_app("Debugger detected")
                        break
                    
                    # Kiểm tra integrity
                    if not self._check_integrity():
                        self._terminate_app("Application integrity compromised")
                        break
                    
                    # Xác thực online định kỳ
                    current_time = time.time()
                    if current_time - self.last_verification > self.verification_interval:
                        if not self._verify_online():
                            self._terminate_app("Online verification failed")
                            break
                    
                    time.sleep(30)  # Kiểm tra mỗi 30 giây
                    
                except Exception as e:
                    print(f"Protection error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=protection_loop, daemon=True)
        thread.start()
    
    def _terminate_app(self, reason):
        """Kết thúc ứng dụng khi phát hiện vi phạm"""
        print(f"[VIOLATION] Protection violation: {reason}")
        print("Ứng dụng sẽ được đóng để bảo vệ bản quyền.")
        
        # Xóa session token
        self.session_token = None
        self.is_protected = False
        
        # Thoát ứng dụng
        os._exit(1)
    
    def initialize_protection(self):
        """Khởi tạo hệ thống bảo vệ"""
        try:
            # Kiểm tra anti-debug
            if not self._check_anti_debug():
                self._terminate_app("Debugger detected")
                return False
            
            # Kiểm tra integrity
            if not self._check_integrity():
                self._terminate_app("Application integrity compromised")
                return False
            
            # Xác thực online
            if not self._verify_online():
                self._terminate_app("Online verification failed")
                return False
            
            # Khởi động protection thread
            self.is_protected = True
            self._start_protection_thread()
            
            print("[OK] Advanced protection system activated")
            return True
            
        except Exception as e:
            print(f"[FAIL] Protection initialization failed: {e}")
            return False
    
    def check_license_with_protection(self, license_key):
        """Kiểm tra license với bảo vệ nâng cao"""
        try:
            # Kiểm tra anti-debug trước
            if not self._check_anti_debug():
                return {'valid': False, 'error': 'Debugger detected'}
            
            # Kiểm tra integrity
            if not self._check_integrity():
                return {'valid': False, 'error': 'Application integrity compromised'}
            
            # Xác thực online
            if not self._verify_online():
                return {'valid': False, 'error': 'Online verification failed'}
            
            # Kiểm tra license với server
            hardware_id = self._get_hardware_fingerprint()
            
            response = requests.post(
                f"{self.server_url}/api/validate",
                json={
                    'license_key': license_key.strip().upper(),
                    'machine_id': hardware_id,
                    'protection_token': self.session_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    # Khởi tạo protection system
                    self.initialize_protection()
                
                return data
            else:
                return {
                    'valid': False,
                    'error': f'Server error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Protection error: {str(e)}'
            }
    
    def shutdown_protection(self):
        """Tắt hệ thống bảo vệ"""
        self.is_protected = False
        self.session_token = None
        print("[PROTECTION] Protection system shutdown")

# Global protection instance
protection_system = AdvancedProtection()
