"""
Configuration loader for License Server
Loads config from environment variables (for production) or local files (for development)
"""

import os
import json

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

def get_email_config():
    """
    Load email configuration from environment variables or local file
    
    Priority:
    1. Environment variables (for production on Render.com)
    2. Local email_config.py file (for development)
    """
    
    # Try loading from environment variables first (Production)
    if os.getenv('EMAIL_ACCOUNT_1') and os.getenv('EMAIL_PASSWORD_1'):
        accounts = []
        
        # Account 1
        if os.getenv('EMAIL_ACCOUNT_1') and os.getenv('EMAIL_PASSWORD_1'):
            accounts.append({
                'email': os.getenv('EMAIL_ACCOUNT_1'),
                'password': os.getenv('EMAIL_PASSWORD_1'),
                'daily_limit': int(os.getenv('EMAIL_LIMIT_1', '500'))
            })
        
        # Account 2
        if os.getenv('EMAIL_ACCOUNT_2') and os.getenv('EMAIL_PASSWORD_2'):
            accounts.append({
                'email': os.getenv('EMAIL_ACCOUNT_2'),
                'password': os.getenv('EMAIL_PASSWORD_2'),
                'daily_limit': int(os.getenv('EMAIL_LIMIT_2', '500'))
            })
        
        return {
            'EMAIL_ACCOUNTS': accounts,
            'EMAIL_FROM_NAME': os.getenv('EMAIL_FROM_NAME', 'OCR Tool'),
            'EMAIL_SUPPORT': os.getenv('EMAIL_SUPPORT', 'support@ocrtool.com')
        }
    
    # Fallback to local config file (Development)
    try:
        from email_config import EMAIL_ACCOUNTS, EMAIL_FROM_NAME, EMAIL_SUPPORT
        return {
            'EMAIL_ACCOUNTS': EMAIL_ACCOUNTS,
            'EMAIL_FROM_NAME': EMAIL_FROM_NAME,
            'EMAIL_SUPPORT': EMAIL_SUPPORT
        }
    except ImportError:
        print("⚠️  Warning: No email configuration found!")
        return {
            'EMAIL_ACCOUNTS': [],
            'EMAIL_FROM_NAME': 'OCR Tool',
            'EMAIL_SUPPORT': 'support@ocrtool.com'
        }


# ==============================================================================
# PAYMENT GATEWAY CONFIGURATION
# ==============================================================================

def get_payment_config():
    """
    Load payment gateway configuration from environment variables or return defaults
    """
    
    return {
        # VNPay
        'VNPAY_TMN_CODE': os.getenv('VNPAY_TMN_CODE', ''),
        'VNPAY_HASH_SECRET': os.getenv('VNPAY_HASH_SECRET', ''),
        'VNPAY_URL': os.getenv('VNPAY_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'),
        
        # MoMo
        'MOMO_PARTNER_CODE': os.getenv('MOMO_PARTNER_CODE', ''),
        'MOMO_ACCESS_KEY': os.getenv('MOMO_ACCESS_KEY', ''),
        'MOMO_SECRET_KEY': os.getenv('MOMO_SECRET_KEY', ''),
        'MOMO_ENDPOINT': os.getenv('MOMO_ENDPOINT', 'https://test-payment.momo.vn/v2/gateway/api/create'),
        
        # ZaloPay
        'ZALOPAY_APP_ID': os.getenv('ZALOPAY_APP_ID', ''),
        'ZALOPAY_KEY1': os.getenv('ZALOPAY_KEY1', ''),
        'ZALOPAY_KEY2': os.getenv('ZALOPAY_KEY2', ''),
        'ZALOPAY_ENDPOINT': os.getenv('ZALOPAY_ENDPOINT', 'https://sb-openapi.zalopay.vn/v2/create'),
    }


# ==============================================================================
# GENERAL CONFIGURATION
# ==============================================================================

def get_app_config():
    """
    Load general app configuration
    """
    
    return {
        'ADMIN_API_KEY': os.getenv('ADMIN_API_KEY', 'your-secure-admin-api-key-here-change-this'),
        'DATABASE': os.getenv('DATABASE_PATH', 'licenses.db'),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'development'),
        'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
        'PORT': int(os.getenv('PORT', '5000')),
        'HOST': os.getenv('HOST', '0.0.0.0'),
    }


# ==============================================================================
# LOAD ALL CONFIGS
# ==============================================================================

EMAIL_CONFIG = get_email_config()
PAYMENT_CONFIG = get_payment_config()
APP_CONFIG = get_app_config()

# Export individual configs for easy import
EMAIL_ACCOUNTS = EMAIL_CONFIG.get('EMAIL_ACCOUNTS', [])
EMAIL_FROM_NAME = EMAIL_CONFIG.get('EMAIL_FROM_NAME', 'OCR Tool')
EMAIL_SUPPORT = EMAIL_CONFIG.get('EMAIL_SUPPORT', 'support@ocrtool.com')

