"""
Casso Payment Integration
Tích hợp thanh toán qua Casso.vn
"""

import requests
import hmac
import hashlib
import json
from datetime import datetime

class CassoPayment:
    """
    Casso Payment Gateway
    """
    
    def __init__(self, api_key, business_id, checksum_key):
        self.api_key = api_key
        self.business_id = business_id
        self.checksum_key = checksum_key
        self.base_url = "https://oauth.casso.vn/v2"
    
    def get_transactions(self, from_date=None, to_date=None):
        """
        Lấy danh sách giao dịch
        
        Args:
            from_date: Từ ngày (YYYY-MM-DD)
            to_date: Đến ngày (YYYY-MM-DD)
        
        Returns:
            dict: Response từ Casso API
        """
        url = f"{self.base_url}/transactions"
        
        headers = {
            "Authorization": f"Apikey {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = {}
        if from_date:
            params['fromDate'] = from_date
        if to_date:
            params['toDate'] = to_date
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting transactions: {e}")
            return None
    
    def verify_webhook_signature(self, webhook_data, signature):
        """
        Xác thực webhook signature từ Casso
        
        Args:
            webhook_data: Dữ liệu webhook (dict)
            signature: Signature từ header
        
        Returns:
            bool: True nếu signature hợp lệ
        """
        # Sắp xếp keys và tạo string để hash
        sorted_data = sorted(webhook_data.items())
        data_string = '&'.join([f"{k}={v}" for k, v in sorted_data])
        
        # Tạo HMAC SHA256
        expected_signature = hmac.new(
            self.checksum_key.encode('utf-8'),
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def parse_transaction_note(self, note):
        """
        Parse ghi chú chuyển khoản để lấy email
        
        Format: email@example.com hoặc EMAIL email@example.com
        
        Args:
            note: Ghi chú chuyển khoản
        
        Returns:
            str: Email hoặc None
        """
        if not note:
            return None
        
        note = note.strip().lower()
        
        # Tìm email trong note
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, note)
        
        if match:
            return match.group(0)
        
        return None
    
    def get_bank_info(self):
        """
        Lấy thông tin tài khoản ngân hàng
        
        Returns:
            dict: Thông tin bank
        """
        url = f"{self.base_url}/userInfo"
        
        headers = {
            "Authorization": f"Apikey {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting bank info: {e}")
            return None


def create_payment_instruction(amount, order_id):
    """
    Tạo hướng dẫn thanh toán
    
    Args:
        amount: Số tiền
        order_id: Mã đơn hàng
    
    Returns:
        dict: Thông tin hướng dẫn thanh toán
    """
    # Thông tin tài khoản (sẽ cập nhật sau khi có bank info)
    instruction = {
        'bank_name': 'MB Bank',
        'account_number': 'XXXXXXXXXX',  # Sẽ lấy từ Casso API
        'account_name': 'NGUYEN VAN A',
        'amount': amount,
        'content': f"{order_id}",
        'note': 'Vui lòng chuyển khoản đúng nội dung để tự động kích hoạt'
    }
    
    return instruction

