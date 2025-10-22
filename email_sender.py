#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-Account Gmail SMTP Sender
Hệ thống gửi email tự động với 3 tài khoản Gmail (1500 emails/ngày)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import json
import os
from pathlib import Path

class MultiAccountEmailSender:
    """
    Quản lý gửi email qua nhiều tài khoản Gmail
    Tự động chuyển đổi khi hết quota
    """
    
    def __init__(self, config_file='email_config.json'):
        """
        Khởi tạo với file config
        
        Args:
            config_file: Đường dẫn đến file config JSON
        """
        self.config_file = config_file
        self.accounts = []
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Load hoặc tạo config
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load config từ file hoặc tạo mới"""
        
        if os.path.exists(self.config_file):
            # Load từ file
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.accounts = data.get('accounts', [])
            print(f"✅ Đã load {len(self.accounts)} tài khoản từ {self.config_file}")
        else:
            # Tạo mới
            print(f"⚠️  Chưa có file {self.config_file}")
            print("→ Chạy setup_email_accounts() để cấu hình")
    
    def save_config(self):
        """Lưu config vào file"""
        
        data = {
            'accounts': self.accounts,
            'last_updated': datetime.datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Đã lưu config vào {self.config_file}")
    
    def setup_accounts(self):
        """
        Setup 3 tài khoản Gmail (interactive)
        """
        
        print("\n" + "="*60)
        print("⚙️  SETUP TÀI KHOẢN GMAIL")
        print("="*60 + "\n")
        
        print("Nhập thông tin 3 tài khoản Gmail đã tạo:\n")
        
        accounts = []
        
        for i in range(3):
            print(f"{'─'*60}")
            print(f"TÀI KHOẢN {i+1}:")
            print(f"{'─'*60}")
            
            email = input(f"Email {i+1}: ").strip()
            password = input(f"App Password {i+1}: ").strip()
            
            # Xóa khoảng trắng
            password = password.replace(" ", "")
            
            accounts.append({
                'email': email,
                'password': password,
                'daily_limit': 500,
                'sent_today': 0,
                'last_reset': datetime.date.today().isoformat()
            })
            
            print(f"✅ Đã thêm {email}\n")
        
        self.accounts = accounts
        self.save_config()
        
        print("\n" + "="*60)
        print("🎉 Setup hoàn tất!")
        print("="*60 + "\n")
        
        # Hỏi test
        test = input("Bạn có muốn test gửi email không? (y/n): ").strip().lower()
        if test == 'y':
            receiver = input("Email nhận: ").strip()
            print()
            for i, account in enumerate(self.accounts, 1):
                print(f"\nTest tài khoản {i}...")
                self.send_license_key(
                    to_email=receiver,
                    license_key="TEST-1234-5678-ABCD",
                    customer_name="Test User",
                    force_account_index=i-1
                )
    
    def _get_available_account(self):
        """
        Tìm tài khoản còn quota
        Tự động reset counter mỗi ngày
        """
        
        today = datetime.date.today().isoformat()
        
        for account in self.accounts:
            # Reset nếu sang ngày mới
            if account['last_reset'] != today:
                account['sent_today'] = 0
                account['last_reset'] = today
                self.save_config()  # Lưu lại
            
            # Tìm account còn quota
            if account['sent_today'] < account['daily_limit']:
                return account
        
        return None
    
    def send_license_key(self, to_email, license_key, customer_name="Khách hàng", 
                        order_id=None, force_account_index=None):
        """
        Gửi license key cho khách hàng
        
        Args:
            to_email: Email khách hàng
            license_key: License key
            customer_name: Tên khách hàng
            order_id: Mã đơn hàng (optional)
            force_account_index: Force dùng account cụ thể (test only)
            
        Returns:
            dict: {'success': bool, 'message': str, 'account_used': str}
        """
        
        # Chọn account
        if force_account_index is not None:
            account = self.accounts[force_account_index]
        else:
            account = self._get_available_account()
        
        if not account:
            return {
                'success': False,
                'message': 'Hết quota! Đã gửi >1500 emails hôm nay.',
                'account_used': None
            }
        
        try:
            # Tạo email
            msg = MIMEMultipart('alternative')
            msg['From'] = f"OCR Tool <{account['email']}>"
            msg['To'] = to_email
            msg['Subject'] = f"🎉 License Key OCR Tool - {license_key}"
            
            # Nội dung HTML
            html = self._create_email_html(
                license_key=license_key,
                customer_name=customer_name,
                order_id=order_id
            )
            
            msg.attach(MIMEText(html, 'html'))
            
            # Gửi email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(account['email'], account['password'])
            server.send_message(msg)
            server.quit()
            
            # Cập nhật counter
            account['sent_today'] += 1
            self.save_config()
            
            return {
                'success': True,
                'message': f'Đã gửi email từ {account["email"]}',
                'account_used': account['email'],
                'emails_sent_today': account['sent_today'],
                'emails_remaining': account['daily_limit'] - account['sent_today']
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi: {str(e)}',
                'account_used': account['email']
            }
    
    def _create_email_html(self, license_key, customer_name, order_id=None):
        """Tạo nội dung email HTML"""
        
        order_info = ""
        if order_id:
            order_info = f"<p><strong>Mã đơn hàng:</strong> {order_id}</p>"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .key-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: 3px dashed #667eea;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}
        .key-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .key {{
            font-size: 26px;
            font-weight: bold;
            color: #667eea;
            font-family: 'Courier New', Consolas, monospace;
            letter-spacing: 3px;
            word-break: break-all;
            user-select: all;
        }}
        .steps {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }}
        .steps h3 {{
            margin: 0 0 20px 0;
            color: #333;
            font-size: 18px;
        }}
        .step {{
            padding: 15px 0;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
        }}
        .step:last-child {{
            border-bottom: none;
        }}
        .step-number {{
            background: #667eea;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        .step-text {{
            color: #555;
            flex: 1;
        }}
        .info-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .info-box p {{
            margin: 5px 0;
            color: #856404;
        }}
        .support {{
            background: #e7f3ff;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
            text-align: center;
        }}
        .support h4 {{
            margin: 0 0 10px 0;
            color: #0066cc;
        }}
        .support p {{
            margin: 5px 0;
            color: #555;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 30px;
        }}
        .footer p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .footer .social {{
            margin-top: 15px;
        }}
        .footer .social a {{
            color: white;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">🎉</div>
            <h1>Cảm ơn bạn đã mua OCR Tool!</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                <p>Xin chào <strong>{customer_name}</strong>,</p>
            </div>
            
            <p>Cảm ơn bạn đã tin tưởng và mua <strong>Vietnamese OCR Tool</strong>. License key của bạn đã sẵn sàng!</p>
            
            {order_info}
            
            <div class="key-box">
                <div class="key-label">License Key của bạn</div>
                <div class="key">{license_key}</div>
            </div>
            
            <div class="info-box">
                <p><strong>⚠️ Lưu ý quan trọng:</strong></p>
                <p>• Hãy lưu lại license key này cẩn thận</p>
                <p>• Mỗi key chỉ kích hoạt được trên 1 máy tính</p>
                <p>• Key có hiệu lực vĩnh viễn</p>
            </div>
            
            <div class="steps">
                <h3>📋 Hướng dẫn kích hoạt</h3>
                
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-text">Mở phần mềm <strong>OCR Tool</strong></div>
                </div>
                
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-text">Click nút <strong>"Kích hoạt bản quyền"</strong></div>
                </div>
                
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-text">Copy và paste <strong>license key</strong> ở trên</div>
                </div>
                
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-text">Click <strong>"Kích hoạt"</strong></div>
                </div>
                
                <div class="step">
                    <div class="step-number">5</div>
                    <div class="step-text">Hoàn tất! Bạn đã có thể sử dụng đầy đủ tính năng 🎉</div>
                </div>
            </div>
            
            <div class="support">
                <h4>💬 Cần hỗ trợ?</h4>
                <p>Nếu gặp vấn đề khi kích hoạt, vui lòng liên hệ:</p>
                <p><strong>Email:</strong> hoangtuan.th484@gmail.com</p>
                <p>Chúng tôi sẽ phản hồi trong vòng 24 giờ!</p>
            </div>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                Chúc bạn sử dụng phần mềm hiệu quả!<br>
                <strong>Team OCR Tool</strong>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Vietnamese OCR Tool</strong></p>
            <p>Công cụ OCR tiếng Việt chuyên nghiệp</p>
            <p style="margin-top: 15px; font-size: 12px;">
                Email này được gửi tự động, vui lòng không reply.
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def get_status(self):
        """
        Lấy trạng thái các tài khoản
        
        Returns:
            dict: Thông tin trạng thái
        """
        
        today = datetime.date.today().isoformat()
        total_sent = 0
        total_remaining = 0
        
        status = []
        
        for i, account in enumerate(self.accounts, 1):
            # Reset nếu cần
            if account['last_reset'] != today:
                account['sent_today'] = 0
                account['last_reset'] = today
            
            sent = account['sent_today']
            remaining = account['daily_limit'] - sent
            
            total_sent += sent
            total_remaining += remaining
            
            status.append({
                'account_number': i,
                'email': account['email'],
                'sent_today': sent,
                'remaining': remaining,
                'limit': account['daily_limit'],
                'percentage_used': (sent / account['daily_limit']) * 100
            })
        
        return {
            'accounts': status,
            'total_sent_today': total_sent,
            'total_remaining': total_remaining,
            'total_limit': len(self.accounts) * 500,
            'date': today
        }
    
    def print_status(self):
        """In ra trạng thái các tài khoản"""
        
        status = self.get_status()
        
        print("\n" + "="*70)
        print(f"📊 TRẠNG THÁI HỆ THỐNG EMAIL - {status['date']}")
        print("="*70 + "\n")
        
        for acc in status['accounts']:
            used_bar = "█" * int(acc['percentage_used'] / 5)
            empty_bar = "░" * (20 - len(used_bar))
            
            print(f"TÀI KHOẢN {acc['account_number']}: {acc['email']}")
            print(f"  [{used_bar}{empty_bar}] {acc['sent_today']}/{acc['limit']} emails")
            print(f"  Còn lại: {acc['remaining']} emails\n")
        
        print("─"*70)
        print(f"TỔNG: {status['total_sent_today']}/{status['total_limit']} emails")
        print(f"CÒN LẠI: {status['total_remaining']} emails")
        print("="*70 + "\n")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """CLI để quản lý email sender"""
    
    import sys
    
    sender = MultiAccountEmailSender()
    
    if len(sys.argv) == 1:
        # Interactive mode
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        📧 MULTI-ACCOUNT GMAIL SMTP SENDER                    ║
║        OCR Tool License System                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Chức năng:
  1. Setup tài khoản
  2. Gửi email test
  3. Xem trạng thái
  4. Thoát

""")
        
        while True:
            choice = input("Chọn (1-4): ").strip()
            
            if choice == '1':
                sender.setup_accounts()
                
            elif choice == '2':
                if not sender.accounts:
                    print("\n❌ Chưa setup tài khoản! Chọn 1 để setup.\n")
                    continue
                
                to_email = input("\nEmail nhận: ").strip()
                result = sender.send_license_key(
                    to_email=to_email,
                    license_key="TEST-1234-5678-ABCD",
                    customer_name="Test User"
                )
                
                if result['success']:
                    print(f"\n✅ {result['message']}")
                    print(f"📧 Đã gửi: {result['emails_sent_today']}")
                    print(f"📧 Còn lại: {result['emails_remaining']}\n")
                else:
                    print(f"\n❌ {result['message']}\n")
                
            elif choice == '3':
                if not sender.accounts:
                    print("\n❌ Chưa setup tài khoản!\n")
                    continue
                sender.print_status()
                
            elif choice == '4':
                print("\n👋 Tạm biệt!\n")
                break
                
            else:
                print("\n❌ Lựa chọn không hợp lệ!\n")


if __name__ == "__main__":
    main()

