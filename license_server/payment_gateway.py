"""
Payment Gateway Integration for Vietnamese OCR Tool
Supports: VNPay, MoMo, ZaloPay, VietQR
Automatically generates license after successful payment
"""

import hashlib
import hmac
import urllib.parse
import requests
import json
from datetime import datetime
import secrets
import qrcode
import io
import base64
from PIL import Image

# ===================================
# VNPay Configuration
# ===================================
VNPAY_CONFIG = {
    'vnp_TmnCode': 'YOUR_VNPAY_TMN_CODE',  # Mã website tại VNPay
    'vnp_HashSecret': 'YOUR_VNPAY_HASH_SECRET',  # Secret key
    'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',  # Sandbox URL
    'vnp_ReturnUrl': 'http://yourdomain.com/payment/vnpay/callback',  # URL callback
}

# VNPay Production URL: https://pay.vnpay.vn/vpcpay.html

# ===================================
# MoMo Configuration
# ===================================
MOMO_CONFIG = {
    'partnerCode': 'YOUR_MOMO_PARTNER_CODE',
    'accessKey': 'YOUR_MOMO_ACCESS_KEY',
    'secretKey': 'YOUR_MOMO_SECRET_KEY',
    'endpoint': 'https://test-payment.momo.vn/v2/gateway/api/create',  # Test endpoint
    'returnUrl': 'http://yourdomain.com/payment/momo/callback',
    'notifyUrl': 'http://yourdomain.com/payment/momo/notify',
}

# MoMo Production: https://payment.momo.vn/v2/gateway/api/create

# ===================================
# ZaloPay Configuration
# ===================================
ZALOPAY_CONFIG = {
    'app_id': 'YOUR_ZALOPAY_APP_ID',
    'key1': 'YOUR_ZALOPAY_KEY1',
    'key2': 'YOUR_ZALOPAY_KEY2',
    'endpoint': 'https://sb-openapi.zalopay.vn/v2/create',  # Sandbox
    'callback_url': 'http://yourdomain.com/payment/zalopay/callback',
}

# ZaloPay Production: https://openapi.zalopay.vn/v2/create

# ===================================
# Pricing Plans (VNĐ)
# ===================================
PRICING = {
    'test': {
        'name': 'Test Plan (2,000đ)',
        'price': 2000,
        'duration_days': 1,  # 1 ngày để test
        'plan_type': 'test'
    },
    'monthly': {
        'name': 'Monthly Plan',
        'price': 99000,
        'duration_days': 30,
        'plan_type': 'monthly'
    },
    'yearly': {
        'name': 'Yearly Plan',
        'price': 799000,
        'duration_days': 365,
        'plan_type': 'yearly'
    },
    'lifetime': {
        'name': 'Lifetime Plan',
        'price': 1999000,
        'duration_days': 36500,  # 100 years
        'plan_type': 'lifetime'
    }
}


class VNPayPayment:
    """VNPay Payment Gateway Integration"""
    
    @staticmethod
    def create_payment_url(order_id, amount, order_info, customer_email):
        """
        Tạo URL thanh toán VNPay
        
        Args:
            order_id: Mã đơn hàng (unique)
            amount: Số tiền (VNĐ)
            order_info: Thông tin đơn hàng
            customer_email: Email khách hàng
            
        Returns:
            URL thanh toán
        """
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': VNPAY_CONFIG['vnp_TmnCode'],
            'vnp_Amount': str(int(amount * 100)),  # VNPay yêu cầu nhân 100
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': order_id,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': VNPAY_CONFIG['vnp_ReturnUrl'],
            'vnp_IpAddr': '127.0.0.1',
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }
        
        # Thêm email nếu có
        if customer_email:
            vnp_params['vnp_Bill_Email'] = customer_email
        
        # Sắp xếp params theo alphabet
        sorted_params = sorted(vnp_params.items())
        
        # Tạo query string
        query_string = '&'.join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
        
        # Tạo secure hash
        hash_data = '&'.join([f"{k}={v}" for k, v in sorted_params])
        secure_hash = hmac.new(
            VNPAY_CONFIG['vnp_HashSecret'].encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # URL cuối cùng
        payment_url = f"{VNPAY_CONFIG['vnp_Url']}?{query_string}&vnp_SecureHash={secure_hash}"
        
        return payment_url
    
    @staticmethod
    def verify_payment_response(params):
        """
        Xác thực response từ VNPay
        
        Args:
            params: Dictionary các params từ callback URL
            
        Returns:
            (is_valid, transaction_info)
        """
        vnp_secure_hash = params.pop('vnp_SecureHash', None)
        
        if not vnp_secure_hash:
            return False, None
        
        # Sắp xếp params
        sorted_params = sorted(params.items())
        hash_data = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Tính hash
        calculated_hash = hmac.new(
            VNPAY_CONFIG['vnp_HashSecret'].encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # So sánh hash
        is_valid = calculated_hash == vnp_secure_hash
        
        if is_valid and params.get('vnp_ResponseCode') == '00':
            transaction_info = {
                'order_id': params.get('vnp_TxnRef'),
                'amount': int(params.get('vnp_Amount', 0)) / 100,
                'bank_code': params.get('vnp_BankCode'),
                'transaction_no': params.get('vnp_TransactionNo'),
                'pay_date': params.get('vnp_PayDate'),
                'status': 'success'
            }
            return True, transaction_info
        
        return False, None


class MoMoPayment:
    """MoMo Payment Gateway Integration"""
    
    @staticmethod
    def create_payment(order_id, amount, order_info, customer_email):
        """
        Tạo giao dịch MoMo
        
        Returns:
            (success, payment_url or error_message)
        """
        request_id = f"{order_id}_{int(datetime.now().timestamp())}"
        
        # Tạo raw signature
        raw_signature = f"accessKey={MOMO_CONFIG['accessKey']}" \
                       f"&amount={amount}" \
                       f"&extraData=" \
                       f"&ipnUrl={MOMO_CONFIG['notifyUrl']}" \
                       f"&orderId={order_id}" \
                       f"&orderInfo={order_info}" \
                       f"&partnerCode={MOMO_CONFIG['partnerCode']}" \
                       f"&redirectUrl={MOMO_CONFIG['returnUrl']}" \
                       f"&requestId={request_id}" \
                       f"&requestType=captureWallet"
        
        # Tạo signature
        signature = hmac.new(
            MOMO_CONFIG['secretKey'].encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Request body
        payload = {
            'partnerCode': MOMO_CONFIG['partnerCode'],
            'accessKey': MOMO_CONFIG['accessKey'],
            'requestId': request_id,
            'amount': str(amount),
            'orderId': order_id,
            'orderInfo': order_info,
            'redirectUrl': MOMO_CONFIG['returnUrl'],
            'ipnUrl': MOMO_CONFIG['notifyUrl'],
            'extraData': '',
            'requestType': 'captureWallet',
            'signature': signature,
            'lang': 'vi'
        }
        
        try:
            response = requests.post(
                MOMO_CONFIG['endpoint'],
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if result.get('resultCode') == 0:
                return True, result.get('payUrl')
            else:
                return False, result.get('message', 'Unknown error')
                
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def verify_payment_response(params):
        """Xác thực response từ MoMo"""
        signature = params.get('signature')
        
        if not signature:
            return False, None
        
        # Tạo raw signature để verify
        raw_signature = f"accessKey={MOMO_CONFIG['accessKey']}" \
                       f"&amount={params.get('amount')}" \
                       f"&extraData={params.get('extraData', '')}" \
                       f"&message={params.get('message')}" \
                       f"&orderId={params.get('orderId')}" \
                       f"&orderInfo={params.get('orderInfo')}" \
                       f"&orderType={params.get('orderType')}" \
                       f"&partnerCode={params.get('partnerCode')}" \
                       f"&payType={params.get('payType')}" \
                       f"&requestId={params.get('requestId')}" \
                       f"&responseTime={params.get('responseTime')}" \
                       f"&resultCode={params.get('resultCode')}" \
                       f"&transId={params.get('transId')}"
        
        calculated_signature = hmac.new(
            MOMO_CONFIG['secretKey'].encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = calculated_signature == signature
        
        if is_valid and params.get('resultCode') == '0':
            transaction_info = {
                'order_id': params.get('orderId'),
                'amount': int(params.get('amount', 0)),
                'transaction_no': params.get('transId'),
                'pay_date': params.get('responseTime'),
                'status': 'success'
            }
            return True, transaction_info
        
        return False, None


class ZaloPayPayment:
    """ZaloPay Payment Gateway Integration"""
    
    @staticmethod
    def create_payment(order_id, amount, order_info, customer_email):
        """Tạo giao dịch ZaloPay"""
        trans_id = int(datetime.now().timestamp() * 1000)
        
        embed_data = json.dumps({
            'redirecturl': ZALOPAY_CONFIG['callback_url']
        })
        
        item = json.dumps([{
            'itemid': order_id,
            'itemname': order_info,
            'itemprice': amount,
            'itemquantity': 1
        }])
        
        # Tạo order data
        order = {
            'app_id': ZALOPAY_CONFIG['app_id'],
            'app_trans_id': f"{datetime.now().strftime('%y%m%d')}_{trans_id}",
            'app_user': customer_email or 'user_' + order_id,
            'app_time': int(datetime.now().timestamp() * 1000),
            'embed_data': embed_data,
            'item': item,
            'amount': amount,
            'description': order_info,
            'bank_code': '',
        }
        
        # Tạo MAC
        data = f"{order['app_id']}|{order['app_trans_id']}|{order['app_user']}|" \
               f"{order['amount']}|{order['app_time']}|{order['embed_data']}|{order['item']}"
        
        order['mac'] = hmac.new(
            ZALOPAY_CONFIG['key1'].encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        try:
            response = requests.post(ZALOPAY_CONFIG['endpoint'], data=order)
            result = response.json()
            
            if result.get('return_code') == 1:
                return True, result.get('order_url')
            else:
                return False, result.get('return_message', 'Unknown error')
                
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def verify_callback(callback_data):
        """Xác thực callback từ ZaloPay"""
        try:
            data_str = callback_data.get('data')
            received_mac = callback_data.get('mac')
            
            # Tính MAC
            calculated_mac = hmac.new(
                ZALOPAY_CONFIG['key2'].encode('utf-8'),
                data_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if calculated_mac != received_mac:
                return False, None
            
            # Parse data
            data = json.loads(data_str)
            
            if data.get('status') == 1:  # Success
                transaction_info = {
                    'order_id': data.get('app_trans_id'),
                    'amount': data.get('amount'),
                    'transaction_no': data.get('zp_trans_id'),
                    'status': 'success'
                }
                return True, transaction_info
            
            return False, None
            
        except Exception as e:
            print(f"ZaloPay verify error: {e}")
            return False, None


class VietQRPayment:
    """
    VietQR Payment Integration
    Tạo mã QR thanh toán ngân hàng theo chuẩn VietQR
    """
    
    @staticmethod
    def generate_vietqr_url(bank_code, account_number, account_name, amount, description):
        """
        Tạo VietQR URL theo chuẩn của Napas
        
        Args:
            bank_code: Mã ngân hàng (VD: "MB", "VCB", "TCB")
            account_number: Số tài khoản
            account_name: Tên chủ tài khoản
            amount: Số tiền (VNĐ)
            description: Nội dung chuyển khoản
            
        Returns:
            VietQR URL
        """
        # VietQR format: https://img.vietqr.io/image/{BANK_CODE}-{ACCOUNT_NUMBER}-{TEMPLATE}.jpg?amount={AMOUNT}&addInfo={DESCRIPTION}&accountName={ACCOUNT_NAME}
        
        base_url = "https://img.vietqr.io/image"
        template = "compact2"  # compact2, print, qr_only
        
        # URL encode description và account name
        description_encoded = urllib.parse.quote(description)
        account_name_encoded = urllib.parse.quote(account_name)
        
        vietqr_url = f"{base_url}/{bank_code}-{account_number}-{template}.jpg?" \
                     f"amount={amount}&" \
                     f"addInfo={description_encoded}&" \
                     f"accountName={account_name_encoded}"
        
        return vietqr_url
    
    @staticmethod
    def generate_qr_code_base64(bank_code, account_number, account_name, amount, description):
        """
        Tạo QR code dưới dạng base64 image
        
        Returns:
            Base64 encoded PNG image
        """
        vietqr_url = VietQRPayment.generate_vietqr_url(
            bank_code, account_number, account_name, amount, description
        )
        
        # Tạo QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vietqr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def get_bank_info():
        """
        Lấy thông tin ngân hàng từ environment variables
        Fallback về giá trị mặc định nếu không có
        """
        import os
        return {
            'bank_code': os.getenv('BANK_CODE', 'MB'),
            'bank_name': os.getenv('BANK_NAME', 'MB Bank (Ngân hàng Quân Đội)'),
            'account_number': os.getenv('BANK_ACCOUNT_NUMBER', '0123456789'),
            'account_name': os.getenv('BANK_ACCOUNT_NAME', 'NGUYEN VAN A'),
        }


def generate_order_id():
    """Tạo order ID unique"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = secrets.token_hex(4).upper()
    return f"ORD{timestamp}{random_str}"


def get_plan_info(plan_type):
    """Lấy thông tin gói"""
    return PRICING.get(plan_type.lower())


# ===================================
# Example Usage
# ===================================
if __name__ == '__main__':
    # Test generate payment URL
    order_id = generate_order_id()
    plan = get_plan_info('lifetime')
    
    print("=== VNPay Payment URL ===")
    vnpay_url = VNPayPayment.create_payment_url(
        order_id=order_id,
        amount=plan['price'],
        order_info=f"Mua license {plan['name']}",
        customer_email='customer@example.com'
    )
    print(vnpay_url)
    
    print("\n=== MoMo Payment ===")
    success, momo_result = MoMoPayment.create_payment(
        order_id=order_id,
        amount=plan['price'],
        order_info=f"Mua license {plan['name']}",
        customer_email='customer@example.com'
    )
    print(f"Success: {success}")
    print(f"Result: {momo_result}")
    
    print("\n=== Order ID Generated ===")
    print(f"Order ID: {order_id}")

