#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Email Configuration Template - OCR Tool License System

HƯỚNG DẪN:
1. Copy file này thành email_config.py
2. Điền thông tin email và App Password của bạn
3. KHÔNG commit file email_config.py lên Git!
"""

# ============================================================================
# EMAIL ACCOUNTS CONFIGURATION
# ============================================================================

EMAIL_ACCOUNTS = [
    {
        'email': 'your-email-1@gmail.com',        # ← ĐỔI THÀNH EMAIL CỦA BẠN
        'password': 'your-app-password-here',     # ← APP PASSWORD (16 ký tự, không dấu cách)
        'name': 'OCR License System',
        'daily_limit': 500,
        'description': 'Tài khoản chính'
    },
    {
        'email': 'your-email-2@gmail.com',        # ← ĐỔI THÀNH EMAIL THỨ 2
        'password': 'your-app-password-here',     # ← APP PASSWORD THỨ 2
        'name': 'OCR License System',
        'daily_limit': 500,
        'description': 'Tài khoản backup'
    }
]

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USE_TLS = True

# Email Templates
DEFAULT_FROM_NAME = 'OCR Tool License'
SUPPORT_EMAIL = 'your-support-email@gmail.com'  # ← ĐỔI THÀNH EMAIL SUPPORT

# Tracking (optional)
ENABLE_TRACKING = True
TRACK_FILE = 'email_usage.json'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_email_accounts():
    """Trả về danh sách email accounts"""
    return EMAIL_ACCOUNTS


def get_smtp_config():
    """Trả về cấu hình SMTP"""
    return {
        'server': SMTP_SERVER,
        'port': SMTP_PORT,
        'use_tls': SMTP_USE_TLS
    }


def get_account_by_email(email):
    """Tìm account theo email"""
    for account in EMAIL_ACCOUNTS:
        if account['email'] == email:
            return account
    return None


def get_total_daily_limit():
    """Tính tổng số email có thể gửi mỗi ngày"""
    return sum(acc['daily_limit'] for acc in EMAIL_ACCOUNTS)


def print_config_summary():
    """In ra thông tin cấu hình"""
    print("\n" + "="*70)
    print("📧 EMAIL CONFIGURATION SUMMARY")
    print("="*70)
    
    for i, acc in enumerate(EMAIL_ACCOUNTS, 1):
        print(f"\nTÀI KHOẢN {i}:")
        print(f"  Email: {acc['email']}")
        print(f"  Name: {acc['name']}")
        print(f"  Daily Limit: {acc['daily_limit']} emails/day")
        print(f"  Description: {acc['description']}")
    
    print("\n" + "─"*70)
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"TLS: {'Enabled' if SMTP_USE_TLS else 'Disabled'}")
    print(f"Total Daily Limit: {get_total_daily_limit()} emails/day")
    print("="*70 + "\n")


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

"""
📋 HƯỚNG DẪN SETUP:

1. TẠO TÀI KHOẢN GMAIL:
   • Tạo 2 tài khoản Gmail mới (hoặc dùng tài khoản có sẵn)
   • Ví dụ: 
     - yourproject.license@gmail.com
     - yourproject.system@gmail.com

2. BẬT 2-STEP VERIFICATION:
   • Vào: https://myaccount.google.com/security
   • Tìm "2-Step Verification"
   • Bật lên (làm theo hướng dẫn của Google)

3. TẠO APP PASSWORD:
   • Vào: https://myaccount.google.com/apppasswords
   • Select app: Mail
   • Select device: Other (Custom name)
   • Nhập tên: "OCR License System"
   • Copy mã 16 ký tự

4. CẤU HÌNH FILE NÀY:
   • Copy file email_config.example.py → email_config.py
   • Điền email và App Password vào EMAIL_ACCOUNTS
   • Bỏ dấu cách trong App Password (vd: "abcd efgh ijkl mnop" → "abcdefghijklmnop")

5. TEST:
   • Chạy: python test_email_config.py
   • Test gửi email
   • Kiểm tra email nhận được

6. BẢO MẬT:
   • KHÔNG commit file email_config.py lên Git
   • File .gitignore đã được cấu hình để ignore file này
   • Backup App Password cẩn thận (không thể xem lại)

═══════════════════════════════════════════════════════════════

⚠️  LƯU Ý QUAN TRỌNG:

• App Password khác với mật khẩu Gmail thông thường
• Mỗi App Password chỉ hiện 1 lần
• Gmail giới hạn 500 emails/account/day
• Hệ thống tự động chuyển đổi giữa 2 accounts

═══════════════════════════════════════════════════════════════

📧 Support: hoangtuan.th484@gmail.com
📖 Docs: EMAIL_SYSTEM_GUIDE.md

═══════════════════════════════════════════════════════════════
"""


if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ⚠️  ĐÂY LÀ FILE MẪU - CHƯA CẤU HÌNH                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Hướng dẫn:

1. Copy file này:
   
   cp email_config.example.py email_config.py

2. Sửa file email_config.py:
   
   • Điền email của bạn
   • Điền App Password
   • Điền support email

3. Test:
   
   python test_email_config.py

4. Đọc hướng dẫn chi tiết:
   
   Xem file: EMAIL_SYSTEM_GUIDE.md

═══════════════════════════════════════════════════════════════

📧 Cần hỗ trợ? Email: hoangtuan.th484@gmail.com

═══════════════════════════════════════════════════════════════
""")
    
    # Hiển thị config mẫu
    print_config_summary()

