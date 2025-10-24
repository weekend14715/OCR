"""
Build Protected Vietnamese OCR Tool
Script để build ứng dụng với hệ thống bảo vệ nâng cao
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def install_dependencies():
    """Cài đặt các dependencies cần thiết"""
    print("[PACKAGE] Installing dependencies...")
    
    dependencies = [
        'pyinstaller',
        'cryptography',
        'psutil',
        'requests',
        'numpy',
        'Pillow',
        'pytesseract',
        'keyboard',
        'pyperclip',
        'pystray'
    ]
    
    success_count = 0
    total_deps = len(dependencies)
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
            print(f"[OK] Installed {dep}")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"[ERROR] Failed to install {dep}")
    
    print(f"[SUMMARY] Installed {success_count}/{total_deps} dependencies")
    return success_count == total_deps

def obfuscate_code():
    """Obfuscate code trước khi build"""
    print("[OBFUSCATE] Obfuscating code...")
    
    try:
        from code_obfuscator import CodeObfuscator
        
        obfuscator = CodeObfuscator()
        
        # Obfuscate main files
        files_to_obfuscate = [
            'ocr_tool_licensed.py',
            'license_client.py',
            'protection_system.py'
        ]
        
        for file in files_to_obfuscate:
            if os.path.exists(file):
                obfuscated_file = f"obfuscated_{file}"
                if obfuscator.obfuscate_file(file, obfuscated_file):
                    print(f"[OK] Obfuscated {file}")
                else:
                    print(f"[ERROR] Failed to obfuscate {file}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Obfuscation failed: {e}")
        return False

def create_protected_spec():
    """Tạo PyInstaller spec file cho ứng dụng được bảo vệ"""
    print("[SPEC] Creating protected spec file...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['obfuscated_ocr_tool_licensed.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Tesseract-OCR', 'Tesseract-OCR'),
        ('icon.png', '.'),
        ('obfuscated_license_client.py', '.'),
        ('obfuscated_protection_system.py', '.'),
    ],
    hiddenimports=[
        'protection_system',
        'license_client',
        'pytesseract',
        'PIL',
        'keyboard',
        'pyperclip',
        'pystray',
        'numpy',
        'cryptography',
        'psutil',
        'requests',
        'hmac',
        'base64',
        'zlib',
        'marshal',
        'types',
        'threading',
        'ctypes',
        'subprocess',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VietnameseOCRTool_Protected',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png'
)
'''
    
    with open('VietnameseOCRTool_Protected.spec', 'w') as f:
        f.write(spec_content)
    
    print("[OK] Created protected spec file")
    return True

def build_executable():
    """Build executable với PyInstaller"""
    print("[BUILD] Building protected executable...")
    
    try:
        # Build với spec file
        subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'VietnameseOCRTool_Protected.spec'
        ], check=True)
        
        print("[OK] Executable built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False

def create_installer():
    """Tạo installer cho ứng dụng"""
    print("[INSTALLER] Creating installer...")
    
    try:
        # Tạo thư mục dist nếu chưa có
        dist_dir = Path('dist')
        if not dist_dir.exists():
            dist_dir.mkdir()
        
        # Tạo zip file
        zip_path = 'VietnameseOCRTool_Protected.zip'
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Thêm executable
            exe_path = dist_dir / 'VietnameseOCRTool_Protected.exe'
            if exe_path.exists():
                zipf.write(exe_path, 'VietnameseOCRTool_Protected.exe')
            
            # Thêm thư mục Tesseract-OCR
            tesseract_dir = dist_dir / 'Tesseract-OCR'
            if tesseract_dir.exists():
                for root, dirs, files in os.walk(tesseract_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arc_path = file_path.relative_to(dist_dir)
                        zipf.write(file_path, arc_path)
            
            # Thêm README
            readme_content = """
Vietnamese OCR Tool - Protected Version
=======================================

HƯỚNG DẪN CÀI ĐẶT:
1. Giải nén file này vào thư mục bất kỳ
2. Chạy VietnameseOCRTool_Protected.exe
3. Nhập license key khi được yêu cầu
4. Ứng dụng sẽ tự động kích hoạt hệ thống bảo vệ

TÍNH NĂNG BẢO VỆ:
- Mã hóa code và obfuscation
- Ràng buộc với phần cứng máy tính
- Xác thực online định kỳ
- Chống debug và reverse engineering
- Chống sao chép thư mục ứng dụng

LƯU Ý:
- Ứng dụng cần kết nối internet để xác thực
- Không thể chạy trên máy khác mà không có license
- Không thể sao chép thư mục để sử dụng

HỖ TRỢ:
- Email: support@vietnamese-ocr.com
- Website: https://vietnamese-ocr.com
"""
            
            zipf.writestr('README.txt', readme_content)
        
        print(f"[OK] Installer created: {zip_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Installer creation failed: {e}")
        return False

def cleanup():
    """Dọn dẹp các file tạm"""
    print("[CLEANUP] Cleaning up...")
    
    temp_files = [
        'obfuscated_ocr_tool_licensed.py',
        'obfuscated_license_client.py',
        'obfuscated_protection_system.py',
        'VietnameseOCRTool_Protected.spec'
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"[REMOVED] {file}")
    
    # Xóa thư mục build
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("[REMOVED] build directory")

def main():
    """Hàm main để build ứng dụng được bảo vệ"""
    print("[BUILD] Building Protected Vietnamese OCR Tool")
    print("=" * 50)
    
    # Bước 1: Cài đặt dependencies
    if not install_dependencies():
        print("[ERROR] Failed to install dependencies")
        return False
    
    # Bước 2: Obfuscate code
    if not obfuscate_code():
        print("[ERROR] Failed to obfuscate code")
        return False
    
    # Bước 3: Tạo spec file
    if not create_protected_spec():
        print("[ERROR] Failed to create spec file")
        return False
    
    # Bước 4: Build executable
    if not build_executable():
        print("[ERROR] Failed to build executable")
        return False
    
    # Bước 5: Tạo installer
    if not create_installer():
        print("[ERROR] Failed to create installer")
        return False
    
    # Bước 6: Cleanup
    cleanup()
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Protected application built successfully!")
    print("[PACKAGE] Installer: VietnameseOCRTool_Protected.zip")
    print("[PROTECTION] Protection features enabled:")
    print("   - Code obfuscation")
    print("   - Hardware binding")
    print("   - Online verification")
    print("   - Anti-debugging")
    print("   - Anti-copy protection")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
