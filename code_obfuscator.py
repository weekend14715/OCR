"""
Code Obfuscator for Vietnamese OCR Tool
Mã hóa và obfuscation code để bảo vệ khỏi reverse engineering
"""

import base64
import zlib
import marshal
import types
import sys
import os
import random
import string

class CodeObfuscator:
    """Lớp obfuscation code Python"""
    
    def __init__(self):
        self.obfuscated_functions = {}
        self.string_table = {}
        self.function_table = {}
        
    def _generate_random_name(self, length=8):
        """Tạo tên ngẫu nhiên"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _obfuscate_strings(self, code):
        """Obfuscate strings trong code"""
        import re
        
        # Tìm tất cả strings
        string_pattern = r'(["\'])(?:(?!\1)[^\\]|\\.)*\1'
        strings = re.findall(string_pattern, code)
        
        for i, string_match in enumerate(strings):
            # Tạo key ngẫu nhiên
            key = self._generate_random_name()
            self.string_table[key] = string_match
            
            # Thay thế string bằng key
            code = code.replace(string_match, f'__str_{key}__')
        
        return code
    
    def _obfuscate_function_names(self, code):
        """Obfuscate tên function"""
        import re
        
        # Tìm function definitions
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        functions = re.findall(func_pattern, code)
        
        for func_name in functions:
            if not func_name.startswith('__'):  # Không obfuscate magic methods
                new_name = self._generate_random_name()
                self.function_table[func_name] = new_name
                
                # Thay thế tên function
                code = re.sub(rf'\b{func_name}\b', new_name, code)
        
        return code
    
    def _obfuscate_variables(self, code):
        """Obfuscate tên biến"""
        import re
        
        # Tìm variable assignments
        var_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        variables = re.findall(var_pattern, code)
        
        for var_name in variables:
            if not var_name.startswith('__') and var_name not in ['self', 'cls']:
                new_name = self._generate_random_name()
                code = re.sub(rf'\b{var_name}\b', new_name, code)
        
        return code
    
    def _add_dummy_code(self, code):
        """Thêm code giả để làm rối"""
        dummy_functions = [
            f"def {self._generate_random_name()}(): pass",
            f"def {self._generate_random_name()}(x): return x + 1",
            f"def {self._generate_random_name()}(): return {random.randint(1, 100)}",
        ]
        
        # Thêm dummy code vào đầu file
        dummy_code = '\n'.join(dummy_functions) + '\n\n'
        return dummy_code + code
    
    def _compress_and_encode(self, code):
        """Nén và encode code"""
        # Compress code
        compressed = zlib.compress(code.encode())
        
        # Base64 encode
        encoded = base64.b64encode(compressed)
        
        return encoded.decode()
    
    def _create_loader(self, obfuscated_code):
        """Tạo loader để giải mã và chạy code"""
        loader_template = '''
import base64
import zlib
import marshal
import types
import sys

def __load_obfuscated_code():
    """Load và giải mã obfuscated code"""
    obfuscated_data = """{obfuscated_code}"""
    
    try:
        # Decode và decompress
        decoded = base64.b64decode(obfuscated_data)
        decompressed = zlib.decompress(decoded)
        
        # Compile và execute
        code_obj = compile(decompressed, '<obfuscated>', 'exec')
        exec(code_obj, globals())
        
    except Exception as e:
        print(f"Error loading obfuscated code: {{e}}")
        sys.exit(1)

# Chạy obfuscated code
if __name__ == "__main__":
    __load_obfuscated_code()
'''
        
        return loader_template.format(obfuscated_code=obfuscated_code)
    
    def obfuscate_file(self, input_file, output_file):
        """Obfuscate một file Python"""
        try:
            # Đọc file gốc
            with open(input_file, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Obfuscate
            obfuscated_code = self._obfuscate_strings(original_code)
            obfuscated_code = self._obfuscate_function_names(obfuscated_code)
            obfuscated_code = self._obfuscate_variables(obfuscated_code)
            obfuscated_code = self._add_dummy_code(obfuscated_code)
            
            # Compress và encode
            encoded_code = self._compress_and_encode(obfuscated_code)
            
            # Tạo loader
            loader_code = self._create_loader(encoded_code)
            
            # Ghi file obfuscated
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(loader_code)
            
            print(f"✅ Obfuscated {input_file} -> {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Obfuscation failed: {e}")
            return False
    
    def obfuscate_directory(self, input_dir, output_dir):
        """Obfuscate toàn bộ thư mục"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        input_path = os.path.join(root, file)
                        relative_path = os.path.relpath(input_path, input_dir)
                        output_path = os.path.join(output_dir, relative_path)
                        
                        # Tạo thư mục con nếu cần
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        # Obfuscate file
                        self.obfuscate_file(input_path, output_path)
            
            print(f"✅ Obfuscated directory {input_dir} -> {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Directory obfuscation failed: {e}")
            return False

def create_protected_executable():
    """Tạo executable được bảo vệ"""
    try:
        import PyInstaller
        
        # Tạo spec file cho PyInstaller
        spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ocr_tool_licensed.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Tesseract-OCR', 'Tesseract-OCR'),
        ('icon.png', '.'),
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
    name='VietnameseOCRTool',
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
        
        with open('VietnameseOCRTool.spec', 'w') as f:
            f.write(spec_content)
        
        print("✅ Created PyInstaller spec file")
        return True
        
    except ImportError:
        print("❌ PyInstaller not installed. Install with: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Failed to create executable spec: {e}")
        return False

if __name__ == "__main__":
    # Test obfuscation
    obfuscator = CodeObfuscator()
    
    # Obfuscate main file
    if os.path.exists('ocr_tool_licensed.py'):
        obfuscator.obfuscate_file('ocr_tool_licensed.py', 'ocr_tool_obfuscated.py')
    
    # Create protected executable
    create_protected_executable()
