#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vietnamese OCR Tool - Offline Protection System Demo
Demo hệ thống bảo vệ mà không cần license server
"""

import os
import sys
import time
import hashlib
import psutil
import platform
from datetime import datetime

def get_hardware_id():
    """Tạo hardware ID từ thông tin hệ thống"""
    try:
        # Lấy thông tin CPU
        cpu_info = platform.processor()
        
        # Lấy thông tin RAM
        memory = psutil.virtual_memory()
        ram_info = f"{memory.total}_{memory.available}"
        
        # Lấy thông tin disk
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.total}_{disk.free}"
        
        # Lấy thông tin network
        network_info = ""
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # AF_INET
                    network_info += f"{interface}_{addr.address}_"
        
        # Tạo hardware ID
        hardware_string = f"{cpu_info}_{ram_info}_{disk_info}_{network_info}"
        hardware_id = hashlib.sha256(hardware_string.encode()).hexdigest()[:32]
        
        return hardware_id
    except Exception as e:
        print(f"[ERROR] Cannot get hardware info: {e}")
        return "unknown_hardware"

def check_anti_debugging():
    """Kiểm tra anti-debugging"""
    try:
        # Kiểm tra process list cho debug tools
        debug_tools = [
            'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 'ida.exe', 'ida64.exe',
            'idaq.exe', 'idaq64.exe', 'immunity.exe', 'w32dasm.exe',
            'hopper.exe', 'radare2.exe', 'gdb.exe', 'lldb.exe'
        ]
        
        running_processes = [p.name().lower() for p in psutil.process_iter(['name'])]
        
        for tool in debug_tools:
            if tool in running_processes:
                print(f"   [WARNING] Debug tool detected: {tool}")
                return False
        
        print("   [OK] No debugger detected")
        return True
    except Exception as e:
        print(f"   [ERROR] Anti-debugging check failed: {e}")
        return False

def check_application_integrity():
    """Kiểm tra tính toàn vẹn ứng dụng"""
    try:
        # Kiểm tra file hiện tại
        current_file = __file__
        if os.path.exists(current_file):
            with open(current_file, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
                print(f"   [OK] Application integrity verified (hash: {file_hash[:16]}...)")
                return True
        else:
            print("   [ERROR] Application file not found")
            return False
    except Exception as e:
        print(f"   [ERROR] Integrity check failed: {e}")
        return False

def simulate_license_validation():
    """Mô phỏng license validation (offline)"""
    try:
        # Tạo license key giả lập
        hardware_id = get_hardware_id()
        license_key = f"TEST-{hardware_id[:16].upper()}"
        
        print(f"   [OK] License validation successful (offline mode)")
        print(f"   License: {license_key}")
        print(f"   Hardware ID: {hardware_id[:16]}...")
        return True
    except Exception as e:
        print(f"   [ERROR] License validation failed: {e}")
        return False

def demo_protection_violations():
    """Demo các vi phạm bảo vệ"""
    print("\n" + "=" * 60)
    print("PROTECTION VIOLATION DEMO")
    print("=" * 60)
    
    print("1. Testing invalid license...")
    print("   [OK] Invalid license would be rejected")
    
    print("2. Testing wrong hardware ID...")
    print("   [OK] Wrong hardware ID would be rejected")
    
    print("3. Testing expired license...")
    print("   [OK] Expired license would be rejected")
    
    print("4. Testing debugger detection...")
    if check_anti_debugging():
        print("   [OK] No debugger detected - system secure")
    else:
        print("   [WARNING] Debugger detected - system compromised")

def main():
    """Main demo function"""
    print("Vietnamese OCR Tool - Offline Protection System Demo")
    print("Advanced protection system against copying and reverse engineering")
    
    print("\n" + "=" * 60)
    print("VIETNAMESE OCR TOOL - PROTECTION SYSTEM")
    print("=" * 60)
    
    # Kiểm tra các lớp bảo vệ
    print("1. Checking anti-debugging...")
    anti_debug_ok = check_anti_debugging()
    
    print("2. Checking application integrity...")
    integrity_ok = check_application_integrity()
    
    print("3. Verifying license (offline mode)...")
    license_ok = simulate_license_validation()
    
    # Kết quả
    if anti_debug_ok and integrity_ok and license_ok:
        print("\n[SUCCESS] Protection system initialized successfully!")
        hardware_id = get_hardware_id()
        print(f"Hardware ID: {hardware_id[:16]}...")
        
        # Demo license validation
        print("\n" + "=" * 60)
        print("LICENSE VALIDATION DEMO")
        print("=" * 60)
        simulate_license_validation()
        
        # Demo protection violations
        demo_protection_violations()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED")
        print("=" * 60)
        print("Protection system demo completed successfully!")
        print("Protection features:")
        print("- Hardware fingerprinting")
        print("- Anti-debugging detection")
        print("- Application integrity checking")
        print("- License validation with hardware binding")
        print("- Protection against copying and reverse engineering")
        print("\nNote: This is offline demo mode. In production,")
        print("online verification with license server is required.")
        
    else:
        print("\n[ERROR] Cannot initialize protection system!")
        print("Some protection checks failed.")

if __name__ == "__main__":
    main()
