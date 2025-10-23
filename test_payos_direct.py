#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PayOS API trực tiếp với thư viện payos v1.0.0
"""

import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
from payos import PayOS
from payos.types import ItemData, CreatePaymentLinkRequest

# Load credentials
client_id = os.environ.get('PAYOS_CLIENT_ID')
api_key = os.environ.get('PAYOS_API_KEY')
checksum_key = os.environ.get('PAYOS_CHECKSUM_KEY')

print("=" * 60)
print("TESTING PAYOS v1.0.0 PYTHON SDK")
print("=" * 60)

# Check credentials
print(f"\n📋 Credentials Check:")
print(f"   Client ID: {client_id[:10]}..." if client_id else "   Client ID: ❌ MISSING")
print(f"   API Key: {api_key[:10]}..." if api_key else "   API Key: ❌ MISSING")
print(f"   Checksum Key: {checksum_key[:10]}..." if checksum_key else "   Checksum Key: ❌ MISSING")

if not all([client_id, api_key, checksum_key]):
    print("\n❌ Missing PayOS credentials!")
    exit(1)

try:
    # Initialize PayOS
    print(f"\n🔧 Initializing PayOS client...")
    payos_client = PayOS(
        client_id=client_id,
        api_key=api_key,
        checksum_key=checksum_key
    )
    print("   ✅ PayOS client initialized")
    
    # Create test payment
    import time
    order_code = int(time.time() * 1000)
    
    print(f"\n💳 Creating payment link...")
    print(f"   Order Code: {order_code}")
    print(f"   Amount: 10,000 VND")
    
    # Create item (REQUIRED in PayOS v1.0.0)
    item = ItemData(
        name="Test License",  # Max 25 chars
        quantity=1,
        price=10000
    )
    
    # Create payment data
    payment_data = CreatePaymentLinkRequest(
        orderCode=order_code,
        amount=10000,
        description="Test payment",  # Max 25 chars
        items=[item],
        returnUrl="https://ocr-uufr.onrender.com/success",
        cancelUrl="https://ocr-uufr.onrender.com/cancel"
    )
    
    # Create payment link
    response = payos_client.payment_links.create(payment_data)
    
    print(f"\n✅ SUCCESS!")
    print(f"   Payment Link ID: {response.paymentLinkId}")
    print(f"   Checkout URL: {response.checkoutUrl}")
    print(f"   QR Code: {response.qrCode[:50]}...")
    print(f"   Status: {response.status}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ PayOS SDK Test PASSED!")
print("=" * 60)

