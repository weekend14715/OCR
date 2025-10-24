"""
Script test giao diện nhập license
"""

import sys
import io

# Fix encoding cho Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from license.license_dialog import LicenseDialog

def test_dialog():
    print("="*70)
    print("TEST GIAO DIEN NHAP LICENSE")
    print("="*70)
    print("\nDang hien dialog...\n")
    
    dialog = LicenseDialog()
    key = dialog.show()
    
    print("\n" + "="*70)
    if key:
        print(f"OK - User da nhap: {key}")
        print("="*70)
    else:
        print("CANCEL - User da huy")
        print("="*70)

if __name__ == "__main__":
    test_dialog()

