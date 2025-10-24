"""
License Client - Tích hợp vào OCR Tool
Hệ thống xác thực license key từ Render server
"""

import requests
import hashlib
import json
import os
import base64
from cryptography.fernet import Fernet
import platform
import uuid
import time

class LicenseClient:
    def __init__(self):
        self.server_url = "https://ocr-uufr.onrender.com"
        self.license_file = os.path.join(os.getenv('LOCALAPPDATA'), 'VietnameseOCRTool', 'license.dat')
        self.hardware_id = self._get_hardware_id()
        
    def _get_hardware_id(self):
        """Tạo hardware ID duy nhất cho máy tính"""
        try:
            # Lấy thông tin phần cứng
            mac = uuid.getnode()
            cpu = platform.processor()
            system = platform.system()
            machine = platform.machine()
            
            # Tạo ID duy nhất
            hw_string = f"{mac}-{cpu}-{system}-{machine}"
            return hashlib.sha256(hw_string.encode()).hexdigest()[:16]
        except:
            return "unknown"
    
    def _encrypt_license_data(self, data):
        """Mã hóa dữ liệu license"""
        try:
            # Tạo key từ hardware ID
            key = hashlib.sha256(self.hardware_id.encode()).digest()
            fernet = Fernet(base64.urlsafe_b64encode(key))
            
            # Mã hóa dữ liệu
            encrypted_data = fernet.encrypt(json.dumps(data).encode())
            return encrypted_data
        except Exception as e:
            print(f"Lỗi mã hóa: {e}")
            return None
    
    def _decrypt_license_data(self, encrypted_data):
        """Giải mã dữ liệu license"""
        try:
            # Tạo key từ hardware ID
            key = hashlib.sha256(self.hardware_id.encode()).digest()
            fernet = Fernet(base64.urlsafe_b64encode(key))
            
            # Giải mã dữ liệu
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Lỗi giải mã: {e}")
            return None
    
    def save_license(self, license_key, license_data):
        """Lưu license key và dữ liệu vào file bảo mật"""
        try:
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            
            data = {
                'license_key': license_key,
                'license_data': license_data,
                'hardware_id': self.hardware_id,
                'timestamp': time.time()
            }
            
            encrypted_data = self._encrypt_license_data(data)
            if encrypted_data:
                with open(self.license_file, 'wb') as f:
                    f.write(encrypted_data)
                return True
        except Exception as e:
            print(f"Lỗi lưu license: {e}")
        return False
    
    def load_license(self):
        """Tải license từ file"""
        try:
            if not os.path.exists(self.license_file):
                return None
                
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()
            
            data = self._decrypt_license_data(encrypted_data)
            if data and data.get('hardware_id') == self.hardware_id:
                return data
        except Exception as e:
            print(f"Lỗi tải license: {e}")
        return None
    
    def verify_license_online(self, license_key):
        """Xác thực license với server"""
        try:
            payload = {
                'license_key': license_key,
                'machine_id': self.hardware_id
            }
            
            response = requests.post(
                f"{self.server_url}/api/validate",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    return {
                        'valid': True,
                        'license_data': {
                            'plan': data.get('plan', 'unknown'),
                            'activated': data.get('activated', ''),
                            'expires': data.get('expires', '')
                        },
                        'message': data.get('message', 'License hop le')
                    }
                else:
                    return {
                        'valid': False,
                        'message': data.get('error', 'License khong hop le')
                    }
            else:
                return {
                    'valid': False,
                    'message': f"Loi server: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'valid': False,
                'message': f"Khong the ket noi server: {str(e)}"
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f"Loi xac thuc: {str(e)}"
            }
    
    def verify_license_offline(self):
        """Xác thực license offline từ file"""
        try:
            data = self.load_license()
            if not data:
                return {
                    'valid': False,
                    'message': 'Khong tim thay license'
                }
            
            # Kiểm tra thời gian hết hạn
            license_data = data.get('license_data', {})
            if 'expires_at' in license_data:
                expires_at = license_data['expires_at']
                if time.time() > expires_at:
                    return {
                        'valid': False,
                        'message': 'License da het han'
                    }
            
            return {
                'valid': True,
                'license_data': license_data,
                'message': 'License hop le (offline)'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f"Loi xac thuc offline: {str(e)}"
            }
    
    def activate_license(self, license_key):
        """Kích hoạt license mới"""
        try:
            # Xác thực với server
            result = self.verify_license_online(license_key)
            
            if result['valid']:
                # Lưu license vào file
                if self.save_license(license_key, result['license_data']):
                    return {
                        'success': True,
                        'message': 'Kich hoat license thanh cong!'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Loi luu license'
                    }
            else:
                return {
                    'success': False,
                    'message': result['message']
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Loi kich hoat: {str(e)}"
            }
    
    def is_license_valid(self):
        """Kiểm tra license có hợp lệ không"""
        # Thử offline trước
        offline_result = self.verify_license_offline()
        if offline_result['valid']:
            return True
        
        # Nếu offline không được, thử online
        data = self.load_license()
        if data:
            online_result = self.verify_license_online(data['license_key'])
            if online_result['valid']:
                # Cập nhật lại file
                self.save_license(data['license_key'], online_result['license_data'])
                return True
        
        return False
    
    def get_license_info(self):
        """Lấy thông tin license"""
        data = self.load_license()
        if data:
            return {
                'license_key': data['license_key'][:8] + "..." + data['license_key'][-4:],
                'hardware_id': data['hardware_id'],
                'license_data': data.get('license_data', {}),
                'timestamp': data.get('timestamp', 0)
            }
        return None
