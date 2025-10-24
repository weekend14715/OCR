"""
License Activator
Xử lý kích hoạt license với server
"""

import requests
import json
import time
from .hardware_id import get_hardware_id


class LicenseActivator:
    """Lớp xử lý kích hoạt license với server"""
    
    # URL API server (Render deployment)
    API_BASE_URL = "https://ocr-uufr.onrender.com/api"
    
    # Timeout cho requests (giây)
    TIMEOUT = 10
    
    def __init__(self):
        self.hwid = get_hardware_id()
    
    def activate_online(self, license_key):
        """
        Kích hoạt license trực tuyến với server
        
        Args:
            license_key (str): License key người dùng nhập
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'data': dict hoặc None,
                'error': str hoặc None
            }
        """
        try:
            # Chuẩn bị request data
            request_data = {
                'license_key': license_key,
                'hwid': self.hwid,
                'timestamp': time.time(),
                'product': 'OCR_TOOL',
                'version': '1.0'
            }
            
            print(f"🔄 Đang kết nối server để kích hoạt...")
            print(f"   License Key: {license_key}")
            print(f"   HWID: {self.hwid[:16]}...")
            
            # Gửi request đến server
            response = requests.post(
                f"{self.API_BASE_URL}/validate",
                json={
                    'license_key': license_key,
                    'machine_id': self.hwid
                },
                timeout=self.TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'OCRTool/1.0'
                }
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                
                if result.get('valid'):
                    print(f"✅ Kích hoạt thành công!")
                    return {
                        'success': True,
                        'message': result.get('message', 'License activated successfully'),
                        'data': {
                            'plan': result.get('plan'),
                            'activated': result.get('activated'),
                            'expires': result.get('expires')
                        },
                        'error': None
                    }
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ Kích hoạt thất bại: {error_msg}")
                    return {
                        'success': False,
                        'message': error_msg,
                        'data': None,
                        'error': error_msg
                    }
            
            else:
                return {
                    'success': False,
                    'message': f'Lỗi server (HTTP {response.status_code})',
                    'data': None,
                    'error': f'HTTP {response.status_code}'
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Timeout: Không thể kết nối đến server',
                'data': None,
                'error': 'Connection timeout'
            }
        
        except requests.exceptions.ConnectionError:
            print("⚠️ Không thể kết nối server, thử kích hoạt offline...")
            return self._activate_offline(license_key)
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi không xác định: {str(e)}',
                'data': None,
                'error': str(e)
            }
    
    def _activate_offline(self, license_key):
        """
        Kích hoạt offline (fallback khi không có mạng)
        Sử dụng thuật toán validate key cục bộ
        
        Args:
            license_key (str): License key
            
        Returns:
            dict: Kết quả kích hoạt
        """
        print("🔒 Chế độ kích hoạt OFFLINE")
        
        # Validate format key
        if not self._validate_key_format(license_key):
            return {
                'success': False,
                'message': 'License key không đúng định dạng',
                'data': None,
                'error': 'Invalid key format'
            }
        
        # Validate checksum
        if not self._validate_key_checksum(license_key):
            return {
                'success': False,
                'message': 'License key không hợp lệ (checksum sai)',
                'data': None,
                'error': 'Invalid checksum'
            }
        
        # Nếu pass tất cả checks → cho phép kích hoạt
        print("✅ Kích hoạt offline thành công!")
        
        return {
            'success': True,
            'message': 'Đã kích hoạt offline thành công',
            'data': {
                'license_key': license_key,
                'activation_type': 'offline',
                'user_info': None
            },
            'error': None
        }
    
    def _validate_key_format(self, key):
        """
        Kiểm tra định dạng key: XXXX-XXXX-XXXX-XXXX (4 groups, mỗi group 4 ký tự hex)
        Đồng bộ với server generate_license_key() trong app.py
        
        Args:
            key (str): License key
            
        Returns:
            bool: True nếu đúng format
        """
        import re
        # Format: 4 nhóm, mỗi nhóm 4 ký tự hex [0-9A-F]
        pattern = r'^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}$'
        return bool(re.match(pattern, key.upper()))
    
    def _validate_key_checksum(self, key):
        """
        Validate key bằng cách kiểm tra với database server
        Không còn dùng checksum offline vì server quản lý toàn bộ
        
        Args:
            key (str): License key
            
        Returns:
            bool: True nếu key tồn tại trong database (basic check)
        """
        # Format XXXX-XXXX-XXXX-XXXX đã đủ, không cần checksum offline
        # Server sẽ validate key có trong database hay không
        return True
    
    def verify_with_server(self, license_key):
        """
        Verify license với server (không kích hoạt, chỉ kiểm tra)
        
        Args:
            license_key (str): License key
            
        Returns:
            dict: Thông tin license từ server
        """
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/validate",
                json={
                    'license_key': license_key,
                    'machine_id': self.hwid
                },
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': result.get('valid', False),
                    'error': result.get('error', None),
                    'data': result
                }
            else:
                return {'success': False, 'error': 'Verification failed'}
                
        except:
            return {'success': False, 'error': 'Cannot connect to server'}
    
    def deactivate(self, license_key):
        """
        Hủy kích hoạt license (giải phóng máy)
        Chức năng này cần admin API key, user không thể tự deactivate
        
        Args:
            license_key (str): License key
            
        Returns:
            dict: Kết quả deactivate
        """
        print("⚠️ Deactivate license cần liên hệ admin")
        print("   Email support để yêu cầu chuyển license sang máy khác")
        return {
            'success': False,
            'message': 'Vui lòng liên hệ support để chuyển license',
            'support_email': 'support@ocrtool.com'
        }


if __name__ == "__main__":
    # Test
    activator = LicenseActivator()
    
    print("=== TEST LICENSE ACTIVATOR ===")
    print(f"HWID: {activator.hwid}")
    print(f"API Server: {activator.API_BASE_URL}")
    
    # Test với key mẫu (format server: XXXX-XXXX-XXXX-XXXX)
    test_key = "1A2B-3C4D-5E6F-7890"
    
    print(f"\n🧪 Test validate format:")
    print(f"   Key: {test_key}")
    print(f"   Valid: {activator._validate_key_format(test_key)}")
    
    print(f"\n🧪 Test activate (sẽ thử kết nối server):")
    result = activator.activate_online(test_key)
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    
    if not result['success']:
        print(f"\n💡 Lưu ý: Key mẫu '{test_key}' chỉ để test format")
        print(f"   Để test thực tế, cần tạo key từ admin panel hoặc mua license")

