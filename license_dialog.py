"""
License Dialog - Giao diện nhập license key (Simplified & Fixed)
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import threading

class LicenseDialog:
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        self.dialog = None
        self._closed = False
        
    def show(self):
        """Hiển thị dialog license"""
        self.dialog = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.dialog.title("Kich Hoat License - Vietnamese OCR Tool")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Làm cho dialog luôn ở trên (không dùng grab_set để tránh lag)
        self.dialog.attributes('-topmost', True)
        
        # Xử lý đóng dialog
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._create_widgets()
        
        # Focus vào entry
        self.license_entry.focus()
        
        # Chờ dialog đóng (sử dụng cách đơn giản hơn)
        self.dialog.wait_window()
        return self.result
    
    def _on_closing(self):
        """Xử lý khi đóng dialog"""
        if not self._closed:
            self._closed = True
            self.result = False
            self.dialog.destroy()
    
    def _create_widgets(self):
        """Tạo các widget cho dialog"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_font = tkFont.Font(family="Arial", size=16, weight="bold")
        title_label = ttk.Label(
            main_frame,
            text="KICH HOAT LICENSE",
            font=title_font,
            foreground="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Thong tin License", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Instructions
        instructions = [
            "1. Mua license tai: https://ocr-uufr.onrender.com",
            "2. Sau khi thanh toan, ban se nhan duoc License Key",
            "3. Nhap License Key vao o ben duoi",
            "4. Nhan 'Kich Hoat' de su dung ung dung"
        ]
        
        for i, instruction in enumerate(instructions, 1):
            ttk.Label(
                info_frame,
                text=instruction,
                font=("Arial", 9),
                foreground="#34495e"
            ).pack(anchor=tk.W, pady=2)
        
        # License key input
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            input_frame,
            text="License Key:",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.license_entry = ttk.Entry(
            input_frame,
            font=("Consolas", 11),
            width=50,
            show="*"
        )
        self.license_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Show/Hide password button
        self.show_password = tk.BooleanVar()
        show_btn = ttk.Checkbutton(
            input_frame,
            text="Hien thi License Key",
            variable=self.show_password,
            command=self._toggle_password_visibility
        )
        show_btn.pack(anchor=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Activate button
        self.activate_btn = ttk.Button(
            button_frame,
            text="Kich Hoat License",
            command=self._activate_license
        )
        self.activate_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Thoat",
            command=self._cancel
        ).pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=("Arial", 9),
            foreground="#e74c3c"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Bind Enter key
        self.license_entry.bind('<Return>', lambda e: self._activate_license())
        
        # Bind Escape key
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _toggle_password_visibility(self):
        """Toggle hiển thị/ẩn license key"""
        if self.show_password.get():
            self.license_entry.config(show="")
        else:
            self.license_entry.config(show="*")
    
    def _activate_license(self):
        """Kích hoạt license (đơn giản hóa)"""
        if self._closed:
            return
            
        license_key = self.license_entry.get().strip()
        
        if not license_key:
            self._show_status("Vui long nhap License Key!", "error")
            return
        
        if len(license_key) < 10:
            self._show_status("License Key khong hop le!", "error")
            return
        
        # Disable button và hiển thị loading
        self.activate_btn.config(state="disabled", text="Dang kich hoat...")
        self._show_status("Dang kich hoat license...", "info")
        
        # Chạy activation trong thread riêng (đơn giản hóa)
        def do_activation():
            try:
                from license_client_integrated import LicenseClient
                
                client = LicenseClient()
                result = client.activate_license(license_key)
                
                # Update UI trong main thread (kiểm tra dialog còn tồn tại)
                if self.dialog and not self._closed:
                    try:
                        self.dialog.after(0, lambda: self._activation_complete(result))
                    except:
                        pass
                
            except Exception as e:
                error_result = {
                    'success': False,
                    'message': f"Loi kich hoat: {str(e)}"
                }
                # Update UI trong main thread (kiểm tra dialog còn tồn tại)
                if self.dialog and not self._closed:
                    try:
                        self.dialog.after(0, lambda: self._activation_complete(error_result))
                    except:
                        pass
        
        thread = threading.Thread(target=do_activation)
        thread.daemon = True
        thread.start()
    
    def _activation_complete(self, result):
        """Xử lý kết quả kích hoạt"""
        if self._closed:
            return
            
        # Enable button lại
        self.activate_btn.config(state="normal", text="Kich Hoat License")
        
        if result['success']:
            self._show_status("Kich hoat thanh cong!", "success")
            # Đóng dialog sau 1.5 giây
            self.dialog.after(1500, self._success_and_close)
        else:
            self._show_status(f"{result['message']}", "error")
    
    def _success_and_close(self):
        """Đóng dialog sau khi thành công"""
        if not self._closed:
            self._closed = True
            self.result = True
            self.dialog.destroy()
    
    def _cancel(self):
        """Hủy dialog"""
        if not self._closed:
            self._closed = True
            self.result = False
            self.dialog.destroy()
    
    def _show_status(self, message, status_type):
        """Hiển thị trạng thái"""
        colors = {
            "error": "#e74c3c",
            "success": "#27ae60",
            "info": "#3498db"
        }
        
        self.status_label.config(
            text=message,
            foreground=colors.get(status_type, "#34495e")
        )

def show_license_dialog(parent=None):
    """Hiển thị dialog license"""
    dialog = LicenseDialog(parent)
    return dialog.show()

if __name__ == "__main__":
    # Test dialog
    result = show_license_dialog()
    print(f"Result: {result}")