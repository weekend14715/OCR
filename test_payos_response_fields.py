#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PayOS Response Structure
Kiểm tra xem PayOS trả về những field gì
"""

import os
import sys
import datetime
from payos import PayOS
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Initialize PayOS
CLIENT_ID = os.getenv("PAYOS_CLIENT_ID")
API_KEY = os.getenv("PAYOS_API_KEY")
CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY")

if not all([CLIENT_ID, API_KEY, CHECKSUM_KEY]):
    print("❌ Missing PayOS credentials!")
    print(f"CLIENT_ID: {CLIENT_ID[:10]}..." if CLIENT_ID else "NOT SET")
    print(f"API_KEY: {API_KEY[:10]}..." if API_KEY else "NOT SET")
    print(f"CHECKSUM_KEY: {CHECKSUM_KEY[:10]}..." if CHECKSUM_KEY else "NOT SET")
    exit(1)

payos = PayOS(
    client_id=CLIENT_ID,
    api_key=API_KEY,
    checksum_key=CHECKSUM_KEY
)

# Create test payment
order_code = int(datetime.datetime.now().timestamp())

payment_data = {
    "orderCode": order_code,
    "amount": 2000,
    "description": "Test QR Response",
    "returnUrl": "https://ocr-uufr.onrender.com/payment/success",
    "cancelUrl": "https://ocr-uufr.onrender.com/payment/cancel"
}

print("\n" + "="*80)
print("🧪 TESTING PAYOS RESPONSE STRUCTURE")
print("="*80 + "\n")

print(f"📝 Order Code: {order_code}")
print(f"💰 Amount: 2,000 VND")
print()

try:
    print("⏳ Calling payos.payment_requests.create()...")
    response = payos.payment_requests.create(payment_data)
    print("✅ Response received!\n")
    
    # Check response type
    print(f"Response Type: {type(response)}")
    print(f"Response Class: {response.__class__.__name__}\n")
    
    # List ALL attributes
    print("="*80)
    print("📋 ALL RESPONSE ATTRIBUTES:")
    print("="*80)
    
    all_attrs = [attr for attr in dir(response) if not attr.startswith('_')]
    for i, attr in enumerate(all_attrs, 1):
        try:
            value = getattr(response, attr)
            # Only show non-callable attributes
            if not callable(value):
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"{i:2}. {attr:20} = {value_str}")
        except:
            pass
    
    print("\n" + "="*80)
    print("🔍 CHECKING FOR QR CODE FIELDS:")
    print("="*80 + "\n")
    
    # Check various QR field names
    qr_fields = [
        'qrCode', 'qr_code', 'qrCodeUrl', 'qr_code_url',
        'QRCode', 'QR_CODE', 'qrDataURL', 'qrImage',
        'qr', 'QR', 'qrData', 'qr_data'
    ]
    
    found_qr = False
    for field in qr_fields:
        if hasattr(response, field):
            value = getattr(response, field)
            if value:
                print(f"✅ FOUND: {field}")
                print(f"   Type: {type(value)}")
                print(f"   Length: {len(str(value))}")
                if isinstance(value, str):
                    if value.startswith('http'):
                        print(f"   Format: URL")
                        print(f"   Value: {value[:80]}...")
                    elif value.startswith('data:image'):
                        print(f"   Format: Data URI (base64)")
                        print(f"   Preview: {value[:50]}...")
                    else:
                        print(f"   Value: {value[:100]}...")
                found_qr = True
                print()
    
    if not found_qr:
        print("❌ NO QR CODE FIELD FOUND!")
        print("   PayOS might not include QR in payment_requests.create() response")
        print("   → User must open checkout_url to see QR on PayOS website")
    
    print("\n" + "="*80)
    print("🔗 CHECKOUT URL:")
    print("="*80 + "\n")
    
    checkout_fields = ['checkoutUrl', 'checkout_url', 'paymentUrl', 'payment_url', 'url']
    for field in checkout_fields:
        if hasattr(response, field):
            value = getattr(response, field)
            if value:
                print(f"✅ {field}: {value}")
                break
    
    print("\n" + "="*80)
    print("📊 RESPONSE AS DICT:")
    print("="*80 + "\n")
    
    # Try to convert to dict
    if hasattr(response, '__dict__'):
        import json
        try:
            response_dict = vars(response)
            print(json.dumps(response_dict, indent=2, default=str))
        except:
            print(response.__dict__)
    
    print("\n" + "="*80)
    print("💡 CONCLUSION:")
    print("="*80 + "\n")
    
    if found_qr:
        print("✅ PayOS DOES return QR code!")
        print("   → We can display QR directly on our page")
    else:
        print("❌ PayOS does NOT return QR code in API response")
        print("   → Solution: Open checkout_url in new window/redirect")
        print("   → User will see QR on PayOS payment page")
    
    print()

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("="*80 + "\n")

