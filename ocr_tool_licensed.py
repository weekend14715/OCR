import keyboard
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import pytesseract
import pyperclip
import tkinter as tk
from tkinter import font as tkFont, messagebox, simpledialog
from threading import Thread
import ctypes
import time
import configparser
import sys
import os
from pystray import MenuItem as item, Icon
import numpy as np

# Import license client
try:
    from license_client import LicenseManager
    LICENSE_ENABLED = True
except ImportError:
    print("⚠️ License module not found. Running in trial mode.")
    LICENSE_ENABLED = False

# --- CẤU HÌNH ---

APP_NAME = "VietnameseOCRTool" 
CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME) 
os.makedirs(CONFIG_DIR, exist_ok=True) 
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')
ICON_FILE = 'icon.png'

def get_tesseract_path():
    """Tìm đường dẫn đến tesseract.exe một cách linh động."""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        tesseract_path = os.path.join(application_path, 'Tesseract-OCR', 'tesseract.exe')
    else:
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    print(f"Đường dẫn Tesseract được sử dụng: {tesseract_path}")
    return tesseract_path

try:
    pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()
except Exception as e:
    print(f"Lỗi khi thiết lập Tesseract: {e}")

# --- BIẾN TOÀN CỤC ---
current_hotkey = None
hotkey_handle = None
app_icon = None
license_manager = None
is_licensed = False

# ==============================================================================
# LICENSE MANAGEMENT
# ==============================================================================

def check_license():
    """Kiểm tra license khi khởi động"""
    global license_manager, is_licensed
    
    if not LICENSE_ENABLED:
        print("⚠️ License system disabled. Running in trial mode.")
        return True
    
    license_manager = LicenseManager()
    
    # Kiểm tra license hiện tại
    is_valid, message = license_manager.check_license_status()
    
    if is_valid:
        print(f"✅ {message}")
        is_licensed = True
        return True
    else:
        print(f"❌ {message}")
        is_licensed = False
        return False

def show_license_activation_dialog():
    """Hiển thị dialog yêu cầu nhập license key"""
    root = tk.Tk()
    root.withdraw()
    
    while True:
        license_key = simpledialog.askstring(
            "License Activation",
            "Vui lòng nhập License Key của bạn:\n(Format: XXXX-XXXX-XXXX-XXXX)",
            parent=root
        )
        
        if license_key is None:
            # User clicked Cancel
            response = messagebox.askyesno(
                "Thoát",
                "Ứng dụng cần license key để chạy.\nBạn có muốn thoát không?",
                parent=root
            )
            if response:
                root.destroy()
                return False
            else:
                continue
        
        # Validate license
        print(f"\n⏳ Đang xác thực license: {license_key}")
        result = license_manager.activate_license(license_key)
        
        if result.get('valid'):
            messagebox.showinfo(
                "Thành công",
                f"✅ License đã được kích hoạt thành công!\n\n"
                f"Gói: {result.get('plan', 'N/A').upper()}\n"
                f"Hết hạn: {result.get('expires', 'Vĩnh viễn')}",
                parent=root
            )
            root.destroy()
            global is_licensed
            is_licensed = True
            return True
        else:
            error_msg = result.get('error', 'Unknown error')
            messagebox.showerror(
                "Lỗi",
                f"❌ Không thể kích hoạt license:\n\n{error_msg}",
                parent=root
            )

def show_license_info():
    """Hiển thị thông tin license hiện tại"""
    if not LICENSE_ENABLED or not license_manager:
        messagebox.showinfo("License Info", "License system is disabled.")
        return
    
    is_valid, message = license_manager.check_license_status()
    
    if is_valid:
        messagebox.showinfo("License Information", f"✅ {message}")
    else:
        response = messagebox.askyesno(
            "License Invalid",
            f"❌ {message}\n\nBạn có muốn nhập license key mới không?",
        )
        if response:
            show_license_activation_dialog()

def deactivate_license_action():
    """Xóa license khỏi máy này"""
    if not LICENSE_ENABLED or not license_manager:
        messagebox.showinfo("License", "License system is disabled.")
        return
    
    response = messagebox.askyesno(
        "Deactivate License",
        "Bạn có chắc muốn xóa license khỏi máy này?\n\n"
        "Bạn có thể kích hoạt lại trên máy khác sau."
    )
    
    if response:
        license_manager.deactivate_license()
        messagebox.showinfo("Success", "✅ Đã xóa license khỏi máy này.")
        global is_licensed
        is_licensed = False

# ==============================================================================
# PHẦN XỬ LÝ DPI VÀ GIAO DIỆN CHỌN VÙNG
# ==============================================================================

def set_dpi_awareness():
    """Cải thiện độ sắc nét của giao diện trên màn hình có độ phân giải cao."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ==============================================================================
# PHẦN TIỀN XỬ LÝ ẢNH TỐI ƯU
# ==============================================================================

def preprocess_image(image):
    """Tiền xử lý ảnh để tối ưu hóa chất lượng OCR."""
    try:
        gray_image = image.convert('L')
        width, height = gray_image.size
        scale_factor = 3
        gray_image = gray_image.resize((width * scale_factor, height * scale_factor), Image.LANCZOS)
        
        # Simple enhancement
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced = enhancer.enhance(2.0)
        
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
        sharp_image = sharpness_enhancer.enhance(2.5)
        
        return sharp_image
        
    except Exception as e:
        print(f"⚠ Lỗi khi tiền xử lý ảnh: {e}")
        return image.convert('L')

# ==============================================================================
# LỚP XỬ LÝ CHỌN VÙNG MÀN HÌNH
# ==============================================================================

class ScreenSelector:
    """Lớp xử lý việc vẽ hình chữ nhật trên màn hình để chọn vùng OCR."""
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.root = None
        self.canvas = None
        self.rect = None

    def start(self):
        """Khởi tạo và hiển thị cửa sổ chọn vùng."""
        # Check license before allowing OCR
        if LICENSE_ENABLED and not is_licensed:
            messagebox.showerror("License Required", "Vui lòng kích hoạt license để sử dụng OCR!")
            return
        
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0, cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<Escape>', lambda e: self.cancel())
        self.root.mainloop()

    def on_press(self, event):
        """Lưu tọa độ khi nhấn chuột."""
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        """Vẽ hình chữ nhật khi kéo chuột."""
        if self.start_x is not None:
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y, outline='red', width=2)

    def on_release(self, event):
        """Xử lý khi nhả chuột: chụp ảnh và OCR."""
        end_x, end_y = event.x, event.y
        self.root.destroy()
        time.sleep(0.2)

        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        print(f"Vùng chọn: ({x1}, {y1}) → ({x2}, {y2})")
        if x2 - x1 > 5 and y2 - y1 > 5:
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.ocr(screenshot)
        else:
            print("⚠ Vùng chọn quá nhỏ!")

    def cancel(self):
        """Hủy thao tác chọn vùng."""
        print("✖ Đã hủy!")
        self.root.destroy()

    def ocr(self, image):
        """Thực hiện nhận dạng văn bản trên ảnh với tiền xử lý tối ưu."""
        try:
            print("\n" + "="*55)
            print("⏳ BẮT ĐẦU QUÁ TRÌNH OCR")
            print("="*55)
            
            processed_image = preprocess_image(image)
            
            print("\n🔍 Đang nhận dạng văn bản...")
            
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(
                processed_image, 
                lang='vie',
                config=custom_config
            )
            
            text = text.strip()
            
            if text:
                pyperclip.copy(text)
                print("\n" + "="*55)
                print("✓ HOÀN THÀNH - ĐÃ COPY VÀO CLIPBOARD!")
                print("="*55)
                
                if len(text) > 200:
                    print(f"📝 Nội dung (200 ký tự đầu):\n{text[:200]}...")
                else:
                    print(f"📝 Nội dung:\n{text}")
                    
                print(f"\n📊 Độ dài: {len(text)} ký tự")
                print(f"📄 Số dòng: {text.count(chr(10)) + 1}")
                print("="*55 + "\n")
            else:
                print("\n" + "="*55)
                print("⚠ KHÔNG NHẬN DIỆN ĐƯỢC CHỮ!")
                print("="*55 + "\n")
                
        except Exception as e:
            print(f"\n❌ LỖI KHI NHẬN DIỆN: {e}\n")

def trigger_ocr_selection():
    """Hàm được gọi khi nhấn phím tắt."""
    print(f"\n▶ Đã nhấn phím tắt '{current_hotkey}' - Bắt đầu chọn vùng...")
    Thread(target=lambda: ScreenSelector().start(), daemon=True).start()

# ==============================================================================
# GIAO DIỆN YÊU CẦU NHẬP PHÍM TẮT
# ==============================================================================

class HotkeyPromptWindow:
    """Tạo một cửa sổ overlay để yêu cầu người dùng nhập phím tắt."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.75)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')

        prompt_font = tkFont.Font(family="Arial", size=28, weight="bold")
        label = tk.Label(
            self.root,
            text="Hãy nhấn tổ hợp phím bạn muốn dùng để quét",
            font=prompt_font,
            bg="black",
            fg="white"
        )
        label.place(relx=0.5, rely=0.5, anchor='center')

    def get_hotkey(self):
        """Hiển thị cửa sổ, chờ người dùng nhập và trả về phím tắt."""
        self.root.update()
        hotkey = keyboard.read_hotkey(suppress=False)
        self.root.destroy()
        return hotkey

# ==============================================================================
# PHẦN QUẢN LÝ CẤU HÌNH VÀ PHÍM TẮT
# ==============================================================================

def save_hotkey(hotkey_str):
    """Lưu phím tắt vào file config.ini."""
    config = configparser.ConfigParser()
    config['Settings'] = {'hotkey': hotkey_str}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"✓ Đã lưu phím tắt mới: {hotkey_str}")

def load_hotkey():
    """Tải phím tắt từ file config.ini."""
    if not os.path.exists(CONFIG_FILE):
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config.get('Settings', 'hotkey', fallback=None)

def prompt_for_hotkey():
    """Sử dụng HotkeyPromptWindow để yêu cầu người dùng nhập phím tắt."""
    print("\n" + "="*55)
    print("✨ VUI LÒNG ĐẶT TỔ HỢP PHÍM TẮT ✨")
    print("Một cửa sổ sẽ hiện lên, hãy nhấn phím tắt của bạn.")
    print("="*55)

    prompt_window = HotkeyPromptWindow()
    new_hotkey = prompt_window.get_hotkey()

    print(f"\nBạn đã chọn: {new_hotkey}")
    save_hotkey(new_hotkey)
    return new_hotkey

def register_new_hotkey(new_hotkey):
    """Hủy phím tắt cũ và đăng ký phím tắt mới."""
    global current_hotkey, hotkey_handle
    if hotkey_handle:
        keyboard.remove_hotkey(hotkey_handle)

    current_hotkey = new_hotkey
    hotkey_handle = keyboard.add_hotkey(current_hotkey, trigger_ocr_selection)

    if app_icon:
        license_status = "✅ Licensed" if is_licensed else "⚠️ Trial"
        app_icon.title = f"OCR Tool ({license_status}) | Hotkey: {current_hotkey}"

# ==============================================================================
# PHẦN QUẢN LÝ ICON TRÊN SYSTEM TRAY
# ==============================================================================

def change_hotkey_action():
    """Hành động được gọi khi người dùng chọn 'Thay đổi phím tắt'."""
    print("\n🔄 Bắt đầu thay đổi phím tắt...")
    new_hotkey = prompt_for_hotkey()
    register_new_hotkey(new_hotkey)

def exit_action(icon):
    """Hành động thoát ứng dụng."""
    print("\n👋 Đã thoát!")
    icon.stop()
    os._exit(0)

def setup_and_run_tray_app():
    """Thiết lập và chạy icon trên khay hệ thống."""
    global app_icon
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        icon_path = os.path.join(base_path, ICON_FILE)
        image = Image.open(icon_path)
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file '{ICON_FILE}'. Sử dụng icon mặc định.")
        image = Image.new('RGB', (64, 64), 'black')

    # Tạo menu với license options
    if LICENSE_ENABLED:
        menu = (
            item('Thay đổi phím tắt', change_hotkey_action),
            item('License Info', show_license_info),
            item('Deactivate License', deactivate_license_action),
            item('Thoát', exit_action)
        )
    else:
        menu = (
            item('Thay đổi phím tắt', change_hotkey_action),
            item('Thoát', exit_action)
        )

    license_status = "✅ Licensed" if is_licensed else "⚠️ Trial"
    app_icon = Icon("OCRTool", image, f"OCR Tool ({license_status}) | Hotkey: {current_hotkey}", menu)
    app_icon.run()

# ==============================================================================
# HÀM MAIN CHÍNH
# ==============================================================================

def main():
    global current_hotkey

    is_startup_run = "--startup" in sys.argv

    set_dpi_awareness()

    if not is_startup_run:
        print("=" * 55)
        print("    Vietnamese OCR Tool - Licensed Version")
        print("=" * 55)
    
    # Check license
    if LICENSE_ENABLED:
        if not check_license():
            # License invalid, show activation dialog
            if not show_license_activation_dialog():
                print("\n❌ Không có license hợp lệ. Thoát ứng dụng.")
                sys.exit(1)
    
    if not is_startup_run:
        print("\n🚀 Tính năng tối ưu hóa:")
        print("   ✓ Grayscale conversion")
        print("   ✓ Image upscaling 3x")
        print("   ✓ Contrast enhancement")
        print("   ✓ Sharpness enhancement")
        print("   ✓ Tesseract LSTM mode")
        print("=" * 55 + "\n")

    loaded_key = load_hotkey()
    
    if not loaded_key:
        change_hotkey_action()
    else:
        current_hotkey = loaded_key
        if not is_startup_run:
            print(f"✓ Đã tải phím tắt đã lưu: {current_hotkey}")
        register_new_hotkey(current_hotkey)

    if not is_startup_run:
        print("\n📖 Hướng dẫn:")
        print(f"    • Nhấn '{current_hotkey}' để chọn vùng cần OCR")
        print("    • Nhấn ESC để hủy chọn vùng")
        print("    • Chuột phải vào icon ở khay hệ thống để xem license")
        print("=" * 55 + "\n")
        print("🚀 Ứng dụng đang chạy ở chế độ nền...")

    setup_and_run_tray_app()

if __name__ == "__main__":
    main()

