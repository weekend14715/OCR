import keyboard
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import pytesseract
import pyperclip
import tkinter as tk
from tkinter import font as tkFont, messagebox
from threading import Thread
import ctypes
import time
import configparser
import sys
import os
from pystray import MenuItem as item, Icon
import numpy as np

# Import License Manager
from license import LicenseManager

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
    """
    Tiền xử lý ảnh để tối ưu hóa chất lượng OCR.
    
    Các bước xử lý:
    1. Chuyển sang grayscale (giảm nhiễu màu)
    2. Tăng kích thước ảnh (upscaling) - giúp Tesseract nhận dạng tốt hơn
    3. Cân bằng histogram (tăng độ tương phản tự động)
    4. Khử nhiễu adaptive
    5. Áp dụng adaptive threshold thông minh
    6. Làm sạch nhiễu salt-and-pepper
    """
    try:
        # Bước 1: Chuyển sang grayscale
        gray_image = image.convert('L')
        print("🎨 Đã chuyển ảnh sang màu xám")
        
        # Bước 2: Upscaling - tăng kích thước ảnh lên 3x (tăng từ 2x lên 3x)
        # Tesseract hoạt động tốt hơn với ảnh có độ phân giải cao
        width, height = gray_image.size
        scale_factor = 3
        gray_image = gray_image.resize((width * scale_factor, height * scale_factor), Image.LANCZOS)
        print(f"📐 Đã tăng kích thước ảnh: {width}x{height} → {width*scale_factor}x{height*scale_factor}")
        
        # Bước 3: Cân bằng histogram để tăng độ tương phản tự động
        equalized_image = equalize_histogram(gray_image)
        print("📊 Đã cân bằng histogram")
        
        # Bước 4: Tăng độ sắc nét
        sharpness_enhancer = ImageEnhance.Sharpness(equalized_image)
        sharp_image = sharpness_enhancer.enhance(2.5)
        print("✨ Đã tăng độ sắc nét")
        
        # Bước 5: Áp dụng adaptive threshold thông minh
        threshold_image = apply_adaptive_threshold(sharp_image)
        print("⚫⚪ Đã áp dụng adaptive threshold")
        
        # Bước 6: Khử nhiễu salt-and-pepper (nhiễu điểm trắng đen)
        cleaned_image = remove_noise(threshold_image)
        print("🧹 Đã làm sạch nhiễu")
        
        # Bước 7: Làm mịn viền chữ (morphological operations)
        final_image = smooth_text(cleaned_image)
        print("🎯 Đã làm mịn viền chữ")
        
        return final_image
        
    except Exception as e:
        print(f"⚠ Lỗi khi tiền xử lý ảnh: {e}")
        # Nếu có lỗi, trả về ảnh grayscale đơn giản
        return image.convert('L')

def apply_threshold(image):
    """
    Áp dụng adaptive threshold để tạo ảnh đen trắng rõ ràng.
    Sử dụng Otsu's method để tự động tìm ngưỡng tối ưu.
    """
    try:
        # Chuyển PIL Image sang numpy array
        img_array = np.array(image)
        
        # Tính histogram
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        # Otsu's method để tìm threshold tối ưu
        total_pixels = img_array.size
        current_max = 0
        threshold = 0
        sum_total = np.sum(np.arange(256) * hist)
        sum_background = 0
        weight_background = 0
        
        for i in range(256):
            weight_background += hist[i]
            if weight_background == 0:
                continue
            
            weight_foreground = total_pixels - weight_background
            if weight_foreground == 0:
                break
            
            sum_background += i * hist[i]
            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground
            
            variance_between = weight_background * weight_foreground * \
                             (mean_background - mean_foreground) ** 2
            
            if variance_between > current_max:
                current_max = variance_between
                threshold = i
        
        # Áp dụng threshold
        binary_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        # Chuyển lại sang PIL Image
        threshold_image = Image.fromarray(binary_array)
        
        print(f"🎯 Threshold tối ưu: {threshold}")
        return threshold_image
        
    except Exception as e:
        print(f"⚠ Lỗi khi áp dụng threshold: {e}")
        # Fallback: sử dụng threshold cố định
        return image.point(lambda p: 255 if p > 128 else 0)

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
        """
        Thực hiện nhận dạng văn bản trên ảnh với tiền xử lý tối ưu.
        """
        try:
            print("\n" + "="*55)
            print("⏳ BẮT ĐẦU QUÁ TRÌNH OCR")
            print("="*55)
            
            # Tiền xử lý ảnh để tối ưu hóa OCR
            processed_image = preprocess_image(image)
            
            print("\n🔍 Đang nhận dạng văn bản...")
            
            # Cấu hình Tesseract để tối ưu cho tiếng Việt
            custom_config = r'--oem 3 --psm 6'
            # --oem 3: Sử dụng LSTM neural network (tốt nhất)
            # --psm 6: Giả định văn bản là một khối thống nhất
            
            # Sử dụng 'vie' để nhận dạng tiếng Việt
            text = pytesseract.image_to_string(
                processed_image, 
                lang='vie',
                config=custom_config
            )
            
            # Làm sạch text
            text = text.strip()
            
            if text:
                pyperclip.copy(text)
                print("\n" + "="*55)
                print("✓ HOÀN THÀNH - ĐÃ COPY VÀO CLIPBOARD!")
                print("="*55)
                
                # Hiển thị nội dung
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
                print("="*55)
                print("💡 Gợi ý:")
                print("   • Chọn vùng có chữ rõ ràng hơn")
                print("   • Tăng kích thước vùng chọn")
                print("   • Đảm bảo chữ có độ tương phản tốt với nền")
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

class HotkeySelectorWindow:
    """Tạo cửa sổ chọn phím tắt với các tùy chọn có sẵn."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chọn phím tắt OCR")
        self.root.attributes('-topmost', True)
        self.root.geometry("500x450")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"500x450+{x}+{y}")
        
        self.selected_hotkey = None
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng."""
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
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"500x300+{x}+{y}")
        
        self.setup_ui()
        self.hotkey = None
    
    def setup_ui(self):
        """Thiết lập giao diện."""
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
            text="Nhấn tổ hợp phím bạn muốn sử dụng:",
            font=desc_font,
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        desc_label.pack(pady=(0, 20))
        
        self.status_label = tk.Label(
            self.root,
            text="Đang chờ bạn nhấn phím...",
            font=desc_font,
            bg="#2c3e50",
            fg="#f39c12"
        )
        self.status_label.pack(pady=10)
        
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ HỦY",
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
            self.status_label.config(text=f"Đã nhận phím tắt: {hotkey}", fg="#27ae60")
            self.root.update()
            self.root.after(2000, self.root.destroy)
            
        except Exception as e:
            self.status_label.config(text=f"Lỗi: {str(e)}", fg="#e74c3c")
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

# ==============================================================================
# PHẦN QUẢN LÝ CẤU HÌNH VÀ PHÍM TẮT
# ==============================================================================

def save_hotkey(hotkey_str):
    """Lưu phím tắt vào file config.ini."""
    config = configparser.ConfigParser()
    config['Settings'] = {'hotkey': hotkey_str}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print(f"✓ Đã lưu phím tắt mới: {hotkey_str}")

def load_hotkey():
    """Tải phím tắt từ file config.ini."""
    if not os.path.exists(CONFIG_FILE):
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config.get('Settings', 'hotkey', fallback=None)

def prompt_for_hotkey():
    """Hiển thị giao diện chọn phím tắt."""
    print("\n" + "="*55)
    print("✨ VUI LÒNG CHỌN PHÍM TẮT ✨")
    print("="*55)

    selector = HotkeySelectorWindow()
    new_hotkey = selector.get_hotkey()

    if new_hotkey:
        print(f"\n✓ Bạn đã chọn: {new_hotkey}")
        save_hotkey(new_hotkey)
        return new_hotkey
    else:
        # Nếu không chọn được, dùng mặc định
        default_hotkey = "ctrl+q"
        print(f"\n⚠ Sử dụng phím tắt mặc định: {default_hotkey}")
        save_hotkey(default_hotkey)
        return default_hotkey

def register_new_hotkey(new_hotkey):
    """Hủy phím tắt cũ và đăng ký phím tắt mới."""
    global current_hotkey, hotkey_handle
    if hotkey_handle:
        keyboard.remove_hotkey(hotkey_handle)

    current_hotkey = new_hotkey
    hotkey_handle = keyboard.add_hotkey(current_hotkey, trigger_ocr_selection)

    if app_icon:
        app_icon.title = f"OCR Tool (Hotkey: {current_hotkey})"

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

    menu = (
        item('Thay đổi phím tắt', change_hotkey_action),
        item('Thoát', exit_action)
    )

    app_icon = Icon("OCRTool", image, f"OCR Tool (Hotkey: {current_hotkey})", menu)
    app_icon.run()

# ==============================================================================
# HÀM MAIN CHÍNH
# ==============================================================================

def main():
    global current_hotkey

    is_startup_run = "--startup" in sys.argv

    set_dpi_awareness()

    # ============================================================================
    # KIỂM TRA BẢN QUYỀN TRƯỚC KHI CHẠY APP
    # ============================================================================
    try:
        license_manager = LicenseManager()
        
        if not license_manager.check_license():
            print("\n" + "="*60)
            print("❌ KHÔNG THỂ KÍCH HOẠT BẢN QUYỀN")
            print("="*60)
            print("Ứng dụng sẽ thoát sau 3 giây...")
            print("="*60 + "\n")
            
            # Hiển thị messagebox nếu không phải startup
            if not is_startup_run:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "Lỗi Bản Quyền",
                    "Không thể kích hoạt bản quyền!\n\n"
                    "Vui lòng kiểm tra License Key và thử lại."
                )
                root.destroy()
            
            time.sleep(3)
            sys.exit(1)
        
        print("\n" + "="*60)
        print("✅ BẢN QUYỀN HỢP LỆ - Đang khởi động ứng dụng...")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Lỗi kiểm tra bản quyền: {e}")
        print("Ứng dụng sẽ thoát sau 3 giây...\n")
        time.sleep(3)
        sys.exit(1)
    
    # ============================================================================
    # KHỞI ĐỘNG ỨNG DỤNG BÌNH THƯỜNG
    # ============================================================================

    if not is_startup_run:
        print("=" * 55)
        print("    Vietnamese OCR Tool - Optimized Version")
        print("=" * 55)
        print("\n🚀 Tính năng tối ưu hóa:")
        print("   ✓ Grayscale conversion (chuyển màu xám)")
        print("   ✓ Image upscaling 2x (tăng độ phân giải)")
        print("   ✓ Contrast enhancement (tăng độ tương phản)")
        print("   ✓ Sharpness enhancement (tăng độ sắc nét)")
        print("   ✓ Noise reduction (khử nhiễu)")
        print("   ✓ Adaptive thresholding (ngưỡng hóa thông minh)")
        print("   ✓ Tesseract LSTM mode (AI nhận dạng)")
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
        print("    • Chuột phải vào icon ở khay hệ thống để thay đổi")
        print("=" * 55 + "\n")
        print("🚀 Ứng dụng đang chạy ở chế độ nền...")

    setup_and_run_tray_app()

if __name__ == "__main__":
    main()