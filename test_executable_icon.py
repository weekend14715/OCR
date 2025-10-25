#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test executable để kiểm tra icon system tray
"""

import subprocess
import time
import os
import sys

def test_executable_icon():
    """Test executable và kiểm tra icon"""
    print("=== TEST EXECUTABLE ICON ===")
    
    exe_path = os.path.join("dist", "ocr_tool.exe")
    
    if not os.path.exists(exe_path):
        print(f"[ERROR] Executable not found: {exe_path}")
        return False
    
    print(f"[INFO] Found executable: {exe_path}")
    print(f"[INFO] Size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
    
    print("\n[INFO] Starting executable...")
    print("[INFO] Check system tray for icon!")
    print("[INFO] Press Ctrl+C to stop test")
    
    try:
        # Chạy executable
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Đợi một chút để app khởi động
        time.sleep(3)
        
        # Kiểm tra xem process có đang chạy không
        if process.poll() is None:
            print("[OK] Executable is running")
            print("[INFO] Look for icon in system tray (bottom right corner)")
            print("[INFO] Icon should be blue if default, or custom if loaded")
            
            # Đợi thêm để user có thể thấy icon
            print("[INFO] Waiting 10 seconds...")
            time.sleep(10)
            
            # Terminate process
            process.terminate()
            process.wait()
            print("[INFO] Process terminated")
            
        else:
            stdout, stderr = process.communicate()
            print(f"[ERROR] Process exited immediately")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        if 'process' in locals():
            process.terminate()
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_executable_icon()
    if success:
        print("\n=== TEST COMPLETE ===")
        print("If you saw an icon in the system tray, the fix worked!")
    else:
        print("\n=== TEST FAILED ===")
        print("Icon may not be showing in system tray")
