"""
PayOS Payment Handler
Xử lý tạo QR code động và webhook từ PayOS
"""

import os
import hashlib
import hmac
from payos import PayOS
from datetime import datetime

# Khởi tạo PayOS client
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', '')
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', '')
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', '')

# PayOS client instance
payos_client = None

def init_payos():
    """Khởi tạo PayOS client"""
    global payos_client
    
    if not PAYOS_CLIENT_ID or not PAYOS_API_KEY or not PAYOS_CHECKSUM_KEY:
        print("⚠️  Warning: PayOS credentials not configured")
        return False
    
    try:
        payos_client = PayOS(
            client_id=PAYOS_CLIENT_ID,
            api_key=PAYOS_API_KEY,
            checksum_key=PAYOS_CHECKSUM_KEY
        )
        print("✅ PayOS đã được kích hoạt!")
        return True
    except Exception as e:
        print(f"❌ Lỗi khởi tạo PayOS: {e}")
        return False


def create_payment_link(order_id, amount, description, customer_email="", return_url="", cancel_url=""):
    """
    Tạo link thanh toán PayOS với QR code
    
    Args:
        order_id: Mã đơn hàng (unique)
        amount: Số tiền (VND)
        description: Mô tả giao dịch
        customer_email: Email khách hàng (optional)
        return_url: URL trả về khi thành công
        cancel_url: URL khi hủy
    
    Returns:
        dict: {
            'success': True/False,
            'checkout_url': 'https://...',  # URL thanh toán
            'qr_code': 'https://...',       # URL QR code
            'order_id': '...',
            'amount': ...,
            'error': '...'  # Nếu có lỗi
        }
    """
    
    if not payos_client:
        return {
            'success': False,
            'error': 'PayOS not initialized'
        }
    
    try:
        # Tạo payment data
        payment_data = {
            "orderCode": int(order_id),  # PayOS yêu cầu orderCode là số nguyên
            "amount": int(amount),
            "description": description,
            "returnUrl": return_url or f"https://your-app.com/payment/success",
            "cancelUrl": cancel_url or f"https://your-app.com/payment/cancel"
        }
        
        # Tạo payment link
        response = payos_client.createPaymentLink(payment_data)
        
        if response:
            return {
                'success': True,
                'checkout_url': response.checkoutUrl,
                'qr_code': response.qrCode,
                'order_id': order_id,
                'amount': amount,
                'payment_link_id': response.paymentLinkId
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create payment link'
            }
            
    except Exception as e:
        print(f"❌ Lỗi tạo payment link: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def verify_webhook_signature(webhook_data, signature):
    """
    Xác thực chữ ký webhook từ PayOS
    
    Args:
        webhook_data: Dữ liệu webhook (dict)
        signature: Chữ ký từ header
    
    Returns:
        bool: True nếu hợp lệ
    """
    try:
        # Tạo string để sign (theo docs PayOS)
        # Format: amount|description|orderCode|...
        data_str = f"{webhook_data.get('amount')}|{webhook_data.get('description')}|{webhook_data.get('orderCode')}"
        
        # Tính HMAC SHA256
        expected_signature = hmac.new(
            PAYOS_CHECKSUM_KEY.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
        
    except Exception as e:
        print(f"❌ Lỗi xác thực signature: {e}")
        return False


def get_payment_info(order_id):
    """
    Lấy thông tin thanh toán từ PayOS
    
    Args:
        order_id: Mã đơn hàng
    
    Returns:
        dict: Thông tin thanh toán
    """
    if not payos_client:
        return None
    
    try:
        response = payos_client.getPaymentLinkInformation(int(order_id))
        return response
    except Exception as e:
        print(f"❌ Lỗi lấy thông tin thanh toán: {e}")
        return None


def cancel_payment(order_id, reason=""):
    """
    Hủy thanh toán
    
    Args:
        order_id: Mã đơn hàng
        reason: Lý do hủy
    
    Returns:
        bool: True nếu thành công
    """
    if not payos_client:
        return False
    
    try:
        response = payos_client.cancelPaymentLink(int(order_id), reason)
        return True
    except Exception as e:
        print(f"❌ Lỗi hủy thanh toán: {e}")
        return False


# Khởi tạo khi import module
PAYOS_ENABLED = init_payos()

