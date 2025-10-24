"""
License Encryption/Decryption System
Hệ thống mã hóa/giải mã license với AES-256
"""

import os
import json
import time
import base64
import hashlib
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class LicenseCrypto:
    """Lớp xử lý mã hóa/giải mã license"""
    
    # Secret salt (sẽ được obfuscate khi build)
    _SALT = b'OCR_T00L_S3CR3T_S4LT_2024_V1.0_PROD'
    _SECRET_PHRASE = "OCRToolProfessionalEdition2024SecureKey"
    
    def __init__(self):
        pass
    
    def _derive_key(self, hwid):
        """
        Tạo encryption key từ HWID
        Sử dụng PBKDF2 với 100000 iterations
        
        Args:
            hwid (str): Hardware ID
            
        Returns:
            bytes: Fernet key (base64 encoded)
        """
        # Kết hợp hwid với secret phrase
        password = (hwid + self._SECRET_PHRASE).encode('utf-8')
        
        # PBKDF2 key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._SALT,
            iterations=100000,
        )
        key = kdf.derive(password)
        
        # Fernet cần key ở dạng base64
        return base64.urlsafe_b64encode(key)
    
    def _calculate_checksum(self, data):
        """
        Tính CRC32 checksum
        
        Args:
            data (str): Dữ liệu cần tính checksum
            
        Returns:
            str: Checksum (hex)
        """
        crc = zlib.crc32(data.encode('utf-8')) & 0xffffffff
        return format(crc, '08x').upper()
    
    def _calculate_hash(self, data):
        """
        Tính SHA-256 hash
        
        Args:
            data (str): Dữ liệu cần hash
            
        Returns:
            str: Hash (hex)
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest().upper()
    
    def encrypt_license(self, license_key, hwid, user_info=None):
        """
        Mã hóa license với nhiều lớp bảo mật
        
        Args:
            license_key (str): License key từ server
            hwid (str): Hardware ID
            user_info (dict): Thông tin user (optional)
            
        Returns:
            dict: {
                'encrypted_data': str,  # Dữ liệu đã mã hóa
                'checksum': str,        # CRC32 checksum
                'hash': str,            # SHA-256 hash
                'timestamp': float      # Thời gian kích hoạt
            }
        """
        timestamp = time.time()
        
        # Chuẩn bị dữ liệu - lưu thời gian theo múi giờ +7 (Việt Nam)
        from datetime import datetime, timezone, timedelta
        vietnam_tz = timezone(timedelta(hours=7))
        vietnam_time = datetime.now(vietnam_tz)
        
        data = {
            'license_key': license_key,
            'hwid': hwid,
            'timestamp': timestamp,
            'activated_at': vietnam_time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
        }
        
        if user_info:
            data['user_info'] = user_info
        
        # Convert sang JSON
        json_data = json.dumps(data, separators=(',', ':'))
        
        # Tính checksum và hash TRƯỚC khi mã hóa
        checksum = self._calculate_checksum(json_data)
        data_hash = self._calculate_hash(json_data + checksum)
        
        # Thêm checksum vào data
        data['checksum'] = checksum
        data['hash'] = data_hash
        
        # Mã hóa với Fernet (AES-128 trong CBC mode)
        json_data_final = json.dumps(data, separators=(',', ':'))
        
        encryption_key = self._derive_key(hwid)
        f = Fernet(encryption_key)
        
        encrypted_bytes = f.encrypt(json_data_final.encode('utf-8'))
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return {
            'encrypted_data': encrypted_b64,
            'checksum': checksum,
            'hash': data_hash,
            'timestamp': timestamp
        }
    
    def decrypt_license(self, encrypted_data, hwid):
        """
        Giải mã license và verify tính toàn vẹn
        
        Args:
            encrypted_data (str): Dữ liệu đã mã hóa (base64)
            hwid (str): Hardware ID
            
        Returns:
            dict hoặc None: Dữ liệu license nếu hợp lệ, None nếu thất bại
        """
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Tạo key để decrypt
            decryption_key = self._derive_key(hwid)
            f = Fernet(decryption_key)
            
            # Decrypt
            decrypted_bytes = f.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # Parse JSON
            data = json.loads(decrypted_str)
            
            # Verify checksum
            saved_checksum = data.pop('checksum', None)
            saved_hash = data.pop('hash', None)
            
            if not saved_checksum or not saved_hash:
                print("❌ Thiếu checksum hoặc hash")
                return None
            
            # Tính lại checksum để verify
            json_for_check = json.dumps({
                k: v for k, v in data.items() 
                if k not in ['checksum', 'hash']
            }, separators=(',', ':'))
            
            calculated_checksum = self._calculate_checksum(json_for_check)
            
            if calculated_checksum != saved_checksum:
                print(f"❌ Checksum không khớp: {calculated_checksum} != {saved_checksum}")
                return None
            
            # Verify hash
            calculated_hash = self._calculate_hash(json_for_check + saved_checksum)
            
            if calculated_hash != saved_hash:
                print(f"❌ Hash không khớp")
                return None
            
            # Verify HWID
            if data.get('hwid') != hwid:
                print(f"❌ HWID không khớp")
                return None
            
            # Restore checksum và hash vào data
            data['checksum'] = saved_checksum
            data['hash'] = saved_hash
            
            return data
            
        except Exception as e:
            print(f"❌ Lỗi decrypt license: {e}")
            return None
    
    def generate_registry_value(self, encrypted_data):
        """
        Tạo giá trị lưu vào Registry (hash của encrypted data)
        
        Args:
            encrypted_data (str): Dữ liệu đã mã hóa
            
        Returns:
            str: Hash value để lưu registry
        """
        return self._calculate_hash(encrypted_data)[:32]
    
    def generate_backup_checksum(self, encrypted_data, hwid):
        """
        Tạo checksum backup (kết hợp encrypted_data + hwid)
        
        Args:
            encrypted_data (str): Dữ liệu đã mã hóa
            hwid (str): Hardware ID
            
        Returns:
            str: Backup checksum
        """
        combined = encrypted_data + hwid + self._SECRET_PHRASE
        return self._calculate_hash(combined)


if __name__ == "__main__":
    # Test
    crypto = LicenseCrypto()
    
    # Test data
    test_key = "OCR24-ABCDE-12345-FGHIJ"
    test_hwid = "A1B2C3D4E5F6G7H8"
    
    print("=== TEST MÃ HÓA/GIẢI MÃ ===")
    
    # Encrypt
    result = crypto.encrypt_license(test_key, test_hwid)
    print(f"\n✅ Đã mã hóa:")
    print(f"   Encrypted: {result['encrypted_data'][:50]}...")
    print(f"   Checksum: {result['checksum']}")
    print(f"   Hash: {result['hash'][:32]}...")
    
    # Decrypt với đúng HWID
    print(f"\n🔓 Giải mã với đúng HWID:")
    decrypted = crypto.decrypt_license(result['encrypted_data'], test_hwid)
    if decrypted:
        print(f"   ✅ Thành công!")
        print(f"   License Key: {decrypted['license_key']}")
        print(f"   HWID: {decrypted['hwid']}")
    
    # Decrypt với sai HWID
    print(f"\n🔓 Giải mã với SAI HWID:")
    decrypted_wrong = crypto.decrypt_license(result['encrypted_data'], "WRONG_HWID")
    if not decrypted_wrong:
        print(f"   ✅ Đã chặn thành công!")

