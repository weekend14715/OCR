#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Email Sender - OCR Tool License System
Gửi license key tự động sau khi thanh toán
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import json
import os
from pathlib import Path
from email_config import (
    EMAIL_ACCOUNTS, SMTP_SERVER, SMTP_PORT, SMTP_USE_TLS,
    DEFAULT_FROM_NAME, SUPPORT_EMAIL
)


class LicenseEmailSender:
    """
    Gửi license key qua email
    Tự động chuyển đổi giữa 2 tài khoản khi hết quota
    """
    
    def __init__(self, usage_file='email_usage.json'):
        """
        Khởi tạo email sender
        
        Args:
            usage_file: File lưu thông tin usage tracking
        """
        self.usage_file = usage_file
        self.accounts = EMAIL_ACCOUNTS
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.usage_data = self._load_usage()
    
    def _load_usage(self):
        """Load usage data từ file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Initialize usage data
        today = datetime.date.today().isoformat()
        return {
            'date': today,
            'accounts': {
                acc['email']: {
                    'sent_today': 0,
                    'last_reset': today
                }
                for acc in self.accounts
            }
        }
    
    def _save_usage(self):
        """Lưu usage data vào file"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save usage data: {e}")
    
    def _get_available_account(self):
        """
        Tìm tài khoản còn quota
        Tự động reset counter mỗi ngày
        
        Returns:
            dict: Account info or None
        """
        today = datetime.date.today().isoformat()
        
        # Reset nếu sang ngày mới
        if self.usage_data['date'] != today:
            self.usage_data['date'] = today
            for email in self.usage_data['accounts']:
                self.usage_data['accounts'][email] = {
                    'sent_today': 0,
                    'last_reset': today
                }
            self._save_usage()
        
        # Tìm account còn quota
        for account in self.accounts:
            email = account['email']
            usage = self.usage_data['accounts'].get(email, {})
            sent_today = usage.get('sent_today', 0)
            
            if sent_today < account['daily_limit']:
                return account
        
        return None
    
    def send_license_key(self, to_email, license_key, customer_name="Khách hàng", 
                        order_id=None, plan_type="lifetime"):
        """
        Gửi license key cho khách hàng
        
        Args:
            to_email: Email khách hàng
            license_key: License key
            customer_name: Tên khách hàng
            order_id: Mã đơn hàng (optional)
            plan_type: Loại gói (lifetime/yearly/monthly)
            
        Returns:
            dict: {'success': bool, 'message': str, 'account_used': str}
        """
        
        # Chọn account
        account = self._get_available_account()
        
        if not account:
            return {
                'success': False,
                'message': 'Hết quota! Đã gửi >1000 emails hôm nay.',
                'account_used': None
            }
        
        try:
            # Tạo email
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{DEFAULT_FROM_NAME} <{account['email']}>"
            msg['To'] = to_email
            msg['Subject'] = f"🎉 License Key OCR Tool - {license_key}"
            
            # Nội dung HTML
            html = self._create_email_html(
                license_key=license_key,
                customer_name=customer_name,
                order_id=order_id,
                plan_type=plan_type
            )
            
            msg.attach(MIMEText(html, 'html'))
            
            # Gửi email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(account['email'], account['password'])
            server.send_message(msg)
            server.quit()
            
            # Cập nhật counter
            email = account['email']
            self.usage_data['accounts'][email]['sent_today'] += 1
            self._save_usage()
            
            sent_today = self.usage_data['accounts'][email]['sent_today']
            remaining = account['daily_limit'] - sent_today
            
            return {
                'success': True,
                'message': f'Đã gửi email từ {account["email"]}',
                'account_used': account['email'],
                'emails_sent_today': sent_today,
                'emails_remaining': remaining
            }
            
        except smtplib.SMTPAuthenticationError as e:
            return {
                'success': False,
                'message': f'Lỗi xác thực: {str(e)}. Kiểm tra email/password.',
                'account_used': account['email']
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': f'Lỗi SMTP: {str(e)}',
                'account_used': account['email']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi: {str(e)}',
                'account_used': account['email']
            }
    
    def _create_email_html(self, license_key, customer_name, order_id=None, plan_type="lifetime"):
        """Tạo nội dung email HTML đẹp"""
        
        # Thông tin plan
        plan_names = {
            'lifetime': 'Vĩnh viễn',
            'yearly': '1 năm',
            'monthly': '1 tháng'
        }
        plan_name = plan_names.get(plan_type, 'Vĩnh viễn')
        
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
        .plan-badge {{
            display: inline-block;
            background: #ffc107;
            color: #000;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            margin-top: 10px;
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
                <div class="plan-badge">Gói {plan_name}</div>
            </div>
            
            <div class="info-box">
                <p><strong>⚠️ Lưu ý quan trọng:</strong></p>
                <p>• Hãy lưu lại license key này cẩn thận</p>
                <p>• Mỗi key chỉ kích hoạt được trên 1 máy tính</p>
                <p>• Key có hiệu lực: {plan_name}</p>
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
                <p><strong>Email:</strong> {SUPPORT_EMAIL}</p>
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
            dict: Thông tin usage
        """
        today = datetime.date.today().isoformat()
        
        # Reset nếu sang ngày mới
        if self.usage_data['date'] != today:
            self.usage_data['date'] = today
            for email in self.usage_data['accounts']:
                self.usage_data['accounts'][email] = {
                    'sent_today': 0,
                    'last_reset': today
                }
            self._save_usage()
        
        status = []
        total_sent = 0
        total_remaining = 0
        
        for account in self.accounts:
            email = account['email']
            usage = self.usage_data['accounts'].get(email, {})
            sent = usage.get('sent_today', 0)
            remaining = account['daily_limit'] - sent
            
            total_sent += sent
            total_remaining += remaining
            
            status.append({
                'email': email,
                'sent_today': sent,
                'remaining': remaining,
                'limit': account['daily_limit'],
                'percentage_used': (sent / account['daily_limit']) * 100
            })
        
        return {
            'date': today,
            'accounts': status,
            'total_sent': total_sent,
            'total_remaining': total_remaining,
            'total_limit': sum(acc['daily_limit'] for acc in self.accounts)
        }


# ============================================================================
# STANDALONE FUNCTIONS
# ============================================================================

# Global instance
_sender_instance = None

def get_sender():
    """Get singleton instance"""
    global _sender_instance
    if _sender_instance is None:
        _sender_instance = LicenseEmailSender()
    return _sender_instance


def send_license_email(to_email, license_key, customer_name="Khách hàng", 
                      order_id=None, plan_type="lifetime"):
    """
    Shortcut function để gửi license email
    
    Args:
        to_email: Email khách hàng
        license_key: License key
        customer_name: Tên khách hàng
        order_id: Mã đơn hàng
        plan_type: Loại gói
        
    Returns:
        dict: Kết quả gửi email
    """
    sender = get_sender()
    return sender.send_license_key(
        to_email=to_email,
        license_key=license_key,
        customer_name=customer_name,
        order_id=order_id,
        plan_type=plan_type
    )


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import sys
    
    sender = LicenseEmailSender()
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        📧 LICENSE EMAIL SENDER - OCR TOOL                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Chức năng:
  1. Gửi email test
  2. Xem trạng thái
  3. Thoát
""")
    
    while True:
        choice = input("\nChọn (1-3): ").strip()
        
        if choice == '1':
            print("\n" + "─"*60)
            to_email = input("Email nhận: ").strip()
            
            result = sender.send_license_key(
                to_email=to_email,
                license_key="TEST-1234-5678-ABCD",
                customer_name="Người dùng Test",
                order_id="TEST-ORDER-001",
                plan_type="lifetime"
            )
            
            print("\n" + "="*60)
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"📧 Đã gửi: {result['emails_sent_today']}")
                print(f"📧 Còn lại: {result['emails_remaining']}")
            else:
                print(f"❌ {result['message']}")
            print("="*60)
            
        elif choice == '2':
            status = sender.get_status()
            
            print("\n" + "="*60)
            print(f"📊 TRẠNG THÁI HỆ THỐNG EMAIL - {status['date']}")
            print("="*60)
            
            for i, acc in enumerate(status['accounts'], 1):
                bar_length = 20
                used_bar = "█" * int(acc['percentage_used'] / 5)
                empty_bar = "░" * (bar_length - len(used_bar))
                
                print(f"\nTÀI KHOẢN {i}: {acc['email']}")
                print(f"  [{used_bar}{empty_bar}] {acc['sent_today']}/{acc['limit']} emails")
                print(f"  Còn lại: {acc['remaining']} emails")
            
            print("\n" + "─"*60)
            print(f"TỔNG: {status['total_sent']}/{status['total_limit']} emails")
            print(f"CÒN LẠI: {status['total_remaining']} emails")
            print("="*60)
            
        elif choice == '3':
            print("\n👋 Tạm biệt!\n")
            break
            
        else:
            print("\n❌ Lựa chọn không hợp lệ!")

