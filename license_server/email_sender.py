#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Email Sender Module - OCR Tool License System
Gửi license keys qua Gmail với load balancing
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime, timedelta

# Try to load email config from environment variable or file
EMAIL_CONFIG_AVAILABLE = False
EMAIL_ACCOUNTS = []
SMTP_CONFIG = {}
SUPPORT_EMAIL = "support@ocrtool.com"

# Method 1: Load from Environment Variable (Production - Render)
email_accounts_env = os.getenv('EMAIL_ACCOUNTS')
if email_accounts_env:
    try:
        EMAIL_ACCOUNTS = json.loads(email_accounts_env)
        SMTP_CONFIG = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True
        }
        # Get support email from first account
        if EMAIL_ACCOUNTS:
            SUPPORT_EMAIL = EMAIL_ACCOUNTS[0]['email']
        EMAIL_CONFIG_AVAILABLE = True
        print(f"[OK] Email config loaded from environment variable ({len(EMAIL_ACCOUNTS)} accounts)")
    except Exception as e:
        print(f"[WARNING] Could not parse EMAIL_ACCOUNTS env var: {e}")

# Method 2: Fallback to email_config.py (Local development)
if not EMAIL_CONFIG_AVAILABLE:
    try:
        from email_config import get_email_accounts, get_smtp_config, SUPPORT_EMAIL as SUPPORT_EMAIL_FILE
        EMAIL_ACCOUNTS = get_email_accounts()
        SMTP_CONFIG = get_smtp_config()
        SUPPORT_EMAIL = SUPPORT_EMAIL_FILE
        EMAIL_CONFIG_AVAILABLE = True
        print(f"[OK] Email config loaded from email_config.py ({len(EMAIL_ACCOUNTS)} accounts)")
    except ImportError:
        print("[WARNING] No email config found (neither env var nor config file). Email functionality disabled.")


# Tracking file for usage
TRACK_FILE = 'email_usage.json'


def load_usage_stats():
    """Load email usage statistics"""
    if not os.path.exists(TRACK_FILE):
        return {}
    
    try:
        with open(TRACK_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_usage_stats(stats):
    """Save email usage statistics"""
    try:
        with open(TRACK_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save usage stats: {e}")


def get_available_account():
    """
    Chọn account có thể gửi email (round-robin với daily limit)
    
    Returns:
        dict: Account info hoặc None nếu tất cả đã đạt limit
    """
    if not EMAIL_CONFIG_AVAILABLE:
        return None
    
    accounts = EMAIL_ACCOUNTS
    usage_stats = load_usage_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Tìm account còn quota
    for account in accounts:
        email = account['email']
        daily_limit = account.get('daily_limit', 500)
        
        # Check usage today
        if email not in usage_stats:
            usage_stats[email] = {'date': today, 'count': 0}
        
        # Reset counter if new day
        if usage_stats[email]['date'] != today:
            usage_stats[email] = {'date': today, 'count': 0}
        
        # Check if under limit
        if usage_stats[email]['count'] < daily_limit:
            # Update count
            usage_stats[email]['count'] += 1
            save_usage_stats(usage_stats)
            return account
    
    return None


def send_license_email(to_email, license_key, customer_name, order_id="", plan_type=""):
    """
    Gửi email license key cho khách hàng
    Tự động chọn account Gmail khả dụng
    
    Args:
        to_email: Email người nhận
        license_key: License key
        customer_name: Tên khách hàng
        order_id: Mã đơn hàng (optional)
        plan_type: Loại gói (optional)
    
    Returns:
        dict: {'success': True/False, 'message': '...', 'account_used': '...'}
    """
    
    # Nếu không có email config, chỉ log
    if not EMAIL_CONFIG_AVAILABLE:
        print("\n" + "="*60)
        print("📧 EMAIL LICENSE KEY (LOG ONLY - NO CONFIG)")
        print("="*60)
        print(f"To: {to_email}")
        print(f"Customer: {customer_name}")
        print(f"License Key: {license_key}")
        if plan_type:
            print(f"Plan: {plan_type}")
        if order_id:
            print(f"Order: {order_id}")
        print("="*60 + "\n")
        
        return {
            'success': False,
            'message': 'Email config not available - logged only',
            'account_used': 'none'
        }
    
    # Chọn account
    account = get_available_account()
    
    if not account:
        print("❌ All email accounts reached daily limit!")
        return {
            'success': False,
            'message': 'All accounts reached daily limit',
            'account_used': 'none'
        }
    
    smtp_config = SMTP_CONFIG
    
    # Hiển thị thông tin plan
    plan_display = plan_type.upper() if plan_type else "LIFETIME"
    if plan_type == 'lifetime':
        expiry_display = "Không giới hạn (Trọn đời)"
    elif plan_type == 'yearly':
        expiry_display = "1 năm kể từ ngày kích hoạt"
    elif plan_type == 'monthly':
        expiry_display = "30 ngày kể từ ngày kích hoạt"
    else:
        expiry_display = "Xem trong phần mềm"
    
    try:
        # Tạo email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🎉 License Key OCR Tool - {plan_display}'
        msg['From'] = f"{account.get('display_name', 'OCR Tool')} <{account['email']}>"
        msg['To'] = to_email
        msg['Reply-To'] = SUPPORT_EMAIL
        
        # HTML body (đẹp hơn)
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎉 Chúc mừng!</h1>
                <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">Bạn đã nhận được License Key</p>
            </div>
            
            <div style="background: white; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
                
                <p style="font-size: 16px;">Xin chào <strong>{customer_name}</strong>,</p>
                
                <p>Cảm ơn bạn đã tin tưởng và sử dụng <strong>Vietnamese OCR Tool</strong>! 🚀</p>
                
                <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 25px 0; border-radius: 5px;">
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">License Key của bạn:</p>
                    <div style="background: white; padding: 15px; border-radius: 5px; text-align: center; border: 2px dashed #667eea;">
                        <code style="font-size: 20px; font-weight: bold; color: #667eea; letter-spacing: 2px;">{license_key}</code>
                    </div>
                </div>
                
                <div style="background: #f0f7ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #667eea; font-size: 16px;">📋 Thông tin gói:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 5px 0; color: #666;">Loại gói:</td>
                            <td style="padding: 5px 0; font-weight: bold; text-align: right;">{plan_display}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #666;">Thời hạn:</td>
                            <td style="padding: 5px 0; font-weight: bold; text-align: right;">{expiry_display}</td>
                        </tr>
                        {'<tr><td style="padding: 5px 0; color: #666;">Mã đơn:</td><td style="padding: 5px 0; font-weight: bold; text-align: right;">' + order_id + '</td></tr>' if order_id else ''}
                    </table>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin: 0 0 10px 0; color: #856404; font-size: 16px;">📝 Hướng dẫn kích hoạt:</h3>
                    <ol style="margin: 0; padding-left: 20px; color: #856404;">
                        <li>Mở phần mềm OCR Tool</li>
                        <li>Vào phần "License" hoặc "Kích hoạt"</li>
                        <li>Dán License Key vào ô nhập liệu</li>
                        <li>Click "Kích hoạt" và bắt đầu sử dụng!</li>
                    </ol>
                </div>
                
                <p style="margin-top: 25px;">Nếu bạn gặp bất kỳ vấn đề nào, đừng ngại liên hệ với chúng tôi qua email: <a href="mailto:{SUPPORT_EMAIL}" style="color: #667eea;">{SUPPORT_EMAIL}</a></p>
                
                <p style="margin-top: 20px;">Chúc bạn sử dụng phần mềm hiệu quả! 💪</p>
                
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 25px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                    Email tự động từ <strong>OCR Tool License System</strong><br>
                    © 2024 Vietnamese OCR Tool. All rights reserved.
                </p>
                
            </div>
            
        </body>
        </html>
        '''
        
        msg.attach(MIMEText(html, 'html'))
        
        # Gửi email qua SMTP
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            if smtp_config.get('use_tls', True):
                server.starttls()
            
            # Use 'app_password' field from environment variable or 'password' from config file
            password = account.get('app_password') or account.get('password')
            server.login(account['email'], password)
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email} via {account['email']}")
        
        return {
            'success': True,
            'message': f'Email sent successfully to {to_email}',
            'account_used': account['email']
        }
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return {
            'success': False,
            'message': str(e),
            'account_used': account['email'] if account else 'none'
        }


# Backward compatibility
def send_license_email_real(*args, **kwargs):
    """Alias for backward compatibility"""
    return send_license_email(*args, **kwargs)
