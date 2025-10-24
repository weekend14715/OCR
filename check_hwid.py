"""
Script kiểm tra Hardware ID của máy
"""

import sys
import io

# Fix encoding cho Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from license.hardware_id import HardwareID

def check_hwid():
    print("\n" + "="*70)
    print("THONG TIN HARDWARE ID")
    print("="*70)
    
    hwid = HardwareID()
    
    print(f"\nFull Hardware ID:")
    print(f"  {hwid.get_hwid()}")
    
    print(f"\nShort Hardware ID (16 chars):")
    print(f"  {hwid.get_short_hwid()}")
    
    print("\n" + "="*70)
    print("\nLUU Y:")
    print("  - Hardware ID duoc tao tu: CPU + Motherboard + Disk + MAC + Computer Name")
    print("  - License key se duoc bind voi Hardware ID nay")
    print("  - Thay doi phan cung co the lam thay doi Hardware ID")
    print("="*70 + "\n")

if __name__ == "__main__":
    check_hwid()

