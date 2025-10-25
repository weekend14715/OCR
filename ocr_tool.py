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
import signal
from pystray import MenuItem as item, Icon
import numpy as np

# Import License Manager
from license import LicenseManager

# Import Hotkey Manager
from Hotkey.hotkey_manager import HotkeyManager

# --- CẤU HÌNH ---

APP_NAME = "VietnameseOCRTool" 
CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME) 
os.makedirs(CONFIG_DIR, exist_ok=True) 
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')
ICON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.ico')

def get_tesseract_path():
    """Tìm đường dẫn đến tesseract.exe một cách linh động."""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        tesseract_path = os.path.join(application_path, 'Tesseract-OCR', 'tesseract.exe')
    else:
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    print(f"Duong dan Tesseract duoc su dung: {tesseract_path}")
    return tesseract_path

try:
    pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()
except Exception as e:
    print(f"Loi khi thiet lap Tesseract: {e}")

# --- BIẾN TOÀN CỤC ---
hotkey_manager = None
app_icon = None

def cleanup_and_exit():
    """Cleanup toàn bộ và thoát ứng dụng."""
    global hotkey_manager, app_icon
    
    print("\nDang cleanup...")
    
    # Cleanup hotkey manager
    if hotkey_manager:
        try:
            hotkey_manager.cleanup()
        except:
            pass
    
    # Cleanup pystray
    try:
        if app_icon:
            app_icon.stop()
        import pystray
        pystray.Icon.stop_all()
    except:
        pass
    
    print("Cleanup hoan tat")
    os._exit(0)

def signal_handler(signum, frame):
    """Xử lý signal để cleanup khi app bị terminate."""
    cleanup_and_exit()

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
        print("Da lam sach nhieu")
        
        # Bước 7: Làm mịn viền chữ (morphological operations)
        final_image = smooth_text(cleaned_image)
        print("🎯 Đã làm mịn viền chữ")
        
        return final_image
        
    except Exception as e:
        print(f"Loi khi tien xu ly anh: {e}")
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
        print(f"Loi khi ap dung threshold: {e}")
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
            print("Vung chon qua nho!")

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
                print("HOAN THANH - DA COPY VAO CLIPBOARD!")
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
                print("KHONG NHAN DIEN DUOC CHU!")
                print("="*55)
                print("💡 Gợi ý:")
                print("   • Chọn vùng có chữ rõ ràng hơn")
                print("   • Tăng kích thước vùng chọn")
                print("   • Đảm bảo chữ có độ tương phản tốt với nền")
                print("="*55 + "\n")
                
        except Exception as e:
            print(f"\nLOI KHI NHAN DIEN: {e}\n")

def trigger_ocr_selection():
    """Hàm được gọi khi nhấn phím tắt."""
    current_hotkey = hotkey_manager.get_current_hotkey() if hotkey_manager else "unknown"
    print(f"\n▶ Đã nhấn phím tắt '{current_hotkey}' - Bắt đầu chọn vùng...")
    Thread(target=lambda: ScreenSelector().start(), daemon=True).start()

# ==============================================================================
# PHẦN QUẢN LÝ CẤU HÌNH VÀ PHÍM TẮT (ĐÃ CHUYỂN VÀO HOTKEY MANAGER)
# ==============================================================================

# ==============================================================================
# PHẦN QUẢN LÝ ICON TRÊN SYSTEM TRAY
# ==============================================================================

def change_hotkey_action():
    """Hành động được gọi khi người dùng chọn 'Thay đổi phím tắt'."""
    if hotkey_manager:
        # Chạy trong thread riêng để tránh block system tray
        Thread(target=hotkey_manager.change_hotkey_from_tray, daemon=True).start()

def exit_action(icon):
    """Hành động thoát ứng dụng."""
    print("\nDa thoat!")
    cleanup_and_exit()

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
        print(f"Loi: Khong tim thay file '{ICON_FILE}'. Su dung icon mac dinh.")
        image = Image.new('RGB', (64, 64), 'black')

    menu = (
        item('Thay đổi phím tắt', change_hotkey_action),
        item('Thoát', exit_action)
    )

    current_hotkey = hotkey_manager.get_current_hotkey() if hotkey_manager else "unknown"
    app_icon = Icon("OCRTool", image, f"OCR Tool (Hotkey: {current_hotkey})", menu)
    app_icon.run()

# ==============================================================================
# HÀM MAIN CHÍNH
# ==============================================================================

def main():
    global hotkey_manager

    is_startup_run = "--startup" in sys.argv

    set_dpi_awareness()
    
    # Setup signal handlers để cleanup khi app bị terminate
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # ============================================================================
    # KIỂM TRA BẢN QUYỀN TRƯỚC KHI CHẠY APP
    # ============================================================================
    try:
        license_manager = LicenseManager()
        
        if not license_manager.check_license():
            print("\n" + "="*60)
            print("KHONG THE KICH HOAT BAN QUYEN")
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
        print("BAN QUYEN HOP LE - Dang khoi dong ung dung...")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nLoi kiem tra ban quyen: {e}")
        print("Ứng dụng sẽ thoát sau 3 giây...\n")
        time.sleep(3)
        sys.exit(1)
    
    # ============================================================================
    # KHỞI TẠO HOTKEY MANAGER
    # ============================================================================
    hotkey_manager = HotkeyManager(trigger_callback=trigger_ocr_selection)
    
    # ============================================================================
    # KHỞI ĐỘNG ỨNG DỤNG BÌNH THƯỜNG
    # ============================================================================

    if not is_startup_run:
        print("=" * 55)
        print("    Vietnamese OCR Tool - Optimized Version")
        print("=" * 55)
        print("\nTinh nang toi uu hoa:")
        print("   - Grayscale conversion (chuyen mau xam)")
        print("   - Image upscaling 2x (tang do phan giai)")
        print("   - Contrast enhancement (tang do tuong phan)")
        print("   - Sharpness enhancement (tang do sac net)")
        print("   - Noise reduction (khu nhieu)")
        print("   - Adaptive thresholding (nguong hoa thong minh)")
        print("   - Tesseract LSTM mode (AI nhan dang)")
        print("=" * 55 + "\n")

    # Tải phím tắt từ config hoặc yêu cầu người dùng chọn
    loaded_key = hotkey_manager.load_hotkey()
    
    if not loaded_key:
        hotkey_manager.prompt_for_hotkey()
        loaded_key = hotkey_manager.get_current_hotkey()
    
    # Đăng ký phím tắt
    if loaded_key:
        hotkey_manager.register_hotkey(loaded_key)
        if not is_startup_run:
            print(f"Da tai phim tat da luu: {loaded_key}")

    if not is_startup_run:
        current_hotkey = hotkey_manager.get_current_hotkey()
        print("\nHuong dan:")
        print(f"    - Nhan '{current_hotkey}' de chon vung can OCR")
        print("    - Nhan ESC de huy chon vung")
        print("    - Chuot phai vao icon o khay he thong de thay doi")
        print("=" * 55 + "\n")
        print("Ung dung dang chay o che do nen...")

    setup_and_run_tray_app()

if __name__ == "__main__":
    main()