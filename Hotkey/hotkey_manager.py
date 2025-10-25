import keyboard
import tkinter as tk
from tkinter import font as tkFont
import configparser
import os
import sys
from threading import Thread

class HotkeyManager:
    """Quản lý phím tắt cho Vietnamese OCR Tool."""
    
    def __init__(self, trigger_callback=None):
        self.trigger_callback = trigger_callback
        self.current_hotkey = None
        self.hotkey_handle = None
        self.config_file = None
        self._setup_config()
    
    def _setup_config(self):
        """Thiết lập file cấu hình."""
        app_name = "VietnameseOCRTool"
        config_dir = os.path.join(os.getenv('LOCALAPPDATA'), app_name)
        os.makedirs(config_dir, exist_ok=True)
        self.config_file = os.path.join(config_dir, 'config.ini')
    
    def load_hotkey(self):
        """Tải phím tắt từ file config.ini."""
        if not os.path.exists(self.config_file):
            return None
        
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file, encoding='utf-8')
            hotkey = config.get('Settings', 'hotkey', fallback=None)
            if hotkey:
                self.current_hotkey = hotkey
                print(f"Da tai phim tat: {hotkey}")
            return hotkey
        except Exception as e:
            print(f"Loi khi tai phim tat: {e}")
            return None
    
    def save_hotkey(self, hotkey_str):
        """Lưu phím tắt vào file config.ini."""
        try:
            config = configparser.ConfigParser()
            config['Settings'] = {'hotkey': hotkey_str}
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            print(f"Da luu phim tat: {hotkey_str}")
            return True
        except Exception as e:
            print(f"Loi khi luu phim tat: {e}")
            return False
    
    def register_hotkey(self, hotkey_str):
        """Đăng ký phím tắt mới."""
        # Hủy phím tắt cũ nếu có
        self.unregister_hotkey()
        
        try:
            self.current_hotkey = hotkey_str
            if self.trigger_callback:
                self.hotkey_handle = keyboard.add_hotkey(hotkey_str, self.trigger_callback)
                print(f"Da dang ky phim tat: {hotkey_str}")
                return True
            else:
                print("Khong co callback function")
                return False
        except Exception as e:
            print(f"Loi khi dang ky phim tat: {e}")
            return False
    
    def unregister_hotkey(self):
        """Hủy đăng ký phím tắt hiện tại."""
        if self.hotkey_handle:
            try:
                keyboard.remove_hotkey(self.hotkey_handle)
                self.hotkey_handle = None
                print("Da huy dang ky phim tat cu")
            except Exception as e:
                print(f"Loi khi huy dang ky phim tat: {e}")
    
    def get_current_hotkey(self):
        """Lấy phím tắt hiện tại."""
        return self.current_hotkey
    
    def prompt_for_hotkey(self):
        """Hiển thị giao diện chọn phím tắt."""
        print("\n" + "="*55)
        print("✨ VUI LÒNG CHỌN PHÍM TẮT ✨")
        print("="*55)

        selector = HotkeySelectorWindow()
        new_hotkey = selector.get_hotkey()

        if new_hotkey:
            print(f"\nBan da chon: {new_hotkey}")
            self.save_hotkey(new_hotkey)
            return new_hotkey
        else:
            # Nếu không chọn được, dùng mặc định
            default_hotkey = "ctrl+q"
            print(f"\nSu dung phim tat mac dinh: {default_hotkey}")
            self.save_hotkey(default_hotkey)
            return default_hotkey
    
    def change_hotkey_from_tray(self):
        """Thay đổi phím tắt từ system tray."""
        print("\n🔄 Bắt đầu thay đổi phím tắt...")
        # Chạy trong thread riêng để tránh block UI
        def run_hotkey_selection():
            new_hotkey = self.prompt_for_hotkey()
            if new_hotkey:
                self.register_hotkey(new_hotkey)
                return new_hotkey
            return None
        
        # Chạy trong thread riêng
        Thread(target=run_hotkey_selection, daemon=True).start()


class HotkeySelectorWindow:
    """Tạo cửa sổ chọn phím tắt với các tùy chọn có sẵn."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chọn phím tắt OCR")
        self.root.attributes('-topmost', True)
        self.root.geometry("500x450")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        
        # Tối ưu hóa: ẩn cửa sổ trước khi setup UI để tránh flicker
        self.root.withdraw()
        
        # Tính toán vị trí trung tâm
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"500x450+{x}+{y}")
        
        self.selected_hotkey = None
        self.setup_ui()
        
        # Hiển thị cửa sổ sau khi setup xong
        self.root.deiconify()
        self.root.focus_force()
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng."""
        # Tối ưu hóa: tạo font một lần và tái sử dụng
        title_font = tkFont.Font(family="Arial", size=16, weight="bold")
        button_font = tkFont.Font(family="Arial", size=12, weight="bold")
        desc_font = tkFont.Font(family="Arial", size=10)
        
        title_label = tk.Label(
            self.root,
            text="🎯 CHỌN PHÍM TẮT CHO OCR TOOL",
            font=title_font,
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        title_label.pack(pady=20)
        
        desc_label = tk.Label(
            self.root,
            text="Chọn một trong các tùy chọn bên dưới:",
            font=desc_font,
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        desc_label.pack(pady=(0, 20))
        
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(expand=True, fill="both", padx=30, pady=10)
        
        hotkey_options = [
            {"key": "ctrl+q", "name": "Ctrl + Q", "desc": "Tổ hợp phím phổ biến, dễ nhớ"},
            {"key": "alt+space", "name": "Alt + Space", "desc": "Nhanh gọn, không xung đột"},
            {"key": "ctrl+shift+c", "name": "Ctrl + Shift + C", "desc": "Phím tắt chuyên nghiệp"}
        ]
        
        for option in hotkey_options:
            btn_frame = tk.Frame(button_frame, bg="#34495e", relief="raised", bd=2)
            btn_frame.pack(fill="x", pady=5)
            
            btn = tk.Button(
                btn_frame,
                text=f"{option['name']}",
                font=button_font,
                bg="#3498db",
                fg="white",
                relief="flat",
                command=lambda k=option['key']: self.select_hotkey(k)
            )
            btn.pack(fill="x", padx=5, pady=5)
            
            desc_btn = tk.Label(
                btn_frame,
                text=option['desc'],
                font=desc_font,
                bg="#34495e",
                fg="#bdc3c7"
            )
            desc_btn.pack(pady=(0, 5))
        
        # Nút nhấn phím tùy ý
        press_frame = tk.Frame(button_frame, bg="#9b59b6", relief="raised", bd=2)
        press_frame.pack(fill="x", pady=(10, 5))
        
        press_btn = tk.Button(
            press_frame,
            text="⌨️ NHẤN PHÍM TÙY Ý",
            font=button_font,
            bg="#9b59b6",
            fg="white",
            relief="flat",
            command=self.select_press_hotkey
        )
        press_btn.pack(fill="x", padx=5, pady=5)
        
        press_desc = tk.Label(
            press_frame,
            text="Nhấn nút rồi gõ tổ hợp phím bạn muốn",
            font=desc_font,
            bg="#9b59b6",
            fg="white"
        )
        press_desc.pack(pady=(0, 5))
    
    def select_hotkey(self, hotkey):
        """Chọn phím tắt có sẵn."""
        self.selected_hotkey = hotkey
        self.root.destroy()
    
    def select_press_hotkey(self):
        """Chọn phím tắt bằng cách nhấn phím tùy ý."""
        self.root.destroy()
        press_window = PressHotkeyWindow()
        self.selected_hotkey = press_window.get_hotkey()
    
    def get_hotkey(self):
        """Hiển thị cửa sổ và trả về phím tắt được chọn."""
        self.root.mainloop()
        return self.selected_hotkey


class PressHotkeyWindow:
    """Cửa sổ nhấn phím tùy ý."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nhấn phím tùy ý")
        self.root.attributes('-topmost', True)
        self.root.geometry("500x300")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        
        # Tối ưu hóa: ẩn cửa sổ trước khi setup UI
        self.root.withdraw()
        
        # Tính toán vị trí trung tâm
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"500x300+{x}+{y}")
        
        self.hotkey = None
        self.setup_ui()
        
        # Hiển thị cửa sổ sau khi setup xong
        self.root.deiconify()
        self.root.focus_force()
    
    def setup_ui(self):
        """Thiết lập giao diện."""
        # Tối ưu hóa: tạo font một lần và tái sử dụng
        title_font = tkFont.Font(family="Arial", size=16, weight="bold")
        button_font = tkFont.Font(family="Arial", size=12)
        desc_font = tkFont.Font(family="Arial", size=11)
        
        title_label = tk.Label(
            self.root,
            text="⌨️ NHẤN PHÍM TÙY Ý",
            font=title_font,
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        title_label.pack(pady=20)
        
        desc_label = tk.Label(
            self.root,
            text="NHẤN TỔ HỢP PHÍM BẠN MUỐN SỬ DỤNG:",
            font=desc_font,
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        desc_label.pack(pady=(0, 20))
        
        self.status_label = tk.Label(
            self.root,
            text="ĐANG CHỜ BẠN NHẤN PHÍM...",
            font=desc_font,
            bg="#2c3e50",
            fg="#f39c12"
        )
        self.status_label.pack(pady=10)
        
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        cancel_btn = tk.Button(
            button_frame,
            text="HUY",
            font=button_font,
            bg="#e74c3c",
            fg="white",
            relief="flat",
            command=self.cancel,
            width=15,
            height=2
        )
        cancel_btn.pack(padx=10)
        
        # Tự động bắt đầu lắng nghe sau khi UI đã sẵn sàng
        self.root.after(100, self.start_listening)
    
    def start_listening(self):
        """Bắt đầu lắng nghe phím tắt."""
        self.status_label.config(text="Đang chờ bạn nhấn phím...", fg="#f39c12")
        self.root.update()
        
        try:
            hotkey = keyboard.read_hotkey(suppress=False)
            self.hotkey = hotkey
            self.status_label.config(text=f"ĐÃ NHẬN PHÍM TẮT: {hotkey.upper()}", fg="#27ae60")
            self.root.update()
            self.root.after(2000, self.root.destroy)
            
        except Exception as e:
            self.status_label.config(text=f"LỖI: {str(e).upper()}", fg="#e74c3c")
            self.root.update()
            self.root.after(3000, self.root.destroy)
    
    def get_hotkey(self):
        """Lấy phím tắt từ người dùng."""
        self.root.mainloop()
        return self.hotkey
    
    def cancel(self):
        """Hủy nhập phím tắt."""
        self.hotkey = None
        self.root.destroy()
    
    def cleanup(self):
        """Cleanup hotkey manager và remove keyboard hooks."""
        try:
            if self.hotkey_handle:
                keyboard.unhook(self.hotkey_handle)
                self.hotkey_handle = None
            print("Hotkey manager cleaned up")
        except Exception as e:
            print(f"Loi khi cleanup hotkey manager: {e}")


def create_hotkey_manager(trigger_callback=None):
    """Tạo instance của HotkeyManager."""
    return HotkeyManager(trigger_callback)