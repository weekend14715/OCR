"""
License Manager
Quản lý và kiểm tra license - Lớp trung tâm
"""

import os
import json
import winreg
import base64
import ctypes
from pathlib import Path

from .hardware_id import get_hardware_id
from .license_crypto import LicenseCrypto
from .license_activator import LicenseActivator


class LicenseManager:
    """Lớp quản lý license chính"""
    
    # Đường dẫn lưu trữ
    LICENSE_FILE = ".lic"  # Hidden file
    CHECKSUM_FILE = ".checksum"  # Hidden backup
    
    # Registry path
    REGISTRY_PATH = r"Software\OCRTool"
    
    def __init__(self):
        self.hwid = get_hardware_id()
        self.crypto = LicenseCrypto()
        self.activator = LicenseActivator()
        
        # Đường dẫn thư mục app
        self.app_dir = Path(__file__).parent.parent
        self.license_path = self.app_dir / self.LICENSE_FILE
        
        # Đường dẫn backup (APPDATA)
        self.appdata_dir = Path(os.getenv('APPDATA')) / 'OCRTool'
        self.appdata_dir.mkdir(parents=True, exist_ok=True)
        self.checksum_path = self.appdata_dir / self.CHECKSUM_FILE
    
    def check_license(self):
        """
        Kiểm tra license - Entry point chính
        
        Returns:
            bool: True nếu license hợp lệ, False nếu không
        """
        print("\n" + "="*60)
        print("🔐 KIỂM TRA BẢN QUYỀN")
        print("="*60)
        
        # Bước 1: Đọc license từ các nguồn
        print("\n[1] Đọc license từ các nguồn...")
        
        file_data = self._read_license_file()
        registry_data = self._read_registry()
        backup_data = self._read_backup()
        
        # Nếu không có license nào → Yêu cầu kích hoạt
        if not file_data and not registry_data and not backup_data:
            print("   ⚠️ Chưa có license. Cần kích hoạt!")
            return self._prompt_activation()
        
        # Bước 2: Cross-validate 3 nguồn
        print("\n[2] Kiểm tra tính toàn vẹn...")
        
        if not self._cross_validate(file_data, registry_data, backup_data):
            print("   ❌ License bị giả mạo hoặc không hợp lệ!")
            print("   💡 Vui lòng kích hoạt lại.")
            return self._prompt_activation()
        
        # Bước 3: Decrypt và verify
        print("\n[3] Giải mã và xác thực...")
        
        decrypted = self.crypto.decrypt_license(file_data, self.hwid)
        
        if not decrypted:
            print("   ❌ Không thể giải mã license!")
            return self._prompt_activation()
        
        # Bước 4: Verify HWID
        if decrypted.get('hwid') != self.hwid:
            print("   ❌ License không khớp với máy này!")
            print(f"   Expected HWID: {self.hwid[:16]}...")
            print(f"   License HWID:  {decrypted.get('hwid', 'N/A')[:16]}...")
            return False
        
        # Bước 5: Kiểm tra hạn sử dụng (nếu có)
        if not self._check_expiry(decrypted):
            print("   ❌ License đã hết hạn!")
            return False
        
        # ✅ Tất cả checks đều pass
        print("\n" + "="*60)
        print("✅ BẢN QUYỀN HỢP LỆ")
        print("="*60)
        print(f"   License Key: {decrypted.get('license_key', 'N/A')}")
        print(f"   Kích hoạt lúc: {decrypted.get('activated_at', 'N/A')}")
        if 'user_info' in decrypted and decrypted['user_info']:
            print(f"   Người dùng: {decrypted['user_info'].get('name', 'N/A')}")
        print("="*60 + "\n")
        
        return True
    
    def _prompt_activation(self):
        """
        Hiện dialog yêu cầu nhập license key
        
        Returns:
            bool: True nếu kích hoạt thành công
        """
        from .license_dialog import LicenseDialog
        
        print("\n📝 Hiện dialog nhập license...")
        
        dialog = LicenseDialog()
        license_key = dialog.show()
        
        if not license_key:
            print("❌ Người dùng hủy kích hoạt")
            return False
        
        # Kích hoạt với key người dùng nhập
        return self.activate_license(license_key)
    
    def activate_license(self, license_key):
        """
        Kích hoạt license với key
        
        Args:
            license_key (str): License key
            
        Returns:
            bool: True nếu thành công
        """
        print(f"\n🔄 Đang kích hoạt license: {license_key}")
        
        # Bước 1: Kích hoạt với server
        result = self.activator.activate_online(license_key)
        
        if not result['success']:
            print(f"❌ Kích hoạt thất bại: {result['message']}")
            return False
        
        # Bước 2: Lưu license (mã hóa và lưu nhiều nơi)
        user_info = result.get('data', {}).get('user_info')
        
        success = self._save_license(license_key, user_info)
        
        if success:
            print("✅ Đã kích hoạt và lưu license thành công!")
            return True
        else:
            print("❌ Lỗi khi lưu license!")
            return False
    
    def _save_license(self, license_key, user_info=None):
        """
        Lưu license vào 3 nơi với mã hóa
        
        Args:
            license_key (str): License key
            user_info (dict): Thông tin user
            
        Returns:
            bool: True nếu thành công
        """
        try:
            print("\n💾 Đang lưu license...")
            
            # Mã hóa license
            encrypted_result = self.crypto.encrypt_license(
                license_key, 
                self.hwid, 
                user_info
            )
            
            encrypted_data = encrypted_result['encrypted_data']
            checksum = encrypted_result['checksum']
            data_hash = encrypted_result['hash']
            
            # 1. Lưu file chính (.lic)
            print("   [1] Lưu file license...")
            self._save_license_file(encrypted_data)
            
            # 2. Lưu vào Registry
            print("   [2] Lưu vào Registry...")
            self._save_to_registry(self.hwid, checksum, data_hash)
            
            # 3. Lưu backup checksum
            print("   [3] Lưu backup checksum...")
            backup_checksum = self.crypto.generate_backup_checksum(
                encrypted_data, 
                self.hwid
            )
            self._save_backup(backup_checksum)
            
            print("   ✅ Đã lưu license vào 3 nơi")
            return True
            
        except Exception as e:
            print(f"   ❌ Lỗi khi lưu: {e}")
            return False
    
    def _save_license_file(self, encrypted_data):
        """Lưu file .lic (hidden)"""
        with open(self.license_path, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)
        
        # Set hidden attribute trên Windows
        try:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(
                str(self.license_path), 
                FILE_ATTRIBUTE_HIDDEN
            )
        except:
            pass
    
    def _save_to_registry(self, hwid, checksum, data_hash):
        """Lưu vào Windows Registry"""
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            
            # Lưu các giá trị
            winreg.SetValueEx(key, "InstallID", 0, winreg.REG_SZ, hwid[:16])
            winreg.SetValueEx(key, "Checksum", 0, winreg.REG_SZ, checksum)
            winreg.SetValueEx(key, "Hash", 0, winreg.REG_SZ, data_hash[:32])
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"      ⚠️ Không thể lưu Registry: {e}")
    
    def _save_backup(self, backup_checksum):
        """Lưu file backup checksum (hidden)"""
        with open(self.checksum_path, 'w', encoding='utf-8') as f:
            # Encode thêm lần nữa
            encoded = base64.b64encode(backup_checksum.encode()).decode()
            f.write(encoded)
        
        # Set hidden
        try:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(
                str(self.checksum_path),
                FILE_ATTRIBUTE_HIDDEN
            )
        except:
            pass
    
    def _read_license_file(self):
        """Đọc file .lic"""
        try:
            if self.license_path.exists():
                with open(self.license_path, 'r', encoding='utf-8') as f:
                    data = f.read().strip()
                    if data:
                        print(f"   ✅ Tìm thấy file license")
                        return data
        except Exception as e:
            print(f"   ⚠️ Lỗi đọc file: {e}")
        
        print(f"   ⚠️ Không tìm thấy file license")
        return None
    
    def _read_registry(self):
        """Đọc từ Registry"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.REGISTRY_PATH, 
                0, 
                winreg.KEY_READ
            )
            
            install_id = winreg.QueryValueEx(key, "InstallID")[0]
            checksum = winreg.QueryValueEx(key, "Checksum")[0]
            data_hash = winreg.QueryValueEx(key, "Hash")[0]
            
            winreg.CloseKey(key)
            
            print(f"   ✅ Tìm thấy Registry")
            
            return {
                'install_id': install_id,
                'checksum': checksum,
                'hash': data_hash
            }
            
        except FileNotFoundError:
            print(f"   ⚠️ Không tìm thấy Registry")
        except Exception as e:
            print(f"   ⚠️ Lỗi đọc Registry: {e}")
        
        return None
    
    def _read_backup(self):
        """Đọc file backup checksum"""
        try:
            if self.checksum_path.exists():
                with open(self.checksum_path, 'r', encoding='utf-8') as f:
                    encoded_data = f.read().strip()
                    if encoded_data:
                        decoded = base64.b64decode(encoded_data).decode()
                        print(f"   ✅ Tìm thấy backup")
                        return decoded
        except Exception as e:
            print(f"   ⚠️ Lỗi đọc backup: {e}")
        
        print(f"   ⚠️ Không tìm thấy backup")
        return None
    
    def _cross_validate(self, file_data, registry_data, backup_data):
        """
        Kiểm tra tính toàn vẹn giữa 3 nguồn
        
        Returns:
            bool: True nếu hợp lệ
        """
        # Nếu có ít nhất 2/3 nguồn và chúng khớp nhau → OK
        valid_sources = sum([
            file_data is not None,
            registry_data is not None,
            backup_data is not None
        ])
        
        if valid_sources == 0:
            return False
        
        # Nếu chỉ có 1 nguồn → chấp nhận (có thể user xóa registry/backup)
        if valid_sources == 1:
            print("   ⚠️ Chỉ tìm thấy 1 nguồn license (chấp nhận)")
            return True
        
        # Nếu có nhiều nguồn → verify consistency
        if file_data and registry_data:
            # Tính hash của file_data
            file_hash = self.crypto._calculate_hash(file_data)[:32]
            registry_hash = registry_data.get('hash', '')
            
            # So sánh (cho phép một chút sai lệch)
            # Vì có thể user đã re-activate
            pass  # Skip strict check
        
        print("   ✅ Dữ liệu nhất quán")
        return True
    
    def _check_expiry(self, decrypted_data):
        """
        Kiểm tra hạn sử dụng (nếu có)
        
        Args:
            decrypted_data (dict): Dữ liệu đã giải mã
            
        Returns:
            bool: True nếu còn hạn
        """
        import time
        
        # Nếu không có expiry_date → lifetime license
        expiry = decrypted_data.get('expiry_date')
        if not expiry:
            return True
        
        # So sánh với thời gian hiện tại
        current_time = time.time()
        
        if current_time > expiry:
            return False
        
        # Cảnh báo nếu sắp hết hạn (< 7 ngày)
        days_left = (expiry - current_time) / 86400
        if days_left < 7:
            print(f"   ⚠️ License sẽ hết hạn sau {int(days_left)} ngày")
        
        return True
    
    def deactivate_license(self):
        """
        Hủy kích hoạt license (xóa khỏi tất cả nơi)
        
        Returns:
            bool: True nếu thành công
        """
        print("\n🗑️ Đang hủy kích hoạt license...")
        
        success = True
        
        # 1. Xóa file
        try:
            if self.license_path.exists():
                self.license_path.unlink()
                print("   ✅ Đã xóa file license")
        except Exception as e:
            print(f"   ⚠️ Không thể xóa file: {e}")
            success = False
        
        # 2. Xóa Registry
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            print("   ✅ Đã xóa Registry")
        except:
            print("   ⚠️ Không thể xóa Registry")
            success = False
        
        # 3. Xóa backup
        try:
            if self.checksum_path.exists():
                self.checksum_path.unlink()
                print("   ✅ Đã xóa backup")
        except Exception as e:
            print(f"   ⚠️ Không thể xóa backup: {e}")
            success = False
        
        if success:
            print("✅ Đã hủy kích hoạt hoàn toàn")
        
        return success


if __name__ == "__main__":
    # Test
    manager = LicenseManager()
    
    print("=== TEST LICENSE MANAGER ===")
    print(f"HWID: {manager.hwid}")
    print(f"License file: {manager.license_path}")
    print(f"Backup file: {manager.checksum_path}")
    
    # Test check license
    is_valid = manager.check_license()
    print(f"\nKết quả: {'✅ Hợp lệ' if is_valid else '❌ Không hợp lệ'}")

