"""
License Client Module
Module xác thực license cho Vietnamese OCR Tool
"""

import hashlib
import platform
import socket
import requests
import json
import os
import uuid

class LicenseManager:
    """Quản lý license cho ứng dụng"""
    
    def __init__(self, license_server_url="http://127.0.0.1:5000"):
        self.server_url = license_server_url
        self.license_file = os.path.join(
            os.getenv('LOCALAPPDATA'), 
            'VietnameseOCRTool', 
            'license.dat'
        )
        
    def get_machine_id(self):
        """
        Lấy machine ID duy nhất cho máy này
        Sử dụng tổ hợp: hostname + MAC address + processor
        """
        try:
            # Lấy hostname
            hostname = platform.node()
            
            # Lấy MAC address
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 8*6, 8)][::-1])
            
            # Lấy processor info
            processor = platform.processor()
            
            # Tạo unique ID
            machine_string = f"{hostname}-{mac}-{processor}"
            machine_id = hashlib.sha256(machine_string.encode()).hexdigest()[:32]
            
            return machine_id
            
        except Exception as e:
            print(f"⚠️ Lỗi khi lấy machine ID: {e}")
            # Fallback: sử dụng UUID ngẫu nhiên (không ideal nhưng tốt hơn crash)
            return str(uuid.uuid4()).replace('-', '')[:32]
    
    def save_license_key(self, license_key):
        """Lưu license key vào file local"""
        try:
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            with open(self.license_file, 'w') as f:
                f.write(license_key)
            return True
        except Exception as e:
            print(f"❌ Không thể lưu license: {e}")
            return False
    
    def load_license_key(self):
        """Đọc license key từ file local"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            print(f"❌ Không thể đọc license: {e}")
            return None
    
    def delete_license_key(self):
        """Xóa license key khỏi file local"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            return True
        except Exception as e:
            print(f"❌ Không thể xóa license: {e}")
            return False
    
    def validate_license(self, license_key=None):
        """
        Xác thực license với server
        
        Returns:
            dict: {
                'valid': bool,
                'message': str,
                'plan': str (optional),
                'expires': str (optional)
            }
        """
        # Nếu không truyền license_key, đọc từ file
        if license_key is None:
            license_key = self.load_license_key()
        
        if not license_key:
            return {
                'valid': False,
                'error': 'No license key found'
            }
        
        try:
            machine_id = self.get_machine_id()
            
            # Gửi request đến server
            response = requests.post(
                f"{self.server_url}/api/validate",
                json={
                    'license_key': license_key.strip().upper(),
                    'machine_id': machine_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Nếu valid, lưu license key
                if data.get('valid'):
                    self.save_license_key(license_key)
                
                return data
            else:
                return {
                    'valid': False,
                    'error': f'Server error: {response.status_code}'
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'valid': False,
                'error': 'Cannot connect to license server. Please check your internet connection.'
            }
        except requests.exceptions.Timeout:
            return {
                'valid': False,
                'error': 'License server timeout. Please try again later.'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def activate_license(self, license_key):
        """
        Kích hoạt license mới
        
        Args:
            license_key: License key từ người dùng
            
        Returns:
            dict: Kết quả validation
        """
        result = self.validate_license(license_key)
        
        if result.get('valid'):
            self.save_license_key(license_key)
            print(f"✅ License đã được kích hoạt thành công!")
            print(f"   Gói: {result.get('plan', 'N/A')}")
            if result.get('expires'):
                print(f"   Hết hạn: {result['expires']}")
            else:
                print(f"   Hết hạn: Vĩnh viễn")
        
        return result
    
    def check_license_status(self):
        """
        Kiểm tra trạng thái license hiện tại
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        license_key = self.load_license_key()
        
        if not license_key:
            return False, "Chưa kích hoạt license. Vui lòng nhập license key."
        
        result = self.validate_license(license_key)
        
        if result.get('valid'):
            plan = result.get('plan', 'Unknown')
            expires = result.get('expires', 'Never')
            return True, f"License hợp lệ | Gói: {plan} | Hết hạn: {expires if expires != 'Never' else 'Vĩnh viễn'}"
        else:
            error = result.get('error', 'Unknown error')
            return False, f"License không hợp lệ: {error}"
    
    def deactivate_license(self):
        """Xóa license khỏi máy này"""
        if self.delete_license_key():
            print("✅ Đã xóa license khỏi máy này")
            return True
        else:
            print("❌ Không thể xóa license")
            return False


# ==============================================================================
# DEMO / TESTING
# ==============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Vietnamese OCR Tool - License Client Demo")
    print("="*60)
    
    # Khởi tạo license manager
    lm = LicenseManager()
    
    # Hiển thị machine ID
    print(f"\n🖥️  Machine ID của bạn: {lm.get_machine_id()}")
    
    # Kiểm tra license hiện tại
    print("\n📋 Kiểm tra license hiện tại...")
    is_valid, message = lm.check_license_status()
    print(f"   {message}")
    
    if not is_valid:
        # Yêu cầu nhập license key
        print("\n" + "="*60)
        license_key = input("🔑 Nhập license key của bạn: ").strip()
        
        if license_key:
            print("\n⏳ Đang kích hoạt license...")
            result = lm.activate_license(license_key)
            
            if not result.get('valid'):
                print(f"\n❌ Kích hoạt thất bại: {result.get('error')}")
            else:
                print("\n✅ Kích hoạt thành công!")
        else:
            print("\n⚠️  Không nhập license key")
    else:
        print("\n✅ License hợp lệ - Ứng dụng có thể chạy!")
    
    print("\n" + "="*60)

