"""
Demo app đơn giản để test code signing
Tạo file .exe nhỏ để test sign nhanh
"""

import tkinter as tk
from tkinter import messagebox
import sys

def main():
    """Simple GUI app for testing"""
    
    root = tk.Tk()
    root.title("OCR License System - Demo")
    root.geometry("400x300")
    root.resizable(False, False)
    
    # Header
    header = tk.Label(
        root, 
        text="🔐 Code Signing Demo",
        font=("Arial", 18, "bold"),
        pady=20
    )
    header.pack()
    
    # Info
    info_text = """
    Đây là demo app để test code signing!
    
    ✅ App này đã được ký số (signed)
    ✅ Self-signed certificate
    ✅ Giảm cảnh báo Windows SmartScreen
    
    Version: 1.0.0
    """
    
    info = tk.Label(
        root,
        text=info_text,
        font=("Arial", 10),
        justify="left",
        pady=20
    )
    info.pack()
    
    # Button
    def show_message():
        messagebox.showinfo(
            "Success", 
            "✅ App hoạt động bình thường!\n\nCode signing thành công!"
        )
    
    btn = tk.Button(
        root,
        text="Test App",
        command=show_message,
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=10,
        cursor="hand2"
    )
    btn.pack(pady=20)
    
    # Footer
    footer = tk.Label(
        root,
        text="© 2024 OCR License System",
        font=("Arial", 8),
        fg="gray"
    )
    footer.pack(side="bottom", pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()

