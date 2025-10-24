"""
Clean License - Advanced Version
Xóa toàn bộ license data từ 3 vị trí + hiển thị chi tiết
"""

import os
import sys
import winreg
import shutil
from pathlib import Path


class LicenseCleaner:
    """Clean all license data"""
    
    def __init__(self):
        self.results = {
            'lic_file': False,
            'registry': False,
            'backup': False
        }
    
    def clean_all(self):
        """Xóa toàn bộ license data"""
        print("=" * 70)
        print("  🧹 CLEAN LICENSE TOOL - XÓA TOÀN BỘ DỮ LIỆU LICENSE")
        print("=" * 70)
        print()
        
        # Confirm
        confirm = input("⚠️  Bạn có chắc muốn XÓA toàn bộ license? (Y/N): ")
        if confirm.upper() != 'Y':
            print("\n❌ Đã hủy. Không có gì bị xóa.\n")
            return False
        
        print("\n" + "=" * 70)
        print("  BẮT ĐẦU XÓA DỮ LIỆU...")
        print("=" * 70)
        print()
        
        # Clean từng vị trí
        self.clean_lic_file()
        self.clean_registry()
        self.clean_backup()
        
        # Report
        self.show_report()
        
        return all(self.results.values())
    
    def clean_lic_file(self):
        """Xóa file .lic"""
        print("[1/3] Xóa file .lic...")
        
        # Các vị trí có thể có file .lic
        possible_paths = [
            Path('.lic'),
            Path(__file__).parent / '.lic',
            Path.cwd() / '.lic'
        ]
        
        found = False
        deleted = False
        
        for path in possible_paths:
            if path.exists():
                found = True
                try:
                    path.unlink()
                    print(f"   ✅ Đã xóa: {path}")
                    deleted = True
                except Exception as e:
                    print(f"   ❌ Không thể xóa {path}: {e}")
        
        if not found:
            print("   ℹ️  File .lic không tồn tại")
            deleted = True  # Consider as success
        
        self.results['lic_file'] = deleted
        print()
    
    def clean_registry(self):
        """Xóa registry keys"""
        print("[2/3] Xóa Registry (HKCU\\Software\\OCRTool)...")
        
        try:
            # Mở key để kiểm tra
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\OCRTool",
                0,
                winreg.KEY_READ
            )
            
            # Liệt kê các values
            values_deleted = []
            try:
                i = 0
                while True:
                    name, value, type_ = winreg.EnumValue(key, i)
                    values_deleted.append(name)
                    i += 1
            except OSError:
                pass
            
            winreg.CloseKey(key)
            
            # Xóa toàn bộ key
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\OCRTool"
            )
            
            print("   ✅ Đã xóa registry key:")
            for val in values_deleted:
                print(f"      - {val}")
            
            self.results['registry'] = True
        
        except FileNotFoundError:
            print("   ℹ️  Registry key không tồn tại")
            self.results['registry'] = True  # Consider as success
        
        except Exception as e:
            print(f"   ❌ Lỗi xóa registry: {e}")
            self.results['registry'] = False
        
        print()
    
    def clean_backup(self):
        """Xóa backup checksum"""
        print("[3/3] Xóa backup checksum (%APPDATA%\\OCRTool)...")
        
        appdata = os.environ.get('APPDATA')
        if not appdata:
            print("   ❌ Không tìm thấy %APPDATA%")
            self.results['backup'] = False
            print()
            return
        
        ocr_tool_dir = Path(appdata) / 'OCRTool'
        checksum_file = ocr_tool_dir / '.checksum'
        
        found = False
        deleted = False
        
        # Xóa file .checksum
        if checksum_file.exists():
            found = True
            try:
                checksum_file.unlink()
                print(f"   ✅ Đã xóa: {checksum_file}")
                deleted = True
            except Exception as e:
                print(f"   ❌ Không thể xóa {checksum_file}: {e}")
        
        # Xóa thư mục nếu rỗng
        if ocr_tool_dir.exists():
            try:
                if not any(ocr_tool_dir.iterdir()):
                    ocr_tool_dir.rmdir()
                    print(f"   ✅ Đã xóa thư mục: {ocr_tool_dir}")
            except Exception as e:
                print(f"   ℹ️  Không thể xóa thư mục: {e}")
        
        if not found:
            print("   ℹ️  File .checksum không tồn tại")
            deleted = True
        
        self.results['backup'] = deleted
        print()
    
    def show_report(self):
        """Hiển thị báo cáo kết quả"""
        print("=" * 70)
        print("  KIỂM TRA KẾT QUẢ")
        print("=" * 70)
        print()
        
        status_icon = lambda x: "✅" if x else "❌"
        
        print(f"[{status_icon(self.results['lic_file'])}] File .lic")
        print(f"[{status_icon(self.results['registry'])}] Registry keys")
        print(f"[{status_icon(self.results['backup'])}] Backup checksum")
        
        print()
        print("=" * 70)
        
        if all(self.results.values()):
            print("  ✅ HOÀN TẤT! Đã xóa sạch toàn bộ license data")
            print()
            print("  Bây giờ bạn có thể:")
            print("  1. Test với license key mới")
            print("  2. Activate lại với key cũ")
            print("  3. Chạy app sẽ hiện dialog nhập license")
        else:
            print("  ⚠️  MỘT SỐ FILE CHƯA XÓA ĐƯỢC")
            print()
            print("  Nguyên nhân có thể:")
            print("  - File đang được mở bởi ứng dụng")
            print("  - Thiếu quyền truy cập")
            print()
            print("  Giải pháp:")
            print("  1. Đóng tất cả ứng dụng OCR Tool")
            print("  2. Chạy lại script này")
        
        print("=" * 70)
        print()
    
    def verify_clean(self):
        """Verify tất cả đã bị xóa"""
        print("\n" + "=" * 70)
        print("  🔍 VERIFY - KIỂM TRA LẠI")
        print("=" * 70)
        print()
        
        all_clean = True
        
        # Check .lic
        lic_exists = Path('.lic').exists()
        if lic_exists:
            print("❌ File .lic vẫn tồn tại")
            all_clean = False
        else:
            print("✅ File .lic đã bị xóa")
        
        # Check registry
        try:
            winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\OCRTool",
                0,
                winreg.KEY_READ
            )
            print("❌ Registry key vẫn tồn tại")
            all_clean = False
        except FileNotFoundError:
            print("✅ Registry key đã bị xóa")
        
        # Check backup
        appdata = os.environ.get('APPDATA')
        checksum_path = Path(appdata) / 'OCRTool' / '.checksum'
        if checksum_path.exists():
            print("❌ Backup checksum vẫn tồn tại")
            all_clean = False
        else:
            print("✅ Backup checksum đã bị xóa")
        
        print()
        if all_clean:
            print("🎉 TẤT CẢ ĐỀU SẠCH! License đã bị xóa hoàn toàn.")
        else:
            print("⚠️  Một số file vẫn còn. Hãy xóa thủ công hoặc thử lại.")
        
        print("=" * 70)
        print()


def main():
    """Main function"""
    cleaner = LicenseCleaner()
    
    try:
        success = cleaner.clean_all()
        
        # Verify
        if success:
            cleaner.verify_clean()
        
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bởi user.\n")
        return 1
    
    except Exception as e:
        print(f"\n❌ Lỗi không xác định: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

