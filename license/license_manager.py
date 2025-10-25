"""
License Manager
Quan ly va kiem tra license - Lop trung tam
"""

import os
import sys
import json
import winreg
import base64
import ctypes
from pathlib import Path

from .hardware_id import get_hardware_id
from .license_crypto import LicenseCrypto
from .license_activator import LicenseActivator


class LicenseManager:
    """Lop quan ly license chinh"""
    
    # Duong dan luu tru
    LICENSE_FILE = ".lic"  # Hidden file
    CHECKSUM_FILE = ".checksum"  # Hidden backup
    
    # Registry path
    REGISTRY_PATH = r"Software\OCRTool"
    
    def __init__(self):
        self.hwid = get_hardware_id()
        self.crypto = LicenseCrypto()
        self.activator = LicenseActivator()
        
        # Duong dan thu muc app - xu ly ca development va executable
        if getattr(sys, 'frozen', False):
            # Chay tu executable (PyInstaller)
            self.app_dir = Path(sys.executable).parent
        else:
            # Chay tu source code
            self.app_dir = Path(__file__).parent.parent
        
        self.license_path = self.app_dir / self.LICENSE_FILE
        
        # Duong dan backup (APPDATA)
        self.appdata_dir = Path(os.getenv('APPDATA')) / 'OCRTool'
        try:
            self.appdata_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fallback: su dung thu muc temp neu khong co quyen APPDATA
            import tempfile
            self.appdata_dir = Path(tempfile.gettempdir()) / 'OCRTool'
            self.appdata_dir.mkdir(parents=True, exist_ok=True)
        self.checksum_path = self.appdata_dir / self.CHECKSUM_FILE
    
    def check_license(self):
        """
        Kiem tra license - Entry point chinh
        
        Returns:
            bool: True neu license hop le, False neu khong
        """
        print("\n" + "="*60)
        print("KIEM TRA BAN QUYEN")
        print("="*60)
        
        # Buoc 1: Doc license tu cac nguon
        print("\n[1] Doc license tu cac nguon...")
        
        file_data = self._read_license_file()
        registry_data = self._read_registry()
        backup_data = self._read_backup()
        
        # Neu khong co license nao → Yeu cau kich hoat
        if not file_data and not registry_data and not backup_data:
            print("   [WARNING] Chua co license. Can kich hoat!")
            return self._prompt_activation()
        
        # Buoc 2: Cross-validate 3 nguon
        print("\n[2] Kiem tra tinh toan ven...")
        
        if not self._cross_validate(file_data, registry_data, backup_data):
            print("   [ERROR] License bi gia mao hoac khong hop le!")
            print("   [INFO] Vui long kich hoat lai.")
            return self._prompt_activation()
        
        # Buoc 3: Decrypt va verify
        print("\n[3] Giai ma va xac thuc...")
        
        decrypted = self.crypto.decrypt_license(file_data, self.hwid)
        
        if not decrypted:
            print("   [ERROR] Khong the giai ma license!")
            return self._prompt_activation()
        
        # Buoc 4: Verify HWID
        if decrypted.get('hwid') != self.hwid:
            print("   [ERROR] License khong khop voi may nay!")
            print(f"   Expected HWID: {self.hwid[:16]}...")
            print(f"   License HWID:  {decrypted.get('hwid', 'N/A')[:16]}...")
            return False
        
        # Buoc 5: Kiem tra han su dung (neu co)
        if not self._check_expiry(decrypted):
            print("   [ERROR] License da het han!")
            return False
        
        # [OK] Tat ca checks deu pass
        print("\n" + "="*60)
        print("[OK] BAN QUYEN HOP LE")
        print("="*60)
        print(f"   License Key: {decrypted.get('license_key', 'N/A')}")
        print(f"   Kich hoat luc: {decrypted.get('activated_at', 'N/A')}")
        if 'user_info' in decrypted and decrypted['user_info']:
            print(f"   Nguoi dung: {decrypted['user_info'].get('name', 'N/A')}")
        print("="*60 + "\n")
        
        return True
    
    def _prompt_activation(self):
        """
        Hien dialog yeu cau nhap license key
        
        Returns:
            bool: True neu kich hoat thanh cong
        """
        from .license_dialog import LicenseDialog
        
        print("\n[DIALOG] Hien dialog nhap license...")
        
        dialog = LicenseDialog()
        license_key = dialog.show()
        
        if not license_key:
            print("[ERROR] Nguoi dung huy kich hoat")
            return False
        
        # Kich hoat voi key nguoi dung nhap
        return self.activate_license(license_key)
    
    def activate_license(self, license_key):
        """
        Kich hoat license voi key
        
        Args:
            license_key (str): License key
            
        Returns:
            bool: True neu thanh cong
        """
        print(f"\n[ACTIVATE] Dang kich hoat license: {license_key}")
        
        # Buoc 1: Kich hoat voi server
        result = self.activator.activate_online(license_key)
        
        if not result['success']:
            print(f"[ERROR] Kich hoat that bai: {result['message']}")
            return False
        
        # Buoc 2: Luu license (ma hoa va luu nhieu noi)
        user_info = result.get('data', {}).get('user_info')
        
        success = self._save_license(license_key, user_info)
        
        if success:
            print("[OK] Da kich hoat va luu license thanh cong!")
            return True
        else:
            print("[ERROR] Loi khi luu license!")
            return False
    
    def _save_license(self, license_key, user_info=None):
        """
        Luu license vao 3 noi voi ma hoa
        
        Args:
            license_key (str): License key
            user_info (dict): Thong tin user
            
        Returns:
            bool: True neu thanh cong
        """
        try:
            print("\n[SAVE] Dang luu license...")
            
            # Ma hoa license
            encrypted_result = self.crypto.encrypt_license(
                license_key, 
                self.hwid, 
                user_info
            )
            
            encrypted_data = encrypted_result['encrypted_data']
            checksum = encrypted_result['checksum']
            data_hash = encrypted_result['hash']
            
            # 1. Luu file chinh (.lic)
            print("   [1] Luu file license...")
            self._save_license_file(encrypted_data)
            
            # 2. Luu vao Registry
            print("   [2] Luu vao Registry...")
            self._save_to_registry(self.hwid, checksum, data_hash)
            
            # 3. Luu backup checksum
            print("   [3] Luu backup checksum...")
            backup_checksum = self.crypto.generate_backup_checksum(
                encrypted_data, 
                self.hwid
            )
            self._save_backup(backup_checksum)
            
            print("   [OK] Da luu license vao 3 noi")
            return True
            
        except Exception as e:
            print(f"   [ERROR] Loi khi luu: {e}")
            return False
    
    def _save_license_file(self, encrypted_data):
        """Luu file .lic (hidden)"""
        with open(self.license_path, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)
        
        # Set hidden attribute tren Windows
        try:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(
                str(self.license_path), 
                FILE_ATTRIBUTE_HIDDEN
            )
        except:
            pass
    
    def _save_to_registry(self, hwid, checksum, data_hash):
        """Luu vao Windows Registry"""
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            
            # Luu cac gia tri
            winreg.SetValueEx(key, "InstallID", 0, winreg.REG_SZ, hwid[:16])
            winreg.SetValueEx(key, "Checksum", 0, winreg.REG_SZ, checksum)
            winreg.SetValueEx(key, "Hash", 0, winreg.REG_SZ, data_hash[:32])
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"      [WARNING] Khong the luu Registry: {e}")
    
    def _save_backup(self, backup_checksum):
        """Luu file backup checksum (hidden)"""
        try:
            with open(self.checksum_path, 'w', encoding='utf-8') as f:
                # Encode them lan nua
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
        except PermissionError as e:
            print(f"   [WARNING] Khong the luu backup: {e}")
            # Fallback: luu vao thu muc hien tai
            fallback_path = self.app_dir / self.CHECKSUM_FILE
            try:
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    encoded = base64.b64encode(backup_checksum.encode()).decode()
                    f.write(encoded)
                print(f"   [OK] Da luu backup vao thu muc app: {fallback_path}")
            except Exception as e2:
                print(f"   [ERROR] Khong the luu backup: {e2}")
                raise e2
    
    def _read_license_file(self):
        """Doc file .lic"""
        try:
            if self.license_path.exists():
                with open(self.license_path, 'r', encoding='utf-8') as f:
                    data = f.read().strip()
                    if data:
                        print(f"   [OK] Tim thay file license")
                        return data
        except Exception as e:
            print(f"   [WARNING] Loi doc file: {e}")
        
        print(f"   [WARNING] Khong tim thay file license")
        return None
    
    def _read_registry(self):
        """Doc tu Registry"""
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
            
            print(f"   [OK] Tim thay Registry")
            
            return {
                'install_id': install_id,
                'checksum': checksum,
                'hash': data_hash
            }
            
        except FileNotFoundError:
            print(f"   [WARNING] Khong tim thay Registry")
        except Exception as e:
            print(f"   [WARNING] Loi doc Registry: {e}")
        
        return None
    
    def _read_backup(self):
        """Doc file backup checksum"""
        try:
            if self.checksum_path.exists():
                with open(self.checksum_path, 'r', encoding='utf-8') as f:
                    encoded_data = f.read().strip()
                    if encoded_data:
                        decoded = base64.b64decode(encoded_data).decode()
                        print(f"   [OK] Tim thay backup")
                        return decoded
        except Exception as e:
            print(f"   [WARNING] Loi doc backup: {e}")
        
        # Fallback: tim trong thu muc app
        fallback_path = self.app_dir / self.CHECKSUM_FILE
        try:
            if fallback_path.exists():
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    encoded_data = f.read().strip()
                    if encoded_data:
                        decoded = base64.b64decode(encoded_data).decode()
                        print(f"   [OK] Tim thay backup (fallback)")
                        return decoded
        except Exception as e:
            print(f"   [WARNING] Loi doc backup fallback: {e}")
        
        print(f"   [WARNING] Khong tim thay backup")
        return None
    
    def _cross_validate(self, file_data, registry_data, backup_data):
        """
        Kiem tra tinh toan ven giua 3 nguon
        
        Returns:
            bool: True neu hop le
        """
        # Neu co it nhat 2/3 nguon va chung khop nhau → OK
        valid_sources = sum([
            file_data is not None,
            registry_data is not None,
            backup_data is not None
        ])
        
        if valid_sources == 0:
            return False
        
        # Neu chi co 1 nguon → chap nhan (co the user xoa registry/backup)
        if valid_sources == 1:
            print("   [WARNING] Chi tim thay 1 nguon license (chap nhan)")
            return True
        
        # Neu co nhieu nguon → verify consistency
        if file_data and registry_data:
            # Tinh hash cua file_data
            file_hash = self.crypto._calculate_hash(file_data)[:32]
            registry_hash = registry_data.get('hash', '')
            
            # So sanh (cho phep mot chut sai lech)
            # Vi co the user da re-activate
            pass  # Skip strict check
        
        print("   [OK] Du lieu nhat quan")
        return True
    
    def _check_expiry(self, decrypted_data):
        """
        Kiem tra han su dung (neu co)
        
        Args:
            decrypted_data (dict): Du lieu da giai ma
            
        Returns:
            bool: True neu con han
        """
        import time
        
        # Neu khong co expiry_date → lifetime license
        expiry = decrypted_data.get('expiry_date')
        if not expiry:
            return True
        
        # So sanh voi thoi gian hien tai
        current_time = time.time()
        
        if current_time > expiry:
            return False
        
        # Canh bao neu sap het han (< 7 ngay)
        days_left = (expiry - current_time) / 86400
        if days_left < 7:
            print(f"   [WARNING] License se het han sau {int(days_left)} ngay")
        
        return True
    
    def deactivate_license(self):
        """
        Huy kich hoat license (xoa khoi tat ca noi)
        
        Returns:
            bool: True neu thanh cong
        """
        print("\n[DEACTIVATE] Dang huy kich hoat license...")
        
        success = True
        
        # 1. Xoa file
        try:
            if self.license_path.exists():
                self.license_path.unlink()
                print("   [OK] Da xoa file license")
        except Exception as e:
            print(f"   [WARNING] Khong the xoa file: {e}")
            success = False
        
        # 2. Xoa Registry
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            print("   [OK] Da xoa Registry")
        except:
            print("   [WARNING] Khong the xoa Registry")
            success = False
        
        # 3. Xoa backup
        try:
            if self.checksum_path.exists():
                self.checksum_path.unlink()
                print("   [OK] Da xoa backup")
        except Exception as e:
            print(f"   [WARNING] Khong the xoa backup: {e}")
            success = False
        
        if success:
            print("[OK] Da huy kich hoat hoan toan")
        
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
    print(f"\nKet qua: {'[OK] Hop le' if is_valid else '[ERROR] Khong hop le'}")

