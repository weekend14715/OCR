"""
Hardware Fingerprint Generator
Tạo mã định danh duy nhất cho máy tính
"""

import uuid
import platform
import hashlib
import subprocess
import re


class HardwareID:
    """Lớp tạo Hardware Fingerprint cho máy tính"""
    
    def __init__(self):
        self._cache = None
    
    def get_hwid(self):
        """
        Lấy Hardware ID duy nhất của máy
        Returns:
            str: Hardware fingerprint (32 ký tự hex)
        """
        if self._cache:
            return self._cache
        
        components = []
        
        # 1. CPU ID
        cpu_id = self._get_cpu_id()
        if cpu_id:
            components.append(cpu_id)
        
        # 2. Motherboard UUID
        mb_uuid = self._get_motherboard_uuid()
        if mb_uuid:
            components.append(mb_uuid)
        
        # 3. Disk Serial Number
        disk_serial = self._get_disk_serial()
        if disk_serial:
            components.append(disk_serial)
        
        # 4. MAC Address
        mac = self._get_mac_address()
        if mac:
            components.append(mac)
        
        # 5. Computer Name
        comp_name = platform.node()
        if comp_name:
            components.append(comp_name)
        
        # Kết hợp tất cả và hash
        combined = '|'.join(str(c) for c in components if c)
        
        if not combined:
            # Fallback: dùng UUID ngẫu nhiên
            combined = str(uuid.uuid4())
        
        # Tạo SHA-256 hash và lấy 32 ký tự đầu
        hwid = hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32].upper()
        
        self._cache = hwid
        return hwid
    
    def _get_cpu_id(self):
        """Lấy CPU ID"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    'wmic cpu get ProcessorId',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    cpu_id = lines[1].strip()
                    if cpu_id:
                        return cpu_id
            else:
                # Linux/Mac
                output = subprocess.check_output(
                    'cat /proc/cpuinfo | grep "model name" | head -1',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                return output.strip()
        except:
            pass
        return None
    
    def _get_motherboard_uuid(self):
        """Lấy Motherboard UUID"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    'wmic csproduct get UUID',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    mb_uuid = lines[1].strip()
                    if mb_uuid and mb_uuid.lower() != 'ffffffff-ffff-ffff-ffff-ffffffffffff':
                        return mb_uuid
            else:
                # Linux
                output = subprocess.check_output(
                    'sudo dmidecode -s system-uuid',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                return output.strip()
        except:
            pass
        return None
    
    def _get_disk_serial(self):
        """Lấy Serial Number của ổ đĩa hệ thống"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    'wmic diskdrive get SerialNumber',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    serial = lines[1].strip()
                    if serial:
                        return serial
            else:
                # Linux
                output = subprocess.check_output(
                    'lsblk -o SERIAL -d | head -2 | tail -1',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                return output.strip()
        except:
            pass
        return None
    
    def _get_mac_address(self):
        """Lấy MAC Address"""
        try:
            mac = uuid.getnode()
            mac_str = ':'.join(re.findall('..', '%012x' % mac))
            return mac_str
        except:
            pass
        return None
    
    def get_short_hwid(self):
        """
        Lấy phiên bản rút gọn của HWID (16 ký tự)
        Dùng để hiển thị cho user
        """
        full_hwid = self.get_hwid()
        return full_hwid[:16]


# Singleton instance
_hwid_instance = None

def get_hardware_id():
    """
    Hàm tiện ích để lấy Hardware ID
    Returns:
        str: Hardware fingerprint
    """
    global _hwid_instance
    if _hwid_instance is None:
        _hwid_instance = HardwareID()
    return _hwid_instance.get_hwid()


if __name__ == "__main__":
    # Test
    hwid = HardwareID()
    print(f"Full HWID: {hwid.get_hwid()}")
    print(f"Short HWID: {hwid.get_short_hwid()}")

