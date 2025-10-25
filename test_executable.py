#!/usr/bin/env python3
"""
Test script để kiểm tra executable
"""

import subprocess
import sys
from pathlib import Path

def test_executable():
    print("=== TEST EXECUTABLE ===\n")
    
    exe_path = Path("dist/ocr_tool.exe")
    if not exe_path.exists():
        print("ERROR: Khong tim thay executable!")
        return
    
    print(f"Executable: {exe_path}")
    print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Test chạy executable
    print(f"\nDang chay executable...")
    try:
        # Chạy với timeout 10 giây
        result = subprocess.run(
            [str(exe_path)], 
            capture_output=True, 
            text=True, 
            timeout=10,
            cwd=exe_path.parent
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500]}...")
        if result.stderr:
            print(f"Stderr: {result.stderr[:500]}...")
            
    except subprocess.TimeoutExpired:
        print("Timeout - executable dang chay (co the la GUI)")
    except Exception as e:
        print(f"Loi khi chay executable: {e}")

if __name__ == "__main__":
    test_executable()
