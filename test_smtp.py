#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test SMTP Gmail - Gửi email thử nghiệm
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_send_email(sender_email, sender_password, receiver_email):
    """
    Test gửi email từ Gmail SMTP
    
    Args:
        sender_email: Email người gửi (Gmail)
        sender_password: App Password (16 ký tự)
        receiver_email: Email người nhận
    """
    
    print(f"\n{'='*60}")
    print(f"🚀 TEST GỬI EMAIL")
    print(f"{'='*60}")
    print(f"Từ: {sender_email}")
    print(f"Đến: {receiver_email}")
    print(f"{'='*60}\n")
    
    try:
        # Tạo email
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "🎉 Test Email - OCR Tool System"
        
        # Nội dung HTML
        html = """
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .content {
            padding: 30px;
        }
        .success-box {
            background: #d4edda;
            border: 2px solid #28a745;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }
        .success-box h2 {
            color: #155724;
            margin: 0 0 10px 0;
        }
        .info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Test Email Thành Công!</h1>
        </div>
        
        <div class="content">
            <div class="success-box">
                <h2>✅ Hệ thống email hoạt động tốt!</h2>
                <p>SMTP Gmail đã được cấu hình thành công.</p>
            </div>
            
            <div class="info">
                <h3>📧 Thông tin gửi email:</h3>
                <p><strong>Từ:</strong> """ + sender_email + """</p>
                <p><strong>Đến:</strong> """ + receiver_email + """</p>
                <p><strong>Server:</strong> smtp.gmail.com:587</p>
                <p><strong>Bảo mật:</strong> TLS</p>
            </div>
            
            <p>Nếu bạn nhận được email này, có nghĩa là:</p>
            <ul>
                <li>✅ Tài khoản Gmail hoạt động bình thường</li>
                <li>✅ App Password được tạo đúng</li>
                <li>✅ SMTP connection thành công</li>
                <li>✅ Sẵn sàng gửi license key cho khách hàng</li>
            </ul>
            
            <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                <strong>Bước tiếp theo:</strong> Tích hợp vào hệ thống OCR Tool License
            </p>
        </div>
        
        <div class="footer">
            <p>OCR Tool License System</p>
            <p>Powered by Gmail SMTP</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach HTML
        msg.attach(MIMEText(html, 'html'))
        
        # Kết nối SMTP
        print("📡 Đang kết nối Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(0)  # Bật = 1 để xem chi tiết
        
        print("🔒 Đang bật TLS...")
        server.starttls()
        
        print("🔑 Đang đăng nhập...")
        server.login(sender_email, sender_password)
        
        print("📤 Đang gửi email...")
        server.send_message(msg)
        
        print("✅ Đóng kết nối...")
        server.quit()
        
        print(f"\n{'='*60}")
        print("🎉 THÀNH CÔNG! Email đã được gửi!")
        print(f"{'='*60}\n")
        print(f"✅ Check hộp thư: {receiver_email}")
        print(f"✅ Check cả Spam/Junk nếu không thấy")
        print(f"\n")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ LỖI ĐĂNG NHẬP!")
        print("─" * 60)
        print("Nguyên nhân có thể:")
        print("  1. App Password sai")
        print("  2. Chưa bật 2-Step Verification")
        print("  3. Email sai")
        print("\nGiải pháp:")
        print("  → Kiểm tra lại email và App Password")
        print("  → Tạo App Password mới")
        print("  → Đảm bảo đã bật 2-Step Verification")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ LỖI SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False


def test_multi_accounts():
    """
    Test tất cả 3 tài khoản
    """
    
    print("\n" + "="*60)
    print("📧 TEST SMTP CHO 3 TÀI KHOẢN GMAIL")
    print("="*60 + "\n")
    
    # Nhập thông tin tài khoản
    accounts = []
    
    print("Nhập thông tin 3 tài khoản Gmail:\n")
    
    for i in range(3):
        print(f"{'─'*60}")
        print(f"TÀI KHOẢN {i+1}:")
        print(f"{'─'*60}")
        
        email = input(f"Email {i+1}: ").strip()
        password = input(f"App Password {i+1} (16 ký tự): ").strip()
        
        # Xóa khoảng trắng trong App Password
        password = password.replace(" ", "")
        
        accounts.append({
            'email': email,
            'password': password
        })
        
        print()
    
    # Email nhận (test)
    print(f"{'─'*60}")
    receiver = input("Email nhận (để test, có thể là email chính của bạn): ").strip()
    print(f"{'─'*60}\n")
    
    # Test từng tài khoản
    results = []
    
    for i, account in enumerate(accounts, 1):
        print(f"\n{'='*60}")
        print(f"TEST TÀI KHOẢN {i}/{len(accounts)}")
        print(f"{'='*60}")
        
        success = test_send_email(
            sender_email=account['email'],
            sender_password=account['password'],
            receiver_email=receiver
        )
        
        results.append({
            'account': account['email'],
            'success': success
        })
        
        if i < len(accounts):
            input("\n⏸️  Nhấn Enter để test tài khoản tiếp theo...")
    
    # Tổng kết
    print("\n" + "="*60)
    print("📊 KẾT QUẢ TEST")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        status = "✅ Thành công" if result['success'] else "❌ Thất bại"
        print(f"{i}. {result['account']}: {status}")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'─'*60}")
    print(f"Tổng kết: {success_count}/{len(results)} tài khoản hoạt động")
    print(f"{'─'*60}\n")
    
    if success_count == len(results):
        print("🎉 HOÀN HẢO! Tất cả tài khoản đều hoạt động!")
        print("✅ Sẵn sàng tích hợp vào hệ thống OCR Tool")
    elif success_count > 0:
        print(f"⚠️  Có {len(results) - success_count} tài khoản lỗi")
        print("→ Kiểm tra lại tài khoản lỗi")
    else:
        print("❌ Tất cả tài khoản đều lỗi")
        print("→ Kiểm tra lại App Password và 2-Step Verification")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🧪 TEST SMTP GMAIL - OCR TOOL SYSTEM           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Chương trình này sẽ test gửi email từ 3 tài khoản Gmail.

Chuẩn bị:
  ✅ Đã tạo 3 tài khoản Gmail
  ✅ Đã bật 2-Step Verification (cả 3)
  ✅ Đã tạo App Password (cả 3)
  ✅ Đã lưu email và App Password

Lưu ý:
  • App Password là mã 16 ký tự (có hoặc không có khoảng trắng)
  • Ví dụ: abcd efgh ijkl mnop hoặc abcdefghijklmnop
  • Không phải mật khẩu Gmail thông thường!

""")
    
    input("Nhấn Enter để bắt đầu...")
    
    test_multi_accounts()
    
    print("\n✅ Hoàn tất! Check email để xem kết quả.")
    input("\nNhấn Enter để thoát...")

