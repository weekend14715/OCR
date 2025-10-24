"""
License Dialog
Giao diện nhập license key
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import re


class LicenseDialog:
    """Dialog nhập license key"""
    
    def __init__(self):
        self.license_key = None
        self.root = None
    
    def show(self):
        """
        Hiện dialog và đợi user nhập
        
        Returns:
            str hoặc None: License key nếu user nhập, None nếu hủy
        """
        self.root = tk.Tk()
        self.root.title("Kích hoạt OCR Tool")
        
        # Kích thước và vị trí
        window_width = 600
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        
        # Style
        self.root.configure(bg="#2c3e50")
        
        # Ngăn đóng bằng X
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._setup_ui()
        
        # Focus vào ô nhập
        self.key_entry.focus()
        
        # Chạy mainloop
        self.root.mainloop()
        
        return self.license_key
    
    def _setup_ui(self):
        """Thiết lập giao diện"""
        
        # Font
        title_font = tkFont.Font(family="Arial", size=18, weight="bold")
        desc_font = tkFont.Font(family="Arial", size=11)
        label_font = tkFont.Font(family="Arial", size=10)
        entry_font = tkFont.Font(family="Courier New", size=12, weight="bold")
        button_font = tkFont.Font(family="Arial", size=11, weight="bold")
        
        # Container chính
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Icon và Title
        title_frame = tk.Frame(main_frame, bg="#2c3e50")
        title_frame.pack(pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🔐 KÍCH HOẠT BẢN QUYỀN",
            font=title_font,
            bg="#2c3e50",
            fg="#3498db"
        )
        title_label.pack()
        
        # Mô tả
        desc_label = tk.Label(
            main_frame,
            text="Vui lòng nhập License Key để kích hoạt phần mềm",
            font=desc_font,
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        desc_label.pack(pady=(0, 10))
        
        # Hướng dẫn format
        format_label = tk.Label(
            main_frame,
            text="Định dạng: XXXX-XXXX-XXXX-XXXX (16 ký tự hex)",
            font=label_font,
            bg="#2c3e50",
            fg="#95a5a6"
        )
        format_label.pack(pady=(0, 20))
        
        # Frame nhập key
        key_frame = tk.Frame(main_frame, bg="#2c3e50")
        key_frame.pack(pady=(0, 10))
        
        key_label = tk.Label(
            key_frame,
            text="License Key:",
            font=desc_font,
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        key_label.pack(anchor="w", pady=(0, 5))
        
        # Entry với style đẹp
        self.key_entry = tk.Entry(
            key_frame,
            font=entry_font,
            width=30,
            bg="#34495e",
            fg="#ecf0f1",
            insertbackground="#ecf0f1",
            relief="flat",
            bd=2,
            highlightthickness=2,
            highlightbackground="#3498db",
            highlightcolor="#3498db"
        )
        self.key_entry.pack(ipady=8, pady=(0, 5))
        
        # Bind Enter key
        self.key_entry.bind("<Return>", lambda e: self._on_activate())
        self.key_entry.bind("<KeyRelease>", self._on_key_change)
        
        # Status label
        self.status_label = tk.Label(
            key_frame,
            text="",
            font=label_font,
            bg="#2c3e50",
            fg="#e74c3c"
        )
        self.status_label.pack(pady=(5, 0))
        
        # Link mua key
        link_frame = tk.Frame(main_frame, bg="#2c3e50")
        link_frame.pack(pady=(10, 20))
        
        link_label = tk.Label(
            link_frame,
            text="Chưa có License Key?",
            font=label_font,
            bg="#2c3e50",
            fg="#95a5a6"
        )
        link_label.pack(side="left", padx=(0, 5))
        
        buy_link = tk.Label(
            link_frame,
            text="Mua ngay tại đây",
            font=tkFont.Font(family="Arial", size=10, underline=True),
            bg="#2c3e50",
            fg="#3498db",
            cursor="hand2"
        )
        buy_link.pack(side="left")
        buy_link.bind("<Button-1>", self._on_buy_link)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.pack(pady=(10, 0))
        
        self.activate_btn = tk.Button(
            button_frame,
            text="✓ KÍCH HOẠT",
            font=button_font,
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self._on_activate
        )
        self.activate_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="✗ HỦY",
            font=button_font,
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self._on_cancel
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Info nhỏ ở dưới
        info_label = tk.Label(
            main_frame,
            text="License Key sẽ được bind với máy tính này",
            font=tkFont.Font(family="Arial", size=9, slant="italic"),
            bg="#2c3e50",
            fg="#7f8c8d"
        )
        info_label.pack(side="bottom", pady=(20, 0))
    
    def _on_key_change(self, event):
        """Callback khi user gõ key"""
        key = self.key_entry.get().strip().upper()
        
        # Auto format: tự động thêm dấu - (Format: XXXX-XXXX-XXXX-XXXX)
        if len(key) > 0:
            # Remove existing dashes for reformatting
            clean_key = key.replace('-', '')
            
            # Chỉ cho phép hex chars (0-9, A-F)
            clean_key = ''.join(c for c in clean_key if c in '0123456789ABCDEF')
            
            # Giới hạn 16 ký tự
            clean_key = clean_key[:16]
            
            # Format lại: XXXX-XXXX-XXXX-XXXX
            formatted = ''
            for i, char in enumerate(clean_key):
                if i > 0 and i % 4 == 0:
                    formatted += '-'
                formatted += char
            
            # Update nếu khác
            if formatted != key:
                cursor_pos = self.key_entry.index(tk.INSERT)
                self.key_entry.delete(0, tk.END)
                self.key_entry.insert(0, formatted)
                # Restore cursor (adjust for auto-added dashes)
                new_pos = len(formatted[:cursor_pos].replace('-', ''))
                new_pos += formatted[:new_pos].count('-')
                self.key_entry.icursor(min(new_pos, len(formatted)))
        
        # Validate realtime
        self._validate_format()
    
    def _validate_format(self):
        """Validate format của key: XXXX-XXXX-XXXX-XXXX"""
        key = self.key_entry.get().strip().upper()
        
        if not key:
            self.status_label.config(text="", fg="#e74c3c")
            return False
        
        # Check format: 4 groups × 4 hex chars
        pattern = r'^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}$'
        
        if re.match(pattern, key):
            self.status_label.config(text="✓ Định dạng hợp lệ", fg="#27ae60")
            return True
        else:
            # Nếu đang gõ dở
            if len(key) < 19:  # Chưa đủ độ dài (16 chars + 3 dashes)
                self.status_label.config(text="", fg="#e74c3c")
            else:
                self.status_label.config(text="✗ Định dạng không hợp lệ", fg="#e74c3c")
            return False
    
    def _on_activate(self):
        """Callback khi nhấn nút Kích hoạt"""
        key = self.key_entry.get().strip().upper()
        
        if not key:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập License Key!"
            )
            return
        
        # Validate format
        if not self._validate_format():
            messagebox.showerror(
                "Lỗi",
                "License Key không đúng định dạng!\n\n"
                "Định dạng đúng: XXXX-XXXX-XXXX-XXXX\n"
                "(16 ký tự hexadecimal: 0-9, A-F)"
            )
            return
        
        # Lưu key và đóng dialog
        self.license_key = key
        self.root.destroy()
    
    def _on_cancel(self):
        """Callback khi nhấn Hủy"""
        result = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc muốn hủy kích hoạt?\n\n"
            "Ứng dụng sẽ không thể chạy nếu chưa kích hoạt.",
            icon='warning'
        )
        
        if result:
            self.license_key = None
            self.root.destroy()
    
    def _on_buy_link(self, event):
        """Callback khi click link mua"""
        import webbrowser
        
        # URL trang mua (thay bằng URL thật)
        url = "https://ocr-uufr.onrender.com"
        
        try:
            webbrowser.open(url)
        except:
            messagebox.showinfo(
                "Thông tin",
                f"Vui lòng truy cập:\n{url}"
            )


if __name__ == "__main__":
    # Test
    dialog = LicenseDialog()
    key = dialog.show()
    
    if key:
        print(f"✅ User đã nhập: {key}")
    else:
        print("❌ User đã hủy")

