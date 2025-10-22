"""
Email Sender Module
Tạm thời chỉ log ra console, không gửi email thật
"""

def send_license_email(to_email, license_key, customer_name, plan_type="", expiry_date=""):
    """
    Gửi email license key cho khách hàng
    Hiện tại chỉ log ra console
    
    Args:
        to_email: Email người nhận
        license_key: License key
        customer_name: Tên khách hàng
        plan_type: Loại gói (optional)
        expiry_date: Ngày hết hạn (optional)
    
    Returns:
        dict: {'success': True, 'message': '...'}
    """
    
    print("\n" + "="*60)
    print("📧 EMAIL LICENSE KEY")
    print("="*60)
    print(f"To: {to_email}")
    print(f"Customer: {customer_name}")
    print(f"License Key: {license_key}")
    if plan_type:
        print(f"Plan: {plan_type}")
    if expiry_date:
        print(f"Expires: {expiry_date}")
    print("="*60 + "\n")
    
    # Log thành công
    return {
        'success': True,
        'message': f'License key logged for {to_email}'
    }


# Nếu muốn enable email thật, uncomment code dưới:
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_license_email_real(to_email, license_key, customer_name, plan_type="", expiry_date=""):
    # Gmail SMTP Configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = os.getenv('EMAIL_USERNAME', 'your-email@gmail.com')
    SMTP_PASSWORD = os.getenv('EMAIL_APP_PASSWORD', 'your-app-password')
    FROM_EMAIL = SMTP_USERNAME
    
    try:
        # Tạo email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'License Key OCR Tool - {plan_type}'
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # HTML body
        html = f'''
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🎉 Cảm ơn bạn đã mua OCR Tool!</h2>
            <p>Xin chào <strong>{customer_name}</strong>,</p>
            <p>License key của bạn:</p>
            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin: 0; color: #0066cc;">{license_key}</h3>
            </div>
            <p><strong>Gói:</strong> {plan_type}</p>
            <p><strong>Hết hạn:</strong> {expiry_date}</p>
            <hr>
            <p><small>Email tự động từ OCR Tool System</small></p>
        </body>
        </html>
        '''
        
        msg.attach(MIMEText(html, 'html'))
        
        # Gửi email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return {'success': True, 'message': 'Email sent successfully'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
"""
